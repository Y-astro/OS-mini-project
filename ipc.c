#include "ipc.h"
#include "common.h"
#include <fcntl.h>
#include <semaphore.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <time.h>

#define WAIT_SECS 5

static void get_shm_name(char *buf, size_t sz) {
  snprintf(buf, sz, "/cc_shm_%ld", (long)getpid());
}

static void get_sem_ready_name(char *buf, size_t sz) {
  snprintf(buf, sz, "/cc_sem_ready_%ld", (long)getpid());
}

static void get_sem_done_name(char *buf, size_t sz) {
  snprintf(buf, sz, "/cc_sem_done_%ld", (long)getpid());
}

typedef struct {
  int job_id;
  int burst;
  char name[64];
  char response[128];
} Packet;

/* Only unlink objects this process actually created; never touch peers' names. */
static bool owns_shm, owns_ready, owns_done;
int ipc_cleanup(void) {
  char name[128];
  int rc = 0;
  get_shm_name(name, sizeof(name));
  if (owns_shm) {
    if (shm_unlink(name) == -1 && errno != ENOENT) {
      perror("shm_unlink"); rc = 1;
    } else owns_shm = false;
  }
  get_sem_ready_name(name, sizeof(name));
  if (owns_ready) {
    if (sem_unlink(name) == -1 && errno != ENOENT) {
      perror("sem_unlink ready"); rc = 1;
    } else owns_ready = false;
  }
  get_sem_done_name(name, sizeof(name));
  if (owns_done) {
    if (sem_unlink(name) == -1 && errno != ENOENT) {
      perror("sem_unlink done"); rc = 1;
    } else owns_done = false;
  }
  return rc;
}

int ipc_objects_remaining(void) {
  int n = 0;
  char name[128];

  get_shm_name(name, sizeof(name));
  int fd = shm_open(name, O_RDONLY, 0);
  if (fd != -1) {
    close(fd);
    n++;
  } else if (errno != ENOENT) return -1;

  get_sem_ready_name(name, sizeof(name));
  sem_t *s1 = sem_open(name, 0);
  if (s1 != SEM_FAILED) {
    sem_close(s1);
    n++;
  } else if (errno != ENOENT) return -1;

  get_sem_done_name(name, sizeof(name));
  sem_t *s2 = sem_open(name, 0);
  if (s2 != SEM_FAILED) {
    sem_close(s2);
    n++;
  } else if (errno != ENOENT) return -1;

  return n;
}

/* Wait with a timeout so a dead peer can never hang the demo. */
static int wait_sem(sem_t *s) {
  struct timespec ts;
  int r;
  if (clock_gettime(CLOCK_REALTIME, &ts) == -1) return -1;
  ts.tv_sec += WAIT_SECS;
  do {
    r = sem_timedwait(s, &ts);
  } while (r == -1 && errno == EINTR);
  return r;
}

static void child_main(Packet *pkt, sem_t *ready, sem_t *done) {
  /* Step 1: Wait until parent signals that job data is ready in shared memory
   */
  if (wait_sem(ready) == -1)
    child_exit(1);

  /* Step 2: Read job details from shared memory */
  printf("  [Child %d] read from shared memory: job %d '%s', burst %d\n",
         getpid(), pkt->job_id, pkt->name, pkt->burst);

  /* Step 3: Write response back into shared memory */
  snprintf(pkt->response, sizeof(pkt->response), "job %d executed by child %d",
           pkt->job_id, getpid());

  /* Step 4: Signal parent that computation and response are done */
  if (sem_post(done) == -1) child_exit(1);
  child_exit(0);
}

static int ipc_transfer(int job_id, int burst, const char *name) {
  int rc = 1, fd = -1, status = 0;
  pid_t pid;
  Packet *pkt = MAP_FAILED;
  sem_t *ready = SEM_FAILED, *done = SEM_FAILED;
  char shm_name[128], sem_ready_name[128], sem_done_name[128];

  get_shm_name(shm_name, sizeof(shm_name));
  get_sem_ready_name(sem_ready_name, sizeof(sem_ready_name));
  get_sem_done_name(sem_done_name, sizeof(sem_done_name));

  printf("\n=== Shared memory + named semaphore IPC ===\n");
  if (ipc_cleanup() != 0) return 1;

  /* Step 1: Create POSIX shared memory object under /dev/shm */
  fd = shm_open(shm_name, O_CREAT | O_EXCL | O_RDWR, 0600);
  if (fd == -1) {
    perror("shm_open");
    goto out;
  }

  owns_shm = true;

  /* Step 2: Set the size of the shared memory region */
  if (ftruncate(fd, sizeof(Packet)) == -1) {
    perror("ftruncate");
    goto out;
  }

  /* Step 3: Map the shared memory region into virtual address space */
  pkt = mmap(NULL, sizeof(Packet), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
  if (pkt == MAP_FAILED) {
    perror("mmap");
    goto out;
  }

  /* Step 4: Create POSIX named semaphores initialized to 0 */
  ready = sem_open(sem_ready_name, O_CREAT | O_EXCL, 0600, 0);
  if (ready == SEM_FAILED) { perror("sem_open ready"); goto out; }
  owns_ready = true;
  done = sem_open(sem_done_name, O_CREAT | O_EXCL, 0600, 0);
  if (done == SEM_FAILED) { perror("sem_open done"); goto out; }
  owns_done = true;
  printf("[Parent %d] created %s, %s, %s\n", getpid(), shm_name, sem_ready_name,
         sem_done_name);

  /* Step 5: Fork cooperating child process */
  pid = fork_flushed();
  if (pid < 0) {
    perror("fork");
    goto out;
  }
  if (pid == 0)
    child_main(pkt, ready, done);

  /* Step 6: Parent writes job data into shared memory and signals child */
  pkt->job_id = job_id;
  pkt->burst = burst;
  snprintf(pkt->name, sizeof(pkt->name), "%s", name);
  printf("[Parent %d] wrote job %d ('%s', burst %d) to shared memory, posting %s\n",
         getpid(), pkt->job_id, pkt->name, pkt->burst, sem_ready_name);
  bool replied = false;
  if (sem_post(ready) == -1) {
    perror("sem_post ready");
    kill(pid, SIGKILL);
  } else if (wait_sem(done) == -1) {
    perror("[Parent] waiting for child");
    kill(pid, SIGKILL);
  } else {
    replied = true;
    printf("[Parent %d] child replied via shared memory: \"%s\"\n", getpid(),
           pkt->response);
  }
  pid_t reaped;
  do { reaped = waitpid(pid, &status, 0); } while (reaped == -1 && errno == EINTR);
  if (reaped == -1) {
    perror("waitpid");
  } else if (WIFEXITED(status)) {
    printf("[Parent %d] child %d reaped, exit status %d\n", getpid(), pid,
           WEXITSTATUS(status));
    if (replied && WEXITSTATUS(status) == 0 && pkt->response[0]) rc = 0;
  } else if (WIFSIGNALED(status)) {
    printf("[Parent] child terminated by signal %d\n", WTERMSIG(status));
  }

out:
  /* Step 8: Clean up all mapped memory, file descriptors, and semaphores */
  if (pkt != MAP_FAILED && munmap(pkt, sizeof(Packet)) == -1) { perror("munmap"); rc = 1; }
  if (fd != -1 && close(fd) == -1) { perror("close"); rc = 1; }
  if (ready != SEM_FAILED && sem_close(ready) == -1) { perror("sem_close ready"); rc = 1; }
  if (done != SEM_FAILED && sem_close(done) == -1) { perror("sem_close done"); rc = 1; }
  if (ipc_cleanup() != 0) rc = 1;
  int left = ipc_objects_remaining();
  printf("[Cleanup] this process's IPC objects remaining: %d (-1 = check failed)\n", left);
  return (rc == 0 && left == 0) ? 0 : 1;
}

int ipc_demo(void) {
  return ipc_transfer(101, 5, "Fluid_Dynamics_Sim");
}

int ipc_custom(void) {
  int id = 101, burst = 5;
  char name[64];
  printf("\n=== Custom Shared Memory IPC Transfer ===\n");
  if (!read_int("Enter Job ID (1-9999): ", 1, 9999, &id))
    return 1;
  printf("Enter Job / Simulation Name: ");
  if (!fgets(name, sizeof(name), stdin))
    return 1;
  name[strcspn(name, "\r\n")] = '\0';
  if (name[0] == '\0')
    strcpy(name, "Custom_Lab_Job");
  if (!read_int("Enter CPU burst (1-100): ", 1, 100, &burst))
    return 1;
  return ipc_transfer(id, burst, name);
}

#include "worker.h"
#include "common.h"
#include <sys/wait.h>

#define SIMULATED_FAILURE_CODE 42

static int run_worker_with_code(bool simulate_failure, int failure_code) {
  int status;

  pid_t pid = fork_flushed();

  if (pid < 0) {
    perror("fork");
    return 1;
  }

  if (pid == 0) {
    printf("  [Worker %d] started\n", getpid());
    usleep(300000);

    if (simulate_failure) {

      printf("  [Worker %d] SIMULATED FAILURE (deliberate, not a real OS "
             "fault): exit(%d)\n",
             getpid(), failure_code);
      child_exit(failure_code);
    }

    printf("  [Worker %d] work finished, exit(0)\n", getpid());
    child_exit(0);
  }

  printf("[Coordinator %d] created worker %d, waiting with waitpid()\n",
         getpid(), pid);

  while (waitpid(pid, &status, 0) == -1) {
    if (errno != EINTR) {
      perror("waitpid");
      return 1;
    }
  }

  if (WIFSIGNALED(status)) {
    printf("[Coordinator] worker %d killed by signal %d (%s) -> FAILED\n", pid,
           WTERMSIG(status), strsignal(WTERMSIG(status)));
    return 1;
  }

  if (!WIFEXITED(status)) {
    fprintf(stderr, "[Coordinator] unexpected worker status\n");
    return 1;
  }
  int code = WEXITSTATUS(status);
  printf("[Coordinator] worker %d exited with status %d -> %s\n", pid, code,
         code == 0 ? "COMPLETED"
                   : "FAILED (detected from non-zero exit status)");

  return (code == (simulate_failure ? failure_code : 0)) ? 0 : 1;
}

int worker_demo_normal(void) {
  printf("\n=== Worker process: normal completion ===\n");
  return run_worker_with_code(false, 0);
}

int worker_demo_failure(void) {
  printf("\n=== Worker process: simulated failure ===\n");
  return run_worker_with_code(true, SIMULATED_FAILURE_CODE);
}

int worker_custom(void) {
  int code = 0;
  printf("\n=== Custom Worker Process Simulation ===\n");
  if (!read_int("Enter simulated worker exit status (0 = success, 1-255 = "
                "simulated failure): ",
                0, 255, &code))
    return 1;
  return run_worker_with_code(code != 0, code);
}

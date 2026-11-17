#include "common.h"
#include "worker.h"
#include <sys/wait.h>

#define SIMULATED_FAILURE_CODE 42

static int run_worker(bool simulate_failure) {
    int status;

    /* Step 1: Flush stdio buffers and fork a child process */
    pid_t pid = fork_flushed();

    if (pid < 0) {
        perror("fork");
        return 1;
    }

    /* Child Process Execution */
    if (pid == 0) {
        printf("  [Worker %d] started\n", getpid());
        usleep(300000); /* Simulate task execution */

        if (simulate_failure) {
            /* Simulated abnormal termination: exits with code 42 */
            printf("  [Worker %d] SIMULATED FAILURE (deliberate, not a real OS fault): exit(%d)\n",
                   getpid(), SIMULATED_FAILURE_CODE);
            child_exit(SIMULATED_FAILURE_CODE);
        }

        /* Normal successful completion: exits with code 0 */
        printf("  [Worker %d] work finished, exit(0)\n", getpid());
        child_exit(0);
    }

    /* Parent Process Execution */
    printf("[Coordinator %d] created worker %d, waiting with waitpid()\n", getpid(), pid);

    /* Step 2: Parent waits for child state change */
    while (waitpid(pid, &status, 0) == -1) {
        if (errno != EINTR) {
            perror("waitpid");
            return 1;
        }
    }

    /* Step 3: Inspect child termination status using POSIX macros */
    if (WIFSIGNALED(status)) {
        printf("[Coordinator] worker %d killed by signal %d (%s) -> FAILED\n",
               pid, WTERMSIG(status), strsignal(WTERMSIG(status)));
        return 1;
    }

    int code = WEXITSTATUS(status);
    printf("[Coordinator] worker %d exited with status %d -> %s\n", pid, code,
           code == 0 ? "COMPLETED" : "FAILED (detected from non-zero exit status)");

    return (code == (simulate_failure ? SIMULATED_FAILURE_CODE : 0)) ? 0 : 1;
}

int worker_demo_normal(void) {
    printf("\n=== Worker process: normal completion ===\n");
    return run_worker(false);
}

int worker_demo_failure(void) {
    printf("\n=== Worker process: simulated failure ===\n");
    return run_worker(true);
}

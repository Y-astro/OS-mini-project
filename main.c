#include "common.h"
#include "scheduler.h"
#include "logger.h"
#include "ipc.h"
#include "banker.h"
#include "worker.h"
#include "rlimit.h"
#include <sys/wait.h>

static Job jobs[MAX_JOBS];
static int num_jobs;

typedef struct {
    const char *flag;               /* command-line form: ./campuscompute --<flag> */
    const char *label;
    int (*run)(void);               /* 0 = success */
    bool in_demo;                   /* included in the integrated demonstration */
} Command;

static int cmd_input(void)      { return scheduler_input_jobs(jobs, &num_jobs); }
static int cmd_default(void)    {
    scheduler_load_default_jobs(jobs, &num_jobs);
    printf("Loaded %d default jobs.\n", num_jobs);
    return 0;
}
static int cmd_show(void)       { scheduler_display_jobs(jobs, num_jobs); return 0; }
static int cmd_fcfs(void)       { return scheduler_run_fcfs(jobs, num_jobs); }
static int cmd_rr(void)         { return scheduler_run_rr(jobs, num_jobs); }
static int cmd_priority(void)   { return scheduler_run_priority(jobs, num_jobs); }
static int cmd_compare(void)    { return scheduler_compare_all(jobs, num_jobs); }
static int cmd_demo(void);
static int cmd_cleanup(void);

static const Command commands[] = {
    { "input",         "Input custom jobs",                      cmd_input,            false },
    { "default",       "Load default workload (5 jobs)",         cmd_default,          false },
    { "show",          "Display current jobs",                   cmd_show,             true  },
    { "fcfs",          "FCFS scheduling",                        cmd_fcfs,             true  },
    { "rr",            "Round Robin scheduling",                 cmd_rr,               true  },
    { "priority",      "Priority scheduling (non-preemptive)",   cmd_priority,         true  },
    { "compare",       "Compare all scheduling policies",        cmd_compare,          true  },
    { "logger",        "Producer-consumer logger (pthreads)",    logger_demo,          true  },
    { "ipc",           "Shared memory + semaphore IPC",          ipc_demo,             true  },
    { "banker-safe",   "Banker's algorithm: safe state",         banker_demo_safe,     true  },
    { "banker-unsafe", "Banker's algorithm: unsafe state",       banker_demo_unsafe,   true  },
    { "banker-input",  "Banker's algorithm: enter your own state", banker_input_and_check, false },
    { "worker-ok",     "Worker process: normal completion",      worker_demo_normal,   true  },
    { "worker-fail",   "Worker process: simulated failure",      worker_demo_failure,  true  },
    { "rlimit",        "Resource limit demo (RLIMIT_CPU)",       rlimit_demo_cpu,      true  },
    { "demo",          "Integrated demonstration",               cmd_demo,             false },
    { "cleanup",       "Verify cleanup of threads/IPC/processes", cmd_cleanup,         false },
};
#define NUM_COMMANDS ((int)(sizeof(commands) / sizeof(commands[0])))

static int cmd_cleanup(void) {
    logger_shutdown();
    ipc_cleanup();

    int reaped = 0;
    while (waitpid(-1, NULL, WNOHANG) > 0) reaped++;
    bool no_children = (waitpid(-1, NULL, WNOHANG) == -1 && errno == ECHILD);
    int left = ipc_objects_remaining();

    printf("\n=== Cleanup verification ===\n");
    printf("Logger thread: stopped and joined, log file closed\n");
    printf("Child processes: %d stray reaped, none remaining: %s\n", reaped, no_children ? "yes" : "NO");
    printf("IPC objects (shared memory + semaphores) remaining: %d\n", left);
    return (no_children && left == 0) ? 0 : 1;
}

static int cmd_demo(void) {
    int result[NUM_COMMANDS];
    int failures = 0;

    printf("\n=== Integrated demonstration ===\n");
    for (int i = 0; i < NUM_COMMANDS; i++) {
        if (commands[i].in_demo) result[i] = commands[i].run();
    }
    int cleanup_result = cmd_cleanup();

    printf("\n=== Summary ===\n");
    for (int i = 0; i < NUM_COMMANDS; i++) {
        if (!commands[i].in_demo) continue;
        printf("  %-14s %s\n", commands[i].flag, result[i] == 0 ? "PASS" : "FAIL");
        failures += result[i] != 0;
    }
    printf("  %-14s %s\n", "cleanup", cleanup_result == 0 ? "PASS" : "FAIL");
    failures += cleanup_result != 0;
    printf("%d check(s) failed.\n", failures);
    return failures != 0;
}

static void print_banner(void) {
    printf("\nCampusCompute - Job Scheduling and Resource Management | %s\n", SRN);
}

static void print_menu(void) {
    printf("\nCommands (type the number at the prompt, or run ./campuscompute --<flag>):\n");
    for (int i = 0; i < NUM_COMMANDS; i++) {
        printf("  %2d  %-42s --%s\n", i + 1, commands[i].label, commands[i].flag);
    }
    printf("   0  Clean up and exit\n   ?  Show this menu\n");
}

static void run_interactive(void) {
    char line[128];

    print_banner();
    print_menu();
    while (1) {
        printf("\nCampusCompute [%s] >> ", SRN);
        if (!fgets(line, sizeof(line), stdin)) break;
        line[strcspn(line, "\r\n")] = '\0';
        if (line[0] == '\0') continue;
        if (strcmp(line, "?") == 0 || strcmp(line, "help") == 0) {
            print_menu();
            continue;
        }

        char *end;
        long choice = strtol(line, &end, 10);
        if (*end != '\0' || choice < 0 || choice > NUM_COMMANDS) {
            printf("[Error] Invalid command \"%s\". Enter a number 0-%d or '?' for the menu.\n", line, NUM_COMMANDS);
            continue;
        }
        if (choice == 0) break;
        commands[choice - 1].run();
    }
    cmd_cleanup();
    printf("Goodbye.\n");
}

int main(int argc, char *argv[]) {
    num_jobs = 0;
    scheduler_load_default_jobs(jobs, &num_jobs);

    if (argc == 1) {
        run_interactive();
        return 0;
    }
    if (argc == 2 && (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0)) {
        print_banner();
        print_menu();
        return 0;
    }
    if (argc == 2 && strncmp(argv[1], "--", 2) == 0) {
        for (int i = 0; i < NUM_COMMANDS; i++) {
            if (strcmp(argv[1] + 2, commands[i].flag) == 0) return commands[i].run();
        }
    }
    fprintf(stderr, "[Error] Unknown option or arguments: '%s'\n", argc > 1 ? argv[1] : "");
    fprintf(stderr, "Usage: %s [--help | --<command>]   (see --help for the command list)\n", argv[0]);
    return 1;
}

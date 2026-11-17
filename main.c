#include "banker.h"
#include "common.h"
#include "ipc.h"
#include "logger.h"
#include "rlimit.h"
#include "scheduler.h"
#include "worker.h"
#include <sys/wait.h>
#include <limits.h>
#include <ctype.h>

static Job jobs[MAX_JOBS];
static int num_jobs;
static const char *cli_arg; /* argument following a flag, e.g. --jobs FILE */

/* Uses the CLI argument if given, otherwise prompts for it. */
static const char *get_arg(const char *prompt, char *buf, size_t n) {
  if (cli_arg)
    return cli_arg;
  printf("%s", prompt);
  if (!fgets(buf, (int)n, stdin))
    return NULL;
  buf[strcspn(buf, "\r\n")] = '\0';
  return buf[0] ? buf : NULL;
}

typedef struct {
  const char *flag; /* command-line form: ./campuscompute --<flag> */
  const char *label;
  int (*run)(void); /* 0 = success */
  bool in_demo;     /* included in the integrated demonstration */
} Command;

static int cmd_input(void) { return scheduler_input_jobs(jobs, &num_jobs); }
static int cmd_default(void) {
  scheduler_load_default_jobs(jobs, &num_jobs);
  printf("Loaded %d default jobs.\n", num_jobs);
  return 0;
}
static int cmd_jobs_file(void) {
  char buf[256];
  const char *p = get_arg("Path to jobs file: ", buf, sizeof(buf));
  return p ? scheduler_load_file(jobs, &num_jobs, p) : 1;
}
static int cmd_random(void) {
  char buf[64];
  const char *p = get_arg("Number of random jobs (1-20): ", buf, sizeof(buf));
  if (!p)
    return 1;
  int count;
  if (!parse_int(p, 1, MAX_JOBS, &count)) {
    fprintf(stderr, "[Error] Job count must be an integer between 1 and %d\n", MAX_JOBS);
    return 1;
  }
  unsigned seed = 0;
  const char *seed_text = getenv("SEED");
  if (seed_text) {
    char *end;
    errno = 0;
    unsigned long value = strtoul(seed_text, &end, 10);
    if (!isdigit((unsigned char)seed_text[0]) || *end || errno || value > UINT_MAX || value == 0) {
      fprintf(stderr, "[Error] SEED must be a positive unsigned integer\n");
      return 1;
    }
    seed = (unsigned)value;
  }
  int r = scheduler_generate_random(jobs, &num_jobs, count, seed);
  if (r == 0)
    scheduler_display_jobs(jobs, num_jobs);
  return r;
}
static int cmd_banker_file(void) {
  char buf[256];
  const char *p = get_arg("Path to Banker state file: ", buf, sizeof(buf));
  return p ? banker_from_file(p) : 1;
}
static int cmd_add(void) { return scheduler_add_job(jobs, &num_jobs); }
static int cmd_edit_pri(void) {
  return scheduler_edit_job_priority(jobs, num_jobs);
}
static int cmd_quantum(void) { return scheduler_input_quantum(); }
static int cmd_show(void) {
  scheduler_display_jobs(jobs, num_jobs);
  return 0;
}
static int cmd_fcfs(void) { return scheduler_run_fcfs(jobs, num_jobs); }
static int cmd_rr(void) { return scheduler_run_rr(jobs, num_jobs); }
static int cmd_priority(void) { return scheduler_run_priority(jobs, num_jobs); }
static int cmd_compare(void) { return scheduler_compare_all(jobs, num_jobs); }
static int cmd_trace(void) {
  scheduler_set_trace(!scheduler_get_trace());
  printf("Scheduling trace: %s\n", scheduler_get_trace() ? "ON" : "OFF");
  return 0;
}
static int cmd_log_schedule(void) {
  scheduler_set_logging(!scheduler_get_logging());
  printf("Scheduling event logger: %s\n", scheduler_get_logging() ? "ON" : "OFF");
  return 0;
}
static int cmd_dashboard(void) {
  int total = 0, completed = 0;
  for (int i = 0; i < num_jobs; i++) {
    total += jobs[i].burst;
    completed += strcmp(jobs[i].status, "COMPLETED") == 0;
  }
  printf("\n=== CampusCompute | Workload Dashboard ===\n");
  printf("Jobs: %d/%d  |  Last simulated state: %d completed  |  Total CPU demand: %d\n",
         num_jobs, MAX_JOBS, completed, total);
  printf("RR quantum: %d  |  Trace: %s  |  Scheduler logging: %s\n",
         scheduler_get_quantum(), scheduler_get_trace() ? "ON" : "OFF",
         scheduler_get_logging() ? "ON" : "OFF");
  scheduler_display_jobs(jobs, num_jobs);
  return scheduler_compare_all(jobs, num_jobs);
}
static int cmd_demo(void);
static int cmd_cleanup(void);

static const Command commands[] = {
    {"input", "Input custom jobs (replace current list)", cmd_input, false},
    {"jobs", "Load jobs from a file (arrival burst priority)", cmd_jobs_file,
     false},
    {"random", "Generate random jobs (env SEED=n to reproduce)", cmd_random,
     false},
    {"default", "Load default workload (5 jobs)", cmd_default, false},
    {"add-job", "Add a new job to current workload", cmd_add, false},
    {"edit-priority", "Change an existing job's priority", cmd_edit_pri, false},
    {"set-quantum", "Set Round Robin time quantum", cmd_quantum, false},
    {"show", "Display current jobs", cmd_show, true},
    {"fcfs", "FCFS scheduling", cmd_fcfs, true},
    {"rr", "Round Robin scheduling", cmd_rr, true},
    {"priority", "Priority scheduling (non-preemptive)", cmd_priority, true},
    {"compare", "Compare all scheduling policies", cmd_compare, true},
    {"logger", "Producer-consumer logger (default benchmark)", logger_demo,
     true},
    {"logger-custom", "Producer-consumer logger (custom threads)",
     logger_custom_run, false},
    {"logger-msg", "Logger: submit custom message to queue",
     logger_submit_event, false},
    {"ipc", "Shared memory + semaphore IPC (benchmark)", ipc_demo, true},
    {"ipc-custom", "Shared memory IPC: send custom job packet", ipc_custom,
     false},
    {"banker-safe", "Banker's algorithm: safe state", banker_demo_safe, true},
    {"banker-unsafe", "Banker's algorithm: unsafe state", banker_demo_unsafe,
     true},
    {"banker-file", "Banker's algorithm: load state from file",
     cmd_banker_file, false},
    {"banker-input", "Banker's algorithm: enter your own state",
     banker_input_and_check, false},
    {"worker-ok", "Worker process: normal completion", worker_demo_normal,
     true},
    {"worker-fail", "Worker process: simulated failure", worker_demo_failure,
     true},
    {"worker-custom", "Worker process: custom simulated exit code",
     worker_custom, false},
    {"rlimit", "Resource limit demo (RLIMIT_CPU)", rlimit_demo_cpu, true},
    {"demo", "Integrated demonstration", cmd_demo, false},
    {"cleanup", "Verify cleanup of threads/IPC/processes", cmd_cleanup, false},
    {"trace", "Toggle step-by-step scheduling trace", cmd_trace, false},
    {"log-schedule", "Toggle actual scheduling event logger", cmd_log_schedule, false},
    {"dashboard", "Workload dashboard and policy comparison", cmd_dashboard, false},
};
#define NUM_COMMANDS ((int)(sizeof(commands) / sizeof(commands[0])))

static int cmd_cleanup(void) {
  int log_result = logger_shutdown();
  int cleanup_result = ipc_cleanup();

  int reaped = 0;
  pid_t child;
  do {
    child = waitpid(-1, NULL, WNOHANG);
    if (child > 0)
      reaped++;
  } while (child > 0 || (child == -1 && errno == EINTR));
  bool no_children = child == -1 && errno == ECHILD;
  int left = ipc_objects_remaining();

  printf("\n=== Cleanup verification ===\n");
  printf("Logger: %s\n", log_result >= 0 ? "inactive (previous consumer joined)" : "shutdown/write error");
  printf("Child processes: %d stray reaped, none remaining: %s\n", reaped,
         no_children ? "yes" : "NO");
  printf("IPC objects (shared memory + semaphores) remaining: %d\n", left);
  return (no_children && left == 0 && log_result >= 0 && cleanup_result == 0) ? 0 : 1;
}

static int cmd_demo(void) {
  int result[NUM_COMMANDS];
  int failures = 0;

  printf("\n=== Integrated demonstration ===\n");
  for (int i = 0; i < NUM_COMMANDS; i++) {
    if (commands[i].in_demo)
      result[i] = commands[i].run();
  }
  int cleanup_result = cmd_cleanup();

  printf("\n=== Summary ===\n");
  for (int i = 0; i < NUM_COMMANDS; i++) {
    if (!commands[i].in_demo)
      continue;
    printf("  %-14s %s\n", commands[i].flag, result[i] == 0 ? "PASS" : "FAIL");
    failures += result[i] != 0;
  }
  printf("  %-14s %s\n", "cleanup", cleanup_result == 0 ? "PASS" : "FAIL");
  failures += cleanup_result != 0;
  printf("%d check(s) failed.\n", failures);
  return failures != 0;
}

static void print_banner(void) {
  bool color = isatty(STDOUT_FILENO) && !getenv("NO_COLOR");
  printf("\n%sCampusCompute%s | Job Scheduling & Resource Management | %s\n",
         color ? "\033[1;36m" : "", color ? "\033[0m" : "", get_srn());
}

static void print_menu(void) {
  printf("\nCommands (type the number at the prompt, or run ./campuscompute "
         "--<flag>):\n");
  for (int i = 0; i < NUM_COMMANDS; i++) {
    printf("  %2d  %-42s --%s\n", i + 1, commands[i].label, commands[i].flag);
  }
  printf("   0  Clean up and exit\n   ?  Show this menu\n");
  printf("Chain commands in a single invocation, e.g. --trace --jobs FILE --rr 3\n");
}

static int run_interactive(void) {
  char line[128];

  print_banner();
  print_menu();
  while (1) {
    printf("\nCampusCompute [%s] >> ", get_srn());
    if (!fgets(line, sizeof(line), stdin))
      break;
    if (!strchr(line, '\n') && !feof(stdin)) {
      int c;
      while ((c = getchar()) != '\n' && c != EOF) {}
      printf("[Error] Command too long.\n");
      continue;
    }
    line[strcspn(line, "\r\n")] = '\0';
    if (line[0] == '\0')
      continue;
    if (strcmp(line, "?") == 0 || strcmp(line, "help") == 0) {
      print_menu();
      continue;
    }

    int choice;
    if (!parse_int(line, 0, NUM_COMMANDS, &choice)) {
      printf("[Error] Invalid command \"%s\". Enter a number 0-%d or '?' for "
             "the menu.\n",
             line, NUM_COMMANDS);
      continue;
    }
    if (choice == 0)
      break;
    if (commands[choice - 1].run() != 0)
      printf("[Error] Command did not complete successfully.\n");
  }
  int rc = cmd_cleanup();
  printf("Goodbye.\n");
  return rc;
}

int main(int argc, char *argv[]) {
  scheduler_load_default_jobs(jobs, &num_jobs);
  if (argc == 1)
    return run_interactive();
  if (argc == 2 && (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0)) {
    print_banner();
    print_menu();
    return 0;
  }

  /* One process owns the workload and settings for the entire command chain. */
  for (int i = 1; i < argc; i++) {
    const char *arg = argv[i];
    if (strncmp(arg, "--", 2) != 0) {
      fprintf(stderr, "[Error] Unexpected argument: %s\n", arg);
      return 1;
    }
    const char *name = arg + 2;
    if (strcmp(name, "quantum") == 0)
      name = "set-quantum";
    int k;
    for (k = 0; k < NUM_COMMANDS; k++)
      if (strcmp(name, commands[k].flag) == 0)
        break;
    if (k == NUM_COMMANDS) {
      fprintf(stderr, "[Error] Unknown command: %s (see --help)\n", arg);
      return 1;
    }

    bool takes_arg = strcmp(name, "jobs") == 0 ||
                     strcmp(name, "random") == 0 ||
                     strcmp(name, "banker-file") == 0;
    bool quantum = strcmp(name, "rr") == 0 || strcmp(name, "set-quantum") == 0;
    cli_arg = NULL;
    if (takes_arg) {
      if (i + 1 >= argc || strncmp(argv[i + 1], "--", 2) == 0) {
        fprintf(stderr, "[Error] --%s needs an argument\n", name);
        return 1;
      }
      cli_arg = argv[++i];
    }
    if (quantum && i + 1 < argc && strncmp(argv[i + 1], "--", 2) != 0) {
      int q;
      if (!parse_int(argv[++i], 1, 100, &q)) {
        fprintf(stderr, "[Error] Quantum must be an integer from 1 to 100\n");
        return 1;
      }
      scheduler_set_quantum(q);
      if (strcmp(name, "set-quantum") == 0) {
        printf("Round Robin time quantum set to %d.\n", q);
        continue;
      }
    }
    int rc = commands[k].run();
    cli_arg = NULL;
    if (rc != 0)
      return rc;
  }
  return 0;
}

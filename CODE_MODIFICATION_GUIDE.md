# CampusCompute — Source Code Modification & Live Coding Guide

> **Purpose**: This guide provides the exact file paths, line numbers, C code snippets, and terminal commands required if your faculty (Dr. Gokulakrishnan S) asks you to **modify the source code on the spot** during the Level 3 demonstration and viva voce.

---

## Quick Reference: Faculty Request Matrix

| Faculty Asks You To... | Target File | Function / Macro | Lines | Recompile & Verify Command |
|---|---|---|:---:|---|
| **Add/change default jobs in C code** | `scheduler.c` | `scheduler_load_default_jobs()` | 63–70 | `make && ./campuscompute --fcfs` |
| **Make higher number = higher priority** | `scheduler.c` | `better()` | 286–292 | `make && ./campuscompute --priority` |
| **Change tie-breaking rule (e.g. SJF tie-break)** | `scheduler.c` | `better()` | 286–292 | `make && ./campuscompute --priority` |
| **Change default Round Robin quantum in C** | `common.h` | `TIME_QUANTUM` | 16 | `make && ./campuscompute --rr` |
| **Change queue admission order in RR** | `scheduler.c` | `simulate_rr()` | 424–432 | `make && ./campuscompute --trace --rr 2` |
| **Make logger queue fill up faster (smaller buffer)** | `common.h` | `LOG_QUEUE_SIZE` | 19 | `make && ./campuscompute --logger` |
| **Change consumer speed (make it faster/slower)** | `logger.c` | `consume()` | 85 | `make && ./campuscompute --logger` |
| **Change number of producer threads/events** | `logger.c` | `logger_demo()` | 187–189 | `make && ./campuscompute --logger` |
| **Add a custom field to shared memory packet** | `ipc.c` | `typedef struct Packet` | 24–29 | `make && ./campuscompute --ipc` |
| **Change semaphore timeout duration** | `ipc.c` | `WAIT_SECS` | 10 | `make && ./campuscompute --ipc` |
| **Change Banker's default Safe/Unsafe state** | `banker.c` | `SAFE_STATE` / `UNSAFE_STATE` | 13–27 | `make && ./campuscompute --banker-safe` |
| **Change simulated worker failure exit code** | `worker.c` | `SIMULATED_FAILURE_CODE` | 5 | `make && ./campuscompute --worker-fail` |
| **Simulate a real process crash (SIGSEGV/abort)** | `worker.c` | `run_worker_with_code()` | 25–29 | `make && ./campuscompute --worker-fail` |
| **Change kernel CPU limit (soft/hard seconds)** | `rlimit.c` | `rlimit_demo_cpu()` | 9 | `make && ./campuscompute --rlimit` |

---

## 1. CPU Scheduling Modifications (`scheduler.c` & `common.h`)

### Mod 1.1: Add or Change Default Jobs in Source Code
- **File**: `scheduler.c`
- **Function**: `scheduler_load_default_jobs(Job jobs[], int *n)` (Lines 63–70)

#### Before:
```c
void scheduler_load_default_jobs(Job jobs[], int *n) {
  static const int data[5][4] = {
      {1, 0, 5, 2}, {2, 1, 3, 1}, {3, 2, 8, 4}, {4, 3, 6, 2}, {5, 4, 4, 2}};
  for (int i = 0; i < 5; i++) {
    jobs[i] = (Job){data[i][0], data[i][1], data[i][2], data[i][3], "READY"};
  }
  *n = 5;
}
```

#### If faculty asks: *"Add Job 6 (arrival 6, burst 5, priority 1) directly in code"*:
```c
void scheduler_load_default_jobs(Job jobs[], int *n) {
  static const int data[6][4] = {
      {1, 0, 5, 2}, {2, 1, 3, 1}, {3, 2, 8, 4}, {4, 3, 6, 2}, {5, 4, 4, 2},
      {6, 6, 5, 1}}; /* Added Job 6 */
  for (int i = 0; i < 6; i++) {
    jobs[i] = (Job){data[i][0], data[i][1], data[i][2], data[i][3], "READY"};
  }
  *n = 6;
}
```

**Rebuild & Test**:
```bash
make clean && make
./campuscompute --show
./campuscompute --fcfs
```

---

### Mod 1.2: Invert Priority Direction (Higher Number = Higher Priority)
- **File**: `scheduler.c`
- **Function**: `better(const Job *a, const Job *b, Policy p)` (Lines 286–292)

By default, UNIX convention is used: **lower number = higher priority** (`a->priority < b->priority`).

#### If faculty asks: *"Change priority scheduling so that a higher number means higher priority"*:
Change `<` to `>` on line 288:

```c
/* Before (lower number = higher priority): */
static bool better(const Job *a, const Job *b, Policy p) {
  if (p == PRIORITY && a->priority != b->priority)
    return a->priority < b->priority;
  if (a->arrival != b->arrival)
    return a->arrival < b->arrival;
  return a->id < b->id;
}

/* After (higher number = higher priority): */
static bool better(const Job *a, const Job *b, Policy p) {
  if (p == PRIORITY && a->priority != b->priority)
    return a->priority > b->priority; /* INVERTED */
  if (a->arrival != b->arrival)
    return a->arrival < b->arrival;
  return a->id < b->id;
}
```

**Effect on Output**: Job 3 (priority 4) will now execute before Job 1 and 2 (priority 2 and 1).  
**Rebuild & Test**:
```bash
make clean && make
./campuscompute --priority
```

---

### Mod 1.3: Change Priority Tie-Breaking Rule (e.g., Shortest Job First)
- **File**: `scheduler.c`
- **Function**: `better()` (Lines 286–292)

By default, equal priorities break ties by: **earlier arrival**, then **lower Job ID**.

#### If faculty asks: *"If priorities are equal, pick the job with the shorter burst time (SJF tie-break)"*:
```c
static bool better(const Job *a, const Job *b, Policy p) {
  if (p == PRIORITY && a->priority != b->priority)
    return a->priority < b->priority;
  /* Custom tie-break: smaller burst first */
  if (a->burst != b->burst)
    return a->burst < b->burst;
  if (a->arrival != b->arrival)
    return a->arrival < b->arrival;
  return a->id < b->id;
}
```

**Rebuild & Test**:
```bash
make clean && make
./campuscompute --priority
```

---

### Mod 1.4: Change Default Round Robin Quantum in Source Code
- **File**: `common.h` (Line 16)

```c
/* Before: */
#define TIME_QUANTUM 2

/* After (e.g. quantum = 4): */
#define TIME_QUANTUM 4
```

**Rebuild & Test**:
```bash
make clean && make
./campuscompute --rr
```
*Observe that the execution timeline slices drop from 14 to 8 slices.*

---

## 2. Multithreaded Activity Logger Modifications (`logger.c` & `common.h`)

### Mod 2.1: Change Bounded Buffer Capacity
- **File**: `common.h` (Line 19)

```c
/* Before (queue holds up to 8 log events): */
#define LOG_QUEUE_SIZE 8

/* After (e.g. smaller queue of size 3 to force immediate producer blocking): */
#define LOG_QUEUE_SIZE 3
```

**Effect on Output**: Producers will block almost immediately, displaying:
`[Producer] queue full (3/3), waiting for consumer` much more frequently.  
**Rebuild & Test**:
```bash
make clean && make
./campuscompute --logger
```

---

### Mod 2.2: Make Consumer Faster or Slower
- **File**: `logger.c`
- **Function**: `consume()` (Line 85)

```c
/* Before (slow consumer sleeps 20ms to allow buffer to fill): */
usleep(20000);

/* After (fast consumer: 0 delay, queue rarely fills): */
usleep(0);

/* Or ultra-slow consumer (100ms delay, queue constantly stays full): */
usleep(100000);
```

**Rebuild & Test**:
```bash
make clean && make
./campuscompute --logger
```

---

### Mod 2.3: Change Default Producer Count and Events per Producer
- **File**: `logger.c`
- **Function**: `logger_demo(void)` (Lines 187–189)

```c
/* Before (3 producers, 5 events each = 15 events): */
int logger_demo(void) {
  return run_producer_consumer(3, 5);
}

/* After (5 producers, 10 events each = 50 events): */
int logger_demo(void) {
  return run_producer_consumer(5, 10);
}
```

**Rebuild & Test**:
```bash
make clean && make
./campuscompute --logger
# Check line count in log file:
wc -l campuscompute.log
```

---

## 3. Inter-Process Communication Modifications (`ipc.c`)

### Mod 3.1: Add a Custom Field to Shared Memory Packet
- **File**: `ipc.c`
- **Struct**: `Packet` (Lines 24–29) and `child_main()` (Lines 97–114)

#### Step 1: Update `Packet` struct in `ipc.c` (Line 24):
```c
typedef struct {
  int job_id;
  int burst;
  char name[64];
  char response[128];
  char student_srn[32]; /* NEW FIELD */
} Packet;
```

#### Step 2: Parent populates field in `ipc_transfer()` (Line 175):
```c
pkt->job_id = job_id;
pkt->burst = burst;
snprintf(pkt->name, sizeof(pkt->name), "%s", name);
snprintf(pkt->student_srn, sizeof(pkt->student_srn), "%s", get_srn()); /* NEW */
```

#### Step 3: Child reads and prints field in `child_main()` (Line 104):
```c
printf("  [Child %d] read from shared memory: job %d '%s', SRN '%s'\n",
       getpid(), pkt->job_id, pkt->name, pkt->student_srn);
```

**Rebuild & Test**:
```bash
make clean && make
./campuscompute --ipc
```

---

### Mod 3.2: Change Semaphore Timeout Value
- **File**: `ipc.c` (Line 10)

```c
/* Before: 5 second timeout */
#define WAIT_SECS 5

/* After: 10 second timeout */
#define WAIT_SECS 10
```

---

## 4. Banker's Algorithm Modifications (`banker.c`)

### Mod 4.1: Modify Available Vector to Turn Unsafe State into Safe
- **File**: `banker.c`
- **Struct**: `UNSAFE_STATE` (Lines 21–27)

#### Before (UNSAFE because Available is `[0, 1, 0]`):
```c
static const State UNSAFE_STATE = {
    .p = 4,
    .r = 3,
    .alloc = {{3, 1, 2}, {2, 2, 1}, {2, 1, 1}, {1, 1, 1}},
    .max = {{5, 4, 3}, {4, 4, 3}, {6, 3, 3}, {3, 3, 2}},
    .avail = {0, 1, 0},
};
```

#### After (Change `.avail = {2, 2, 2}` to make it SAFE):
```c
static const State UNSAFE_STATE = {
    .p = 4,
    .r = 3,
    .alloc = {{3, 1, 2}, {2, 2, 1}, {2, 1, 1}, {1, 1, 1}},
    .max = {{5, 4, 3}, {4, 4, 3}, {6, 3, 3}, {3, 3, 2}},
    .avail = {2, 2, 2}, /* NOW SAFE */
};
```

**Rebuild & Test**:
```bash
make clean && make
./campuscompute --banker-unsafe
```
*Output will now show `RESULT: SAFE state` with a calculated safe sequence.*

---

## 5. Worker Failure Detection Modifications (`worker.c`)

### Mod 5.1: Change Simulated Failure Exit Code
- **File**: `worker.c` (Line 5)

```c
/* Before: */
#define SIMULATED_FAILURE_CODE 42

/* After (e.g. exit code 99 or 137): */
#define SIMULATED_FAILURE_CODE 99
```

**Rebuild & Test**:
```bash
make clean && make
./campuscompute --worker-fail
```
*Parent will output: `worker exited with status 99 -> FAILED`.*

---

### Mod 5.2: Simulate an Abnormal Termination (Crash by Signal)
- **File**: `worker.c`
- **Function**: `run_worker_with_code()` (Lines 23–29)

By default, the worker exits cleanly via `child_exit(failure_code)`.

#### If faculty asks: *"Simulate a crash where the process is killed by a signal (e.g. SIGSEGV or abort)"*:
```c
    if (simulate_failure) {
      printf("  [Worker %d] Triggering segmentation fault...\n", getpid());
      fflush(stdout);
      /* Dereference a NULL pointer to cause SIGSEGV */
      int *bad_ptr = NULL;
      *bad_ptr = 42;
      child_exit(1);
    }
```

**Effect on Output**: The parent's `WIFSIGNALED(status)` branch triggers:
`[Coordinator] worker killed by signal 11 (Segmentation fault) -> FAILED`.  
**Rebuild & Test**:
```bash
make clean && make
./campuscompute --worker-fail
```

---

## 6. Resource Limits Modifications (`rlimit.c`)

### Mod 6.1: Change CPU Soft & Hard Limit Duration
- **File**: `rlimit.c`
- **Function**: `rlimit_demo_cpu()` (Line 9)

```c
/* Before: soft=1s, hard=2s */
struct rlimit limit = {.rlim_cur = 1, .rlim_max = 2};

/* After: soft=2s, hard=3s */
struct rlimit limit = {.rlim_cur = 2, .rlim_max = 3};
```

**Effect on Output**: The child process spins for 2 full seconds of CPU execution before the kernel sends `SIGXCPU`.  
**Rebuild & Test**:
```bash
make clean && make
./campuscompute --rlimit
```

---

## 7. Fast Rebuild & Verification Protocol (3 Steps)

Whenever you edit any `.c` or `.h` file during the viva:

1. **Recompile**:
   ```bash
   make clean && make
   ```
2. **Run the relevant command**:
   - Scheduling: `./campuscompute --fcfs` or `--rr 2` or `--priority`
   - Logger: `./campuscompute --logger`
   - IPC: `./campuscompute --ipc`
   - Banker: `./campuscompute --banker-safe` or `--banker-unsafe`
   - Worker: `./campuscompute --worker-fail`
   - Limits: `./campuscompute --rlimit`
3. **Verify automated tests still pass**:
   ```bash
   make test
   ```

*(To discard temporary live edits and restore git state: `git restore .`)*

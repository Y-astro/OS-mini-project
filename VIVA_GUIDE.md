# CampusCompute — Comprehensive Viva Voce & Demonstration Guide

> **Revised fork:** Start with [VIVA_QUICKSTART.md](VIVA_QUICKSTART.md) for current commands, metrics, tests and limitations. Use `--help` for current menu numbering. IPC names are PID-scoped, cleanup is process-local, and `make demo` is a smoke test; use `make test` for independent regressions. An unsafe state does not prove deadlock.
**Operating Systems (UE25CS242A) — Level 3 Mini-Project**

---

## Table of Contents
1. [Project Overview & Architecture](#1-project-overview--architecture)
2. [Source Code & System Calls Reference](#2-source-code--system-calls-reference)
3. [CPU Scheduling In-Depth (FR1, FR2)](#3-cpu-scheduling-in-depth-fr1-fr2)
4. [Concurrent Activity Logger & Synchronization (FR3)](#4-concurrent-activity-logger--synchronization-fr3)
5. [Inter-Process Communication & POSIX Semaphores (FR4)](#5-inter-process-communication--posix-semaphores-fr4)
6. [Banker's Algorithm & Resource Safety (FR5)](#6-bankers-algorithm--resource-safety-fr5)
7. [Worker Failure Detection & Process Lifecycle (FR6)](#7-worker-failure-detection--process-lifecycle-fr6)
8. [Resource Limits & System Cleanup (FR7, FR8)](#8-resource-limits--system-cleanup-fr7-fr8)
9. [Official Live Demonstration Tasks (5 Faculty Directives)](#9-official-live-demonstration-tasks-5-faculty-directives)
10. [Official Teacher Viva Voce Questions & Model Answers (Q1 to Q25)](#10-official-teacher-viva-voce-questions--model-answers-q1-to-q25)

---

## 1. Project Overview & Architecture

### Problem Statement
A university computing laboratory operates high-performance computing nodes shared by multiple student and faculty research jobs. Jobs compete for CPU time and shared hardware resources. CampusCompute is a modular C application for Linux that provides:
- Multi-policy CPU scheduling (FCFS, Round Robin, Non-preemptive Priority).
- Thread-safe activity logging using a bounded producer-consumer queue.
- Inter-process communication using POSIX shared memory and named semaphores.
- Deadlock-avoidance safety analysis via Banker's algorithm.
- Robust worker process monitoring with controlled failure detection via `waitpid()`.
- Kernel-enforced resource limits via `setrlimit(RLIMIT_CPU)`.

### Architecture Diagram

```
                              +---------------------------------------+
                              |         main.c (CLI / Menu)           |
                              |  - Dispatches CLI flags & user input  |
                              |  - Runs integrated demo & cleanup     |
                              +-------------------+-------------------+
                                                  |
         +--------------------+-------------------+--------------------+--------------------+
         |                    |                   |                    |                    |
         v                    v                   v                    v                    v
  +--------------+    +---------------+   +---------------+    +---------------+    +---------------+
  | scheduler.c  |    |   logger.c    |   |     ipc.c     |    |   banker.c    |    |   worker.c    |
  | - FCFS       |    | - POSIX Pthr  |   | - shm_open    |    | - Safety Algo |    | - fork()      |
  | - Round Robin|    | - Mutex Lock  |   | - mmap        |    | - Need Matrix |    | - waitpid()   |
  | - Priority   |    | - Cond Vars   |   | - Named Sems  |    | - Safe /      |    | - Status      |
  | - Comparison |    | - Circular Q  |   | - IPC Cleanup |    |   Unsafe Seq  |    |   Inspection  |
  +--------------+    +---------------+   +---------------+    +---------------+    +---------------+
                                                                                            |
                                                                                    +---------------+
                                                                                    |   rlimit.c    |
                                                                                    | - setrlimit() |
                                                                                    | - SIGXCPU     |
                                                                                    +---------------+
```

---

## 2. Source Code & System Calls Reference

| System Call / POSIX API | Header | Purpose in CampusCompute | Why Chosen |
|---|---|---|---|
| `fork()` | `<unistd.h>` | Creates a child worker process in `worker.c`, `ipc.c`, and `rlimit.c`. | Standard UNIX process creation mechanism. |
| `waitpid(pid, &status, options)` | `<sys/wait.h>` | Suspends parent until child changes state; retrieves exit status code or termination signal. | Allows targeted waiting on specific child and non-blocking checks (`WNOHANG`). |
| `setrlimit(resource, &limit)` | `<sys/resource.h>` | Imposes kernel CPU limit (soft=1s, hard=2s) in `rlimit.c`. | Demonstrates real kernel enforcement of CPU consumption. |
| `shm_open(name, oflag, mode)` | `<sys/mman.h>`, `<fcntl.h>` | Creates POSIX shared memory object in `/dev/shm`. | High-throughput zero-copy IPC between processes. |
| `ftruncate(fd, length)` | `<unistd.h>` | Sets size of shared memory region to `sizeof(Packet)`. | Newly created shm has size 0; must be sized before mapping. |
| `mmap(addr, len, prot, flags, fd, off)` | `<sys/mman.h>` | Maps shared memory file descriptor into process address space. | Allows direct pointer access (`pkt->job_id`) across processes. |
| `munmap(addr, len)` | `<sys/mman.h>` | Unmaps shared memory page from virtual address space. | Prevents virtual memory leaks on cleanup. |
| `shm_unlink(name)` | `<sys/mman.h>` | Removes shared memory object name from `/dev/shm`. | Ensures no persistent IPC objects leak into the OS. |
| `sem_open(name, oflag, mode, value)` | `<semaphore.h>` | Creates or opens named POSIX semaphores (`ready`, `done`). | Named semaphores allow process synchronization across address spaces. |
| `sem_timedwait(sem, &ts)` | `<semaphore.h>` | Decrements (locks) semaphore with an absolute timeout (5s). | Prevents coordinator deadlock if child crashes or hangs. |
| `sem_post(sem)` | `<semaphore.h>` | Increments (unlocks) semaphore, waking up blocked waiting processes. | Signals completion of write or read operations. |
| `sem_close(sem)` | `<semaphore.h>` | Closes semaphore descriptor in calling process. | Releases process-level semaphore handle. |
| `sem_unlink(name)` | `<semaphore.h>` | Removes named semaphore from system. | Guarantees complete cleanup. |
| `pthread_create(...)` | `<pthread.h>` | Spawns producer and consumer threads in `logger.c`. | Standard POSIX multithreading within single process memory space. |
| `pthread_join(thread, ...)` | `<pthread.h>` | Blocks until specified thread terminates. | Guarantees all logs are produced and consumed before shutdown. |
| `pthread_mutex_lock/unlock` | `<pthread.h>` | Protects bounded buffer `queue[]` critical section. | Enforces Mutual Exclusion across concurrent threads. |
| `pthread_cond_wait(&cv, &mutex)` | `<pthread.h>` | Atomically unlocks mutex and sleeps waiting on condition. | Avoids busy-waiting when queue is full or empty. |
| `pthread_cond_signal(&cv)` | `<pthread.h>` | Wakes up at least one thread blocked on condition variable. | Notifies consumer when data arrives; notifies producer when space opens. |

---

## 3. CPU Scheduling In-Depth (FR1, FR2)

### Job Attributes (`struct Job`)
- `id`: Unique integer ($1, 2, 3, \dots$).
- `arrival`: Time instant at which the job enters the ready queue ($0 \le \text{arrival} \le 1000$).
- `burst`: Total CPU execution time required ($1 \le \text{burst} \le 100$).
- `priority`: Priority level ($1 \le \text{priority} \le 99$, where lower number = higher priority).
- `status`: String state (`READY` $\rightarrow$ `RUNNING` $\rightarrow$ `COMPLETED`).

### Key Formulas
1. **Completion Time ($CT$)**: Timestamp when the job finishes its final CPU burst.
2. **Turnaround Time ($TAT$)**: Total elapsed time from arrival to completion.
   $$TAT = CT - AT$$
3. **Waiting Time ($WT$)**: Total time the job spent waiting in the ready queue without CPU execution.
   $$WT = TAT - BT$$
4. **Average Metrics**:
   $$\text{Avg } TAT = \frac{\sum_{i=1}^n TAT_i}{n}, \quad \text{Avg } WT = \frac{\sum_{i=1}^n WT_i}{n}$$

### Algorithms & Tie-Breaking Rules

#### 1. First Come First Served (FCFS)
- **Nature**: Non-preemptive.
- **Rule**: Jobs run in ascending order of arrival time ($AT$).
- **Tie-breaker**: If two jobs arrive at the exact same time, the one with lower Job ID runs first.

#### 2. Non-preemptive Priority Scheduling
- **Nature**: Non-preemptive. Once a job is allocated the CPU, it runs to completion.
- **Rule**: At any scheduling point, select the ready job with the lowest priority number.
- **Tie-breaker**:
  1. Priority value (lower number wins).
  2. If priorities are equal: Earlier arrival time wins.
  3. If arrival times are equal: Lower Job ID wins.

#### 3. Round Robin (RR)
- **Nature**: Preemptive.
- **Time Quantum ($q$)**: Configurable (default: $q = 2$).
- **Rule**: The CPU is allocated to the head of the ready queue for up to $q$ time units. If the burst exceeds $q$, the job is preempted and placed at the tail of the queue.
- **Crucial Queue Rule**: When a job's quantum expires at time $t$, **new arrivals occurring at or before time $t$ are admitted into the queue before the preempted job is re-queued**.
- **Tie-breaker for simultaneous arrivals**: Jobs arriving at the same time are queued in order of earlier arrival time, then lower Job ID.

### Benchmark Workload Execution Analysis (Default 5 Jobs)
Default Workload:
- J1: $AT=0, BT=5, Pri=2$
- J2: $AT=1, BT=3, Pri=1$
- J3: $AT=2, BT=8, Pri=4$
- J4: $AT=3, BT=6, Pri=2$
- J5: $AT=4, BT=4, Pri=2$

**Comparison Results**:
- **FCFS**: Execution order: `J1 -> J2 -> J3 -> J4 -> J5`. Avg $TAT = 13.40$, Avg $WT = 8.20$.
- **Priority**: J1 starts at 0 (only job available). At $t=5$, J2, J3, J4, J5 are ready. J2 ($Pri=1$) runs. At $t=8$, J4 ($Pri=2, AT=3$) runs ahead of J5 ($AT=4$). Then J5 runs. Finally J3 ($Pri=4$) runs.
  Execution order: `J1 -> J2 -> J4 -> J5 -> J3`. Avg $TAT = 12.20$, Avg $WT = 7.00$ (Lowest WT!).
- **Round Robin ($q=2$)**: Interleaves slices: `[J1 0-2] [J2 2-4] [J3 4-6] [J1 6-8] ...`. High responsiveness for short jobs (J2 completes at $t=13$), but higher context switching overhead: Avg $TAT = 17.80$, Avg $WT = 12.60$.
- **Round Robin ($q=4$)**: Larger quantum allows J2 ($BT=3$) and J5 ($BT=4$) to complete faster without extra preemptions, dropping Avg $TAT$ to $17.20$ and Avg $WT$ to $12.00$.

---

## 4. Concurrent Activity Logger & Synchronization (FR3)

### The Classical Bounded Buffer Problem
- **Shared resource**: Circular array `queue[LOG_QUEUE_SIZE]` (size 8).
- **Producers**: 3 worker threads producing 5 job log events each (total 15 events + 2 system events = 17 events).
- **Consumer**: 1 logger thread consuming events from the queue, printing them, and writing them to `campuscompute.log`.

### Synchronization Primitives
1. `pthread_mutex_t lock`: Ensures that only one thread accesses `queue`, `head`, `tail`, and `count` at any instant.
2. `pthread_cond_t not_full`:
   - Producers check `while (count == LOG_QUEUE_SIZE)`.
   - If full, producer prints `[Producer] queue full (8/8), waiting for consumer` and calls `pthread_cond_wait(&not_full, &lock)`.
   - Consumer signals `pthread_cond_signal(&not_full)` after popping an element.
3. `pthread_cond_t not_empty`:
   - Consumer checks `while (count == 0)`.
   - If empty, consumer calls `pthread_cond_wait(&not_empty, &lock)`.
   - Producers signal `pthread_cond_signal(&not_empty)` after pushing an element.

### Why `while` loop instead of `if` for condition variables?
To handle **spurious wakeups** and race conditions. A thread may wake up from `pthread_cond_wait` even if no signal was sent, or another thread might claim the slot first before the awakened thread re-acquires the mutex. The `while` loop re-evaluates the predicate upon wakeup.

### Orderly Termination
1. Main thread calls `pthread_join()` on all 3 producer threads.
2. Main thread calls `logger_shutdown()`, which pushes a sentinel stop event (`ev.stop = true`).
3. Consumer thread pops `ev.stop`, breaks out of the loop, flushes `campuscompute.log`, and exits.
4. Main thread joins the consumer thread with `pthread_join(consumer, NULL)`.
5. Guarantees 0 memory leaks, 0 thread leaks, and complete file flushing.

---

## 5. Inter-Process Communication & POSIX Semaphores (FR4)

### Mechanism: Shared Memory (`shm_open` + `mmap`)
- File descriptor opened in `/dev/shm` via `shm_open("/cc_shm_<SRN>", O_CREAT | O_EXCL | O_RDWR, 0600)`.
- Sized with `ftruncate(fd, sizeof(Packet))`.
- Mapped with `mmap(NULL, sizeof(Packet), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)`.
- Child inherits mapped region across `fork()`.

### Synchronization: Dual Named Semaphores
- `sem_ready` (initial value 0): Signaled by parent when job data is written.
- `sem_done` (initial value 0): Signaled by child when job computation is finished and response written.

### Workflow
1. Parent writes job details (`job_id=101`, `name="Fluid_Dynamics_Sim"`, `burst=5`) into `pkt`.
2. Parent calls `sem_post(ready)`.
3. Child, waiting on `sem_timedwait(ready, &timeout)`, wakes up and reads data from shared memory.
4. Child writes response string `"job 101 executed by child <pid>"` into `pkt->response`.
5. Child calls `sem_post(done)` and exits with status 0.
6. Parent wakes from `sem_timedwait(done, &timeout)`, reads the response, and reaps child with `waitpid()`.
7. Cleanup: `munmap()`, `close()`, `shm_unlink()`, `sem_close()`, and `sem_unlink()`.
8. `ipc_objects_remaining()` verifies 0 leftovers in `/dev/shm`.

---

## 6. Banker's Algorithm & Resource Safety (FR5)

### Mathematical Foundation
- $n$ processes ($P_0, \dots, P_{n-1}$), $m$ resource types ($R_0, \dots, R_{m-1}$).
- **Available**: Vector of length $m$. Available instances of each resource.
- **Max**: $n \times m$ matrix. Maximum demand of each process.
- **Allocation**: $n \times m$ matrix. Currently allocated resources to each process.
- **Need**: $n \times m$ matrix. Remaining resources required:
  $$\text{Need}[i][j] = \text{Max}[i][j] - \text{Allocation}[i][j]$$

### Safety Algorithm Steps
1. Let $\text{Work} = \text{Available}$ (length $m$).
2. Let $\text{Finish}[i] = \text{false}$ for $i = 0, 1, \dots, n-1$.
3. Find an index $i$ such that:
   - $\text{Finish}[i] == \text{false}$
   - $\text{Need}[i][j] \le \text{Work}[j]$ for all $j \in \{0, \dots, m-1\}$.
4. If such an $i$ exists:
   - $\text{Work} = \text{Work} + \text{Allocation}[i]$
   - $\text{Finish}[i] = \text{true}$
   - Append $P_i$ to Safe Sequence.
   - Repeat from Step 3.
5. If all $\text{Finish}[i] == \text{true}$, system is in a **SAFE state**.
   If any $\text{Finish}[i] == \text{false}$, system is in an **UNSAFE state** (deadlock possible).

### Demonstration Test Cases

#### Safe State Test Case
- 5 processes, 3 resource types (Total instances = $[10, 5, 7]$).
- $\text{Available} = [3, 3, 2]$.
- Trace:
  - $P_1$ finishes ($\text{Need} [1, 2, 2] \le [3, 3, 2]$) $\rightarrow \text{Work}$ becomes $[5, 3, 2]$.
  - $P_3$ finishes ($\text{Need} [0, 1, 1] \le [5, 3, 2]$) $\rightarrow \text{Work}$ becomes $[7, 4, 3]$.
  - $P_4$ finishes ($\text{Need} [4, 3, 1] \le [7, 4, 3]$) $\rightarrow \text{Work}$ becomes $[7, 4, 5]$.
  - $P_0$ finishes ($\text{Need} [7, 4, 3] \le [7, 4, 5]$) $\rightarrow \text{Work}$ becomes $[7, 5, 5]$.
  - $P_2$ finishes ($\text{Need} [6, 0, 0] \le [7, 5, 5]$) $\rightarrow \text{Work}$ becomes $[10, 5, 7]$.
- **Safe Sequence**: $\langle P_1, P_3, P_4, P_0, P_2 \rangle$.

#### Unsafe State Test Case
- 4 processes, 3 resource types.
- $\text{Available} = [0, 1, 0]$.
- Every process needs at least 2 units of $R_0$ and 1 unit of $R_2$, but available has $0$ units of $R_0$ and $R_2$.
- Result: No process can proceed. System reports: `UNSAFE state. No safe sequence exists; deadlock is possible.`

---

## 7. Worker Failure Detection & Process Lifecycle (FR6)

### Process Lifecycle Implementation
1. **Creation**: Parent calls `fork_flushed()` (flushes stdio buffers before fork so buffered output is not duplicated).
2. **Normal Worker**: Child performs simulation work and exits cleanly with `_exit(0)`.
3. **Simulated Failure**: Child prints `SIMULATED FAILURE (deliberate, not a real OS fault)` and terminates with exit code `42`.
4. **Parent Detection**:
   ```c
   waitpid(pid, &status, 0);
   if (WIFEXITED(status)) {
       int code = WEXITSTATUS(status);
       if (code == 0) // COMPLETED
       else if (code == 42) // FAILED (detected non-zero exit code)
   } else if (WIFSIGNALED(status)) {
       int sig = WTERMSIG(status); // Killed by signal
   }
   ```
5. **Key Viva Point**: We clearly distinguish between normal termination (`exit(0)`) and simulated failure (`exit(42)`), avoiding accidental confusion with kernel-level crashes.

---

## 8. Resource Limits & System Cleanup (FR7, FR8)

### Resource Limit Demonstration (`setrlimit`)
- `struct rlimit limit = { .rlim_cur = 1, .rlim_max = 2 };`
- Child applies limit to itself: `setrlimit(RLIMIT_CPU, &limit);`.
- Child enters CPU-bound infinite spin loop: `while (spin < ~0ULL) spin++;`.
- **Observed Kernel Effect**: Exactly upon reaching 1 second of accumulated CPU time, the Linux kernel generates `SIGXCPU` (signal 24) and forcibly terminates the runaway process.
- Parent inspects status:
  `WIFSIGNALED(status) && WTERMSIG(status) == SIGXCPU` $\rightarrow$ PASS.

### Comprehensive Cleanup Audit
- Logger: Bounded buffer emptied, thread joined, `campuscompute.log` flushed and closed.
- Child Processes: Reaped via `waitpid(-1, NULL, WNOHANG)`. Verified `ECHILD` (no remaining children).
- IPC Objects: `shm_unlink()` and `sem_unlink()` called. `ipc_objects_remaining()` inspects `/dev/shm` and confirms 0 leftover objects.

---

## 9. Official Live Demonstration Tasks (5 Faculty Directives)

According to `OS_Viva.pdf` (Dr. Gokulakrishnan S), students will be asked to perform these five specific tasks without referring to source code documentation:

### Task 1: "Add three jobs and execute FCFS scheduling."
**Action in Interactive Mode**:
```bash
./campuscompute
# Option 5 (--add-job): Enter Arrival=5, Burst=4, Priority=1 (Job 6)
# Option 5 (--add-job): Enter Arrival=6, Burst=2, Priority=3 (Job 7)
# Option 5 (--add-job): Enter Arrival=7, Burst=5, Priority=2 (Job 8)
# Option 9 (--fcfs): Run FCFS
```
**Observation & What to Explain**:
- The default 5 jobs finish at $t=26$.
- Job 6 arrives at $t=5$, waits in queue, and executes from $t=26$ to $30$ ($CT=30, TAT=25, WT=21$).
- Job 7 executes from $t=30$ to $32$ ($CT=32, TAT=26, WT=24$).
- Job 8 executes from $t=32$ to $37$ ($CT=37, TAT=30, WT=25$).
- Confirms non-preemptive FIFO ordering without losing earlier jobs.

### Task 2: "Change the Round Robin time quantum and demonstrate the difference in output."
**Direct CLI Commands**:
```bash
# Run with default quantum 2
./campuscompute --rr 2

# Run with larger quantum 4
./campuscompute --rr 4
```
**Explanation to Faculty**:
- **With $q=2$**: High preemption frequency causes 14 timeline slices. Short jobs get early CPU slices (responsive), but frequent preemption increases average turnaround time ($17.80$).
- **With $q=4$**: Slices drop from 14 to 8 because shorter jobs (like J2 with $BT=3$ and J5 with $BT=4$) complete in a single quantum without preemption. Average turnaround drops to $17.20$.

### Task 3: "Demonstrate producer-consumer synchronization."
**Direct CLI Command**:
```bash
./campuscompute --logger
# Or with custom thread count:
./campuscompute --logger-custom
```
**Observation & What to Explain**:
- Point out log lines showing `[Producer] queue full (8/8), waiting for consumer` to demonstrate blocking synchronization.
- Explain that producers call `pthread_cond_wait(&not_full, &lock)` when buffer is full, and consumer signals `pthread_cond_signal(&not_full)` after popping an element.
- Shows orderly shutdown via sentinel stop message and clean `pthread_join()`.

### Task 4: "Run Banker's Algorithm with one safe and one unsafe state."
**Direct CLI Commands**:
```bash
# Safe state check
./campuscompute --banker-safe

# Unsafe state check (from sample file)
./campuscompute --banker-file samples/banker_unsafe.txt
# (or ./campuscompute --banker-unsafe)
```
**Observation & What to Explain**:
- **Safe State**: Evaluates $\text{Need} \le \text{Work}$. System finds a valid safe sequence $\langle P_1, P_3, P_4, P_0, P_2 \rangle$ and proves all processes can complete.
- **Unsafe State**: Available $[0, 1, 0]$ cannot satisfy any process's minimum requirement ($R_0 \ge 2, R_2 \ge 1$). System flags `UNSAFE state (deadlock possible)`.

### Task 5: "Simulate worker failure and show how the parent detects it."
**Direct CLI Commands**:
```bash
./campuscompute --worker-fail
# Or custom exit code:
./campuscompute --worker-custom
```
**Observation & What to Explain**:
- Child process is spawned using `fork()`.
- Worker deliberately terminates with exit code 42 (`exit(42)`).
- Parent waits using `waitpid(pid, &status, 0)` and inspects status macros:
  - `WIFEXITED(status)` is true.
  - `WEXITSTATUS(status)` returns 42.
- Parent detects non-zero exit code and prints `FAILED (detected from non-zero exit status)`.

---

## 10. Official Teacher Viva Voce Questions & Model Answers (Q1 to Q25)

The following 25 questions and 6 sections are taken verbatim from the official examination syllabus `OS_Viva.pdf` set by **Dr. Gokulakrishnan S**:

### Section 1: Project Understanding and Job Management

#### Q1: What is the main problem that your CampusCompute project is trying to solve?
> **Model Answer**:
> In a shared university computing laboratory, diverse student and faculty workloads (batch simulations, compiles, machine learning tasks) compete for finite CPU cores, memory buffers, and peripherals. Without an intelligent supervisor, uncoordinated execution leads to CPU starvation, unpredictable response times, deadlocks over hardware resources, resource leakage when processes crash, and lack of audit logging.
> **CampusCompute** solves this by providing a unified, modular operating system resource manager that demonstrates:
> 1. Multi-policy CPU scheduling (FCFS, Priority, Round Robin).
> 2. Thread-safe concurrent activity logging using bounded buffers.
> 3. Zero-copy inter-process communication using POSIX shared memory and semaphores.
> 4. Proactive deadlock avoidance using Banker's Algorithm.
> 5. Child process monitoring and failure detection via `fork()` and `waitpid()`.
> 6. Kernel resource quota enforcement via `setrlimit(RLIMIT_CPU)`.

#### Q2: Explain the overall architecture of your project. What are its major modules?
> **Model Answer**:
> CampusCompute is structured into 8 modular C source/header components coordinated by `main.c`:
> 1. **`main.c`**: CLI entry point, 30-command menu dispatcher, CLI flag parsing (`--fcfs`, `--demo`), and integrated test harness.
> 2. **`common.h`**: Shared data structures (`Job`, `Metrics`), state enums, constants, and dynamic SRN resolution (`getenv("SRN")`).
> 3. **`input.c`**: Robust input handling (`read_int()`) with `fgets()`, `strtol()`, range boundary validation, and stdin buffer clearing.
> 4. **`scheduler.c` / `scheduler.h`**: Scheduling engines for FCFS, Non-preemptive Priority, and Round Robin; Gantt chart rendering and metrics calculations (CT, TAT, WT, RT, throughput).
> 5. **`logger.c` / `logger.h`**: Bounded circular buffer activity logger using POSIX threads, mutexes, and condition variables.
> 6. **`ipc.c` / `ipc.h`**: Inter-process communication using POSIX shared memory (`shm_open`, `mmap`) and named semaphores (`sem_open`).
> 7. **`banker.c` / `banker.h`**: Deadlock avoidance via Banker's algorithm; Need matrix generation and safe sequence verification.
> 8. **`worker.c` / `worker.h`**: Process management using `fork()` and `waitpid()` for normal and failure simulation.
> 9. **`rlimit.c` / `rlimit.h`**: Resource limits using `setrlimit(RLIMIT_CPU)` and kernel `SIGXCPU` signal handling.

#### Q3: How do you represent a job in your program? Explain job ID, arrival time, CPU burst, priority and status.
> **Model Answer**:
> In `common.h`, each job is represented by `struct Job`:
> ```c
> typedef enum { JOB_READY, JOB_RUNNING, JOB_COMPLETED } JobState;
> typedef struct {
>     int id;          // Unique job identifier (1, 2, 3...)
>     int arrival;     // Time instant t when job enters system (>= 0)
>     int burst;       // Total CPU time units required for execution (> 0)
>     int remaining;   // Remaining CPU burst time (used in Round Robin)
>     int priority;    // Priority rank (lower integer = higher priority, e.g. 1 > 2)
>     JobState state;  // Lifecycle status (JOB_READY, JOB_RUNNING, JOB_COMPLETED)
>     int completion;  // Timestamp when job completes
>     int turnaround;  // TAT = Completion - Arrival
>     int waiting;     // WT = Turnaround - Burst
>     int response;    // RT = First Run Time - Arrival
> } Job;
> ```
> - **Job ID**: Unique numeric tag.
> - **Arrival Time ($AT$)**: Logical clock tick when the job becomes available for dispatch.
> - **CPU Burst ($BT$)**: Amount of active CPU execution time needed to finish.
> - **Priority**: Scheduling preference (1 is highest priority, 99 is lowest).
> - **Status**: Active state tracking lifecycle: `JOB_READY` (waiting in queue), `JOB_RUNNING` (dispatched on CPU), `JOB_COMPLETED` (finished).

#### Q4: How does your program validate user input? What happens if the user enters invalid job details?
> **Model Answer**:
> In `input.c`, the `read_int(prompt, min, max)` function enforces strict validation:
> 1. Reads raw user input into a safe buffer using `fgets()` to prevent buffer overflows.
> 2. Parses the number using `strtol()` and checks `endptr` to reject trailing non-numeric characters (e.g. entering `4abc`).
> 3. Verifies that the integer falls strictly within `[min, max]`.
> 4. Safely flushes stdin if the user entered more characters than the buffer size.
> If the user enters invalid input (e.g. negative burst, non-numeric letters, or out-of-range priority), the program prints an error message (`[Error] Value must be between min and max`) and re-prompts the user in a loop until valid data is provided. On CLI arguments, malformed flags exit with code 1 and display usage help.

#### Q5: How do you track the lifecycle of a job from arrival to completion?
> **Model Answer**:
> In `scheduler.c`, the lifecycle is tracked through state transitions:
> 1. **Admission**: Created with `state = JOB_READY`, `remaining = burst`. When the logical simulation clock $t$ reaches `job.arrival`, it enters the ready queue.
> 2. **Dispatch**: When the scheduler picks the job, its state transitions to `JOB_RUNNING`. If this is the first time the job is scheduled, its Response Time is recorded: `job.response = current_time - job.arrival`.
> 3. **Preemption (Round Robin)**: When the time quantum expires and `remaining > 0`, the state transitions back to `JOB_READY` and the job is appended to the tail of the ready queue.
> 4. **Completion**: When `remaining == 0`, state transitions to `JOB_COMPLETED`. The completion time is stamped (`job.completion = current_time`), and $TAT = CT - AT$ and $WT = TAT - BT$ are computed.

---

### Section 2: CPU Scheduling Algorithms

#### Q6: Explain the FCFS scheduling algorithm. Demonstrate it using your project output.
> **Model Answer**:
> First Come First Serve (FCFS) is a non-preemptive algorithm that assigns the CPU to jobs in strict ascending order of their arrival time ($AT$). Once a job starts executing, it holds the CPU until its entire burst time finishes. If the CPU is idle when no jobs have arrived, the clock advances to the next arrival time.
> **Demonstration (`./campuscompute --fcfs`)**:
> Using the benchmark workload (J1: $AT=0, BT=5$; J2: $AT=1, BT=3$; J3: $AT=2, BT=8$; J4: $AT=3, BT=6$; J5: $AT=4, BT=4$):
> - Timeline: `[J1 0-5] [J2 5-8] [J3 8-16] [J4 16-22] [J5 22-26]`
> - Completion Times: J1=5, J2=8, J3=16, J4=22, J5=26.
> - Averages: Avg $TAT = 13.40$, Avg $WT = 8.20$.

#### Q7: What is the difference between FCFS, Round Robin and Priority Scheduling?
> **Model Answer**:
> | Feature | FCFS | Round Robin | Priority Scheduling |
> |---|---|---|---|
> | **Type** | Non-preemptive | Preemptive (time-sliced) | Non-preemptive (in our project) |
> | **Selection Basis** | Arrival Time ($AT$) | FIFO Queue with Quantum ($q$) | Priority Rank (lower integer = higher priority) |
> | **Short Job Treatment** | Suffers from Convoy Effect behind long jobs | High responsiveness; short jobs finish quickly | High-priority jobs run first regardless of length |
> | **Starvation** | Impossible | Impossible | Possible for low-priority jobs if high-priority jobs continually arrive |
> | **Context Switches** | Minimum ($n$ dispatches) | High (depends on quantum $q$) | Moderate ($n$ dispatches) |

#### Q8: Why is Round Robin considered a preemptive scheduling algorithm? Demonstrate how your time quantum works.
> **Model Answer**:
> Round Robin is preemptive because the OS scheduler forcibly interrupts a running job when its allocated time slice (quantum $q$) expires, moving the job from `JOB_RUNNING` back to `JOB_READY` at the end of the ready queue, even though it still has remaining burst time.
> **Demonstration**:
> - Run with $q=2$ (`./campuscompute --rr 2`): J1 ($BT=5$) runs from $0-2$ (preempted, 3 left); J2 ($BT=3$) runs from $2-4$ (preempted, 1 left). Timeline has 14 slices.
> - Run with $q=4$ (`./campuscompute --rr 4`): J1 runs from $0-4$ (1 left); J2 ($BT=3$) finishes in one slice from $4-7$. Slices drop to 8, reducing preemption overhead.

#### Q9: How do you calculate completion time, turnaround time and waiting time? Explain with one job from your output.
> **Model Answer**:
> - **Completion Time ($CT$)**: Timestamp when the job finishes execution.
> - **Turnaround Time ($TAT$)**: Total elapsed time from arrival to completion:
>   $$TAT = CT - AT$$
> - **Waiting Time ($WT$)**: Total time the job spent waiting in the ready queue:
>   $$WT = TAT - BT$$
> **Example from FCFS output for Job 2** ($AT=1, BT=3$):
> 1. Job 1 runs from $t=0$ to $t=5$.
> 2. Job 2 gets the CPU at $t=5$ and runs for 3 units, finishing at $t=8 \implies CT = 8$.
> 3. $TAT = CT - AT = 8 - 1 = 7$.
> 4. $WT = TAT - BT = 7 - 3 = 4$ (waited in queue from $t=1$ to $t=5$).

#### Q10: In Priority Scheduling, what happens when two jobs have the same priority? What tie-breaking rule have you implemented?
> **Model Answer**:
> When two or more ready jobs share the same priority rank, CampusCompute applies a deterministic two-level tie-breaking hierarchy:
> 1. **Primary Tie-Break**: Earlier arrival time ($AT$) wins.
> 2. **Secondary Tie-Break**: If arrival times are also identical, the lower Job ID wins.
> **Code implementation** (`scheduler.c` in `pick_priority_job()`):
> ```c
> if (jobs[i].priority < best_pri ||
>    (jobs[i].priority == best_pri && jobs[i].arrival < best_arr) ||
>    (jobs[i].priority == best_pri && jobs[i].arrival == best_arr && jobs[i].id < best_id))
> ```

#### Q11: Run the same set of jobs using all three scheduling algorithms. Which algorithm gives the lowest average waiting time in your test case, and why?
> **Model Answer**:
> Run `./campuscompute --compare`:
> - **FCFS**: Avg $WT = 8.20$, Avg $TAT = 13.40$
> - **Priority**: Avg $WT = 7.00$, Avg $TAT = 12.20$
> - **Round Robin ($q=2$)**: Avg $WT = 12.60$, Avg $TAT = 17.80$
> **Result**: **Priority Scheduling** produces the lowest average waiting time ($7.00$).
> **Why**: In this workload, Job 2 has highest priority ($Pri=1$) and short burst ($BT=3$), running early at $t=5$. Moderate priority jobs (J4 and J5) run ahead of the long, low-priority Job 3 ($Pri=4, BT=8$). Running shorter, high-priority jobs earlier frees up jobs sooner, minimizing cumulative queue waiting time across the workload (similar to the Shortest Job First principle).

---

### Section 3: Multithreading and Synchronization

#### Q12: Why have you used POSIX threads in your concurrent activity logger?
> **Model Answer**:
> POSIX threads (`pthreads`) provide lightweight, shared-memory concurrency within the same process.
> Instead of pausing the main CPU scheduler to perform slow disk I/O, compute tasks spawn producer threads that instantly drop log events into an in-memory buffer. A separate background consumer thread handles formatting and writing them asynchronously to `campuscompute.log`. This decouples compute throughput from disk latency.

#### Q13: Explain the producer-consumer problem. Who is the producer and who is the consumer in your implementation?
> **Model Answer**:
> The producer-consumer problem is a classic synchronization challenge where one or more producer threads insert data into a fixed-size bounded buffer, and one or more consumer threads remove data from it.
> - **Requirement**: Producers must sleep when the buffer is full; consumers must sleep when the buffer is empty; and buffer manipulation must be mutually exclusive.
> - **In CampusCompute (`logger.c`)**:
>   - **Producers**: 3 concurrent worker threads (`producer_thread`), each generating 5 log events (total 15 events + 2 system lifecycle events).
>   - **Consumer**: 1 dedicated logger thread (`consumer_thread`) that dequeues events, prints them, and flushes them to disk.

#### Q14: What is a mutex? What problem can occur if you do not protect the shared queue using a mutex?
> **Model Answer**:
> A **mutex** (`pthread_mutex_t`) is a mutual exclusion locking primitive ensuring that only one thread can execute a critical section at any given time.
> **If the shared queue is not protected**:
> 1. **Race Conditions on Indices**: Two producers could simultaneously read `tail`, write into the same slot, and overwrite each other's data.
> 2. **Lost Updates on Counter**: The `count` variable involves non-atomic read-modify-write CPU instructions (`count++`, `count--`). Concurrent updates cause lost increments/decrements, leading to buffer overflow, buffer underflow, or queue corruption.

#### Q15: Why are condition variables required in your implementation? How do you handle a full or empty queue?
> **Model Answer**:
> Condition variables (`pthread_cond_t`) allow threads to sleep efficiently without busy-waiting (spinning in a CPU loop).
> - **Full Queue**: When `count == QUEUE_CAPACITY` (8), the producer calls `pthread_cond_wait(&not_full, &lock)`. This atomically releases the mutex and suspends the producer. When the consumer dequeues an item, it calls `pthread_cond_signal(&not_full)` to wake a producer.
> - **Empty Queue**: When `count == 0`, the consumer calls `pthread_cond_wait(&not_empty, &lock)`. When a producer enqueues an item, it calls `pthread_cond_signal(&not_empty)` to wake the consumer.
> - **`while` Loop Check**: `pthread_cond_wait` is always wrapped inside a `while (condition)` loop to handle **spurious wakeups** (where the kernel wakes a thread without a signal) and race conditions where another thread claimed the slot first.

---

### Section 4: Inter-Process Communication

#### Q16: What is Inter-Process Communication (IPC)? Why have you selected shared memory for this project?
> **Model Answer**:
> IPC is a set of OS mechanisms that allow distinct processes with isolated virtual address spaces to exchange data and synchronize.
> We selected **POSIX Shared Memory** because it is the **fastest IPC mechanism available in Linux**:
> - Unlike pipes, FIFOs, or sockets, which require copying data from user space to kernel buffer and back to user space (2 context switches and 2 memory copies), shared memory maps physical RAM pages directly into the address spaces of both processes.
> - Once mapped, communication occurs at native memory bus speed with **zero kernel memory copying**.

#### Q17: How do two processes exchange information through POSIX shared memory in your implementation?
> **Model Answer**:
> In `ipc.c`, communication follows a 6-step lifecycle:
> 1. **Creation**: Parent calls `shm_open("/cc_shm_PID", O_CREAT | O_EXCL | O_RDWR, 0600)` to create a shared memory object under `/dev/shm`.
> 2. **Allocation**: Parent calls `ftruncate(fd, sizeof(Packet))` to set the physical segment size.
> 3. **Mapping**: Both parent and child call `mmap(NULL, sizeof(Packet), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)` to map the segment to a `Packet*` pointer.
> 4. **Transfer & Handshake**:
>    - Parent writes job data (`job_id`, `name`, `burst`) into the mapped `Packet` and calls `sem_post(sem_ready)`.
>    - Child, waiting on `sem_timedwait(sem_ready, &timeout)`, wakes up, reads the job, processes it, writes response data into `packet->response`, and calls `sem_post(sem_done)`.
>    - Parent, waiting on `sem_timedwait(sem_done, &timeout)`, reads the response.
> 5. **Reaping**: Parent calls `waitpid()` to cleanly reap the child process.
> 6. **Cleanup**: Both processes call `munmap()` and `close()`, and the parent calls `shm_unlink()` and `sem_unlink()`.

#### Q18: What is the purpose of a semaphore? How is it different from a mutex?
> **Model Answer**:
> A semaphore is a kernel-supported synchronization variable that maintains an integer counter to control access to shared resources or coordinate execution order.
> **Differences between Semaphore and Mutex**:
> 1. **Ownership**: A mutex has ownership—only the specific thread that called `lock()` is permitted to call `unlock()`. A semaphore has no ownership—Process A can wait (`sem_wait`), and Process B can signal (`sem_post`).
> 2. **Scope**: Mutexes are designed for threads within a single process. Named POSIX semaphores (`sem_open`) synchronize separate independent processes across the operating system.
> 3. **Value Range**: A mutex is strictly binary (0 or 1). A counting semaphore can take any non-negative integer value ($0, 1, 2, \dots, N$).

---

### Section 5: Resource Management and Process Handling

#### Q19: Explain the Banker's Algorithm. What are Available, Allocation, Maximum and Need?
> **Model Answer**:
> Banker's Algorithm is a classic **deadlock avoidance** algorithm designed by Edsger Dijkstra. When a process requests resources, the OS simulates resource allocation to determine if granting the request leaves the system in a **Safe State**.
> - **Available $[m]$**: 1D array of length $m$ representing the number of currently unallocated instances of each resource type.
> - **Allocation $[n][m]$**: 2D matrix where `Allocation[i][j]` is the number of instances of resource $j$ currently held by process $i$.
> - **Maximum $[n][m]$**: 2D matrix where `Max[i][j]` is the maximum resource demand declared by process $i$.
> - **Need $[n][m]$**: 2D matrix representing remaining resources process $i$ may still request before completion:
>   $$\text{Need}[i][j] = \text{Maximum}[i][j] - \text{Allocation}[i][j]$$

#### Q20: What is the difference between a safe state and an unsafe state? Demonstrate both using your implementation.
> **Model Answer**:
> - **Safe State**: A state in which there exists at least one ordering of processes (a **Safe Sequence** $\langle P_{s1}, P_{s2}, \dots, P_{sn} \rangle$) such that each process can satisfy its maximum resource needs using currently available resources plus the resources released by earlier processes, guaranteeing no deadlock.
> - **Unsafe State**: A state where no safe sequence exists. If all processes simultaneously demand their maximum resource claims, circular wait occurs, leading to **deadlock**. (Note: An unsafe state does not guarantee immediate deadlock, but the OS can no longer guarantee deadlock prevention).
> **Demonstration**:
> - Safe State: `./campuscompute --banker-safe` $\implies$ finds safe sequence $\langle P_1, P_3, P_4, P_0, P_2 \rangle$.
> - Unsafe State: `./campuscompute --banker-file samples/banker_unsafe.txt` $\implies$ Available $[0, 1, 0]$ cannot satisfy any process's need; flags `UNSAFE state (deadlock possible)`.

#### Q21: What is the purpose of fork() and waitpid()? How does your parent process detect whether a child process completed successfully or failed?
> **Model Answer**:
> - `fork()` creates a new child process by duplicating the calling parent process's address space. In the parent, `fork()` returns the child PID; in the child, it returns 0; on failure, it returns -1.
> - `waitpid(pid, &status, options)` suspends the calling parent process until the child process terminates, retrieving its termination status and releasing its process table entry (preventing zombie processes).
> **Detection Mechanism**:
> The parent inspects `status` using POSIX macros:
> 1. `WIFEXITED(status)`: Evaluates to true if the child terminated normally (via `exit()` or `return`).
> 2. `WEXITSTATUS(status)`: Extracts the exit code (0–255). If `WEXITSTATUS(status) == 0`, the child completed successfully. If non-zero (e.g. 42), the parent detects application-level failure.
> 3. `WIFSIGNALED(status)`: Evaluates to true if the child was killed by an unhandled signal; `WTERMSIG(status)` gives the signal number (e.g. `SIGXCPU`).

#### Q22: How have you simulated worker failure? How do you distinguish a simulated failure from an actual operating-system failure?
> **Model Answer**:
> - In `worker.c`, worker failure is simulated by having the child process deliberately call `exit(42)` (or an arbitrary exit code supplied via `--worker-custom`).
> **Distinguishing Controlled Failure vs OS Crash**:
> - **Simulated / Controlled Failure**: `WIFEXITED(status)` is **true**, and `WEXITSTATUS(status) == 42`. The process terminated cleanly through normal system exit, but returned a failure status code.
> - **Actual OS Crash**: `WIFEXITED(status)` is **false**, and `WIFSIGNALED(status)` is **true**. The process was forcibly killed by the kernel due to a fault, such as `SIGSEGV` (signal 11, invalid memory access) or `SIGFPE` (signal 8, division by zero).

#### Q23: What is setrlimit()? Which resource limit have you applied, and what effect did you observe?
> **Model Answer**:
> `setrlimit()` is a Linux system call that sets soft and hard resource limits for the calling process (`struct rlimit { rlim_cur, rlim_max }`).
> - In `rlimit.c`, we applied `RLIMIT_CPU` with a soft limit of 1 second (`rlim_cur = 1`) and hard limit of 2 seconds (`rlim_max = 2`).
> - **Observed Effect**: When the child process enters a compute-heavy CPU loop, the instant its accumulated user-space CPU consumption reaches 1.0 second, the Linux kernel generates `SIGXCPU` (signal 24). The child's signal handler traps `SIGXCPU`, prints a resource violation notification, and terminates. The parent reaps the child with `waitpid()` and confirms abnormal termination via `WIFSIGNALED(status) && WTERMSIG(status) == SIGXCPU`.

---

### Section 6: Integration and Code Verification

#### Q24: What happens if your program encounters an error during shared-memory or semaphore creation? How do you ensure that resources are cleaned up?
> **Model Answer**:
> In `ipc.c`, creation steps (`shm_open`, `ftruncate`, `mmap`, `sem_open`) are guarded by immediate error checks (`< 0` or `SEM_FAILED`).
> - If an error occurs at any step, the program executes a **structured rollback**:
>   1. If `sem_done` failed, `sem_close(sem_ready)` and `sem_unlink("/cc_sem_ready_PID")` are called.
>   2. If `mmap` failed, descriptors are closed and `shm_unlink("/cc_shm_PID")` is called.
>   3. Errors are reported via `perror()` and the program safely exits without leaking IPC objects into `/dev/shm`.
> - Additionally, CampusCompute uses **PID-scoped names** (`/cc_shm_<pid>`), ensuring no name collisions across concurrent runs, and provides a dedicated cleanup verification command (`./campuscompute --cleanup`) that unlinks any lingering objects.

#### Q25: If I ask you to add a new scheduling algorithm, such as Shortest Job First (SJF), which part of your code would you modify? Explain how you would integrate it without affecting the existing algorithms.
> **Model Answer**:
> Thanks to modular separation, adding SJF requires modifying only 2 files while leaving existing algorithms completely untouched:
> 1. **`scheduler.h`**: Declare the prototype:
>    ```c
>    void schedule_sjf(Job jobs[], int count, Metrics *m);
>    ```
> 2. **`scheduler.c`**: Implement `schedule_sjf()` by adapting `schedule_priority()`:
>    - At current logical clock time $t$, identify all arrived jobs ($AT \le t$).
>    - Pick the job with the smallest CPU burst time ($BT$), breaking ties with arrival time ($AT$) and Job ID.
>    - Advance clock by the job's burst time, and compute $CT, TAT, WT, RT$.
> 3. **`main.c`**: Add an option in `print_menu()` and a `--sjf` CLI flag in `parse_args()`.
> Existing FCFS, Round Robin, and Priority functions remain 100% unaffected.


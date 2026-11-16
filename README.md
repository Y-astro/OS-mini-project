# CampusCompute (UE25CS242A Level 3 Mini-Project)
**Intelligent Job Scheduling and Resource Management**

- **Team Members**:
  - Yatin R (`PES2UG25CS617`)
  - Thirukumaran (`PES2UG25CS586`)
- **Course**: Operating Systems (UE25CS242A) — Level 3 Mini-Project
- **Environment**: C on Linux / Ubuntu / WSL Ubuntu

Every result is computed dynamically at run time. The integrated demonstration reports real `PASS`/`FAIL` metrics for every component.

---

## 1. Prerequisites
- `gcc` (with C99 support)
- `make`
- POSIX threads (`-pthread`) and Real-Time extensions (`-lrt`) (standard on Linux / Ubuntu / WSL).

---

## 2. Build, Run, and Packaging

```bash
# Set your SRN environment variable (matches terminal prompt and program banner)
export SRN='PES2UG25CS617'
export PS1='[$SRN] \w\$ '

# Build the executable
make

# Run interactive CLI menu
./campuscompute
# or: make run

# Run CLI help
./campuscompute --help

# Run integrated automated demonstration (exit code 0 = all checks passed)
./campuscompute --demo
# or: make demo

# Cleanup IPC objects and verify
./campuscompute --cleanup

# Package source and documentation for submission with integrity check
make zip

# Clean build artifacts
make clean
```

---

## 3. Project Architecture and Modules

| File | Module / Responsibility | Functional Requirement |
|---|---|---|
| `main.c` | CLI entry point, menu dispatch, CLI flags, integrated demo & cleanup audit | FR8 |
| `scheduler.c` / `scheduler.h` | Job lifecycle, FCFS, Round Robin (configurable quantum), Non-preemptive Priority, comparison | FR1, FR2 |
| `logger.c` / `logger.h` | Concurrent bounded producer-consumer activity logger using POSIX threads, mutex, condition variables | FR3 |
| `ipc.c` / `ipc.h` | Inter-process communication using POSIX shared memory (`shm_open`, `mmap`) and named semaphores | FR4 |
| `banker.c` / `banker.h` | Banker's safety algorithm: safe state, unsafe state, and interactive custom state input | FR5 |
| `worker.c` / `worker.h` | Process management with `fork()` and `waitpid()`, normal exit and simulated failure detection | FR6 |
| `rlimit.c` / `rlimit.h` | OS resource limit demonstration using `setrlimit(RLIMIT_CPU)` and kernel `SIGXCPU` handling | FR7 |
| `input.c` / `common.h` | Validated integer input routines, shared constants, and data structures | Common |

---

## 4. Key Design & Algorithm Details

1. **Job Representation & Lifecycle (FR1)**:
   - Attributes: Job ID, Arrival Time ($0-1000$), Burst Time ($1-100$), Priority ($1-99$), and Status.
   - Lifecycle: `READY` $\rightarrow$ `RUNNING` $\rightarrow$ `COMPLETED`.

2. **CPU Scheduling (FR2)**:
   - **FCFS**: Jobs execute strictly in arrival order. Tie-break: Lower Job ID.
   - **Round Robin**: Configurable time quantum (default: 2). New arrivals admitted before preempted jobs are re-queued. Tie-break for simultaneous arrivals: Earlier arrival time, then lower Job ID.
   - **Priority (Non-preemptive)**: Lower numerical value indicates higher priority. Tie-break: Earlier arrival time, then lower Job ID.
   - **Metrics**:
     - Completion Time ($CT$): Time when job finishes execution.
     - Turnaround Time ($TAT$): $TAT = CT - AT$
     - Waiting Time ($WT$): $WT = TAT - BT$
     - Average $TAT$ and Average $WT$.

3. **Activity Logger (FR3)**:
   - Bounded circular buffer of size 8.
   - 3 producer threads, 1 consumer thread writing to `campuscompute.log`.
   - Synchronized using `pthread_mutex_t`, `not_full`, and `not_empty` condition variables.
   - Orderly shutdown via sentinel event and clean `pthread_join()`.

4. **Inter-Process Communication (FR4)**:
   - POSIX shared memory (`/cc_shm_<SRN>`) via `shm_open`, `ftruncate`, `mmap`.
   - Named semaphores (`/cc_sem_ready_<SRN>`, `/cc_sem_done_<SRN>`) with `sem_timedwait`.
   - Clean unlinking via `shm_unlink()` and `sem_unlink()`.

5. **Banker's Safety Algorithm (FR5)**:
   - Matrices: Available, Max, Allocation, Need ($\text{Need} = \text{Max} - \text{Alloc}$).
   - Safe state demonstrates complete safe execution sequence: $\langle P_1, P_3, P_4, P_0, P_2 \rangle$.
   - Unsafe state correctly identifies deadlock condition where no process can satisfy $\text{Need} \le \text{Work}$.

6. **Worker Failure Detection (FR6)**:
   - Child process created using `fork()`.
   - Parent tracks child with `waitpid(pid, &status, 0)`.
   - Normal completion: `_exit(0)`, detected via `WIFEXITED(status)` and `WEXITSTATUS(status) == 0`.
   - Controlled simulated failure: `_exit(42)`, clearly identified as simulated failure and detected via `WEXITSTATUS(status) == 42`.

7. **Resource Limits & Cleanup (FR7)**:
   - Child process enforces `setrlimit(RLIMIT_CPU, &limit)` with soft limit 1s.
   - Runaway CPU loop is halted by Linux kernel via `SIGXCPU` (signal 24).
   - Parent detects `WIFSIGNALED(status)` and `WTERMSIG(status) == SIGXCPU`.
   - `--cleanup` validates no orphaned processes or leftover IPC objects in `/dev/shm`.

---

## 5. Command Reference & CLI Flags

| Option # | Flag | Description |
|---|---|---|
| 1 | `--input` | Input custom jobs (replaces current workload) |
| 2 | `--default` | Load default workload (5 benchmark jobs) |
| 3 | `--add-job` | Add a single new job to the current workload |
| 4 | `--edit-priority` | Modify priority of an existing job |
| 5 | `--set-quantum` | Set Round Robin time quantum (or `--quantum <val>`) |
| 6 | `--show` | Display current job table |
| 7 | `--fcfs` | Run First Come First Served scheduling |
| 8 | `--rr` | Run Round Robin scheduling (or `--rr <quantum>`) |
| 9 | `--priority` | Run Non-preemptive Priority scheduling |
| 10 | `--compare` | Compare all 3 scheduling algorithms on current job set |
| 11 | `--logger` | Demonstrate multithreaded producer-consumer logger |
| 12 | `--ipc` | Demonstrate shared memory and named semaphore IPC |
| 13 | `--banker-safe` | Demonstrate Banker's algorithm safe state |
| 14 | `--banker-unsafe` | Demonstrate Banker's algorithm unsafe state |
| 15 | `--banker-input` | Enter custom state and run Banker's safety check |
| 16 | `--worker-ok` | Demonstrate normal worker process completion |
| 17 | `--worker-fail` | Demonstrate simulated worker failure detection |
| 18 | `--rlimit` | Demonstrate CPU resource limit enforcement (`SIGXCPU`) |
| 19 | `--demo` | Run full integrated test suite with PASS/FAIL summary |
| 20 | `--cleanup` | Verify cleanup of threads, processes, and IPC resources |
| 0 | - | Exit interactive CLI |

---

## 6. Screenshot Checklist Guide (S01 to S24)

Set the prompt first before capturing screenshots:
```bash
export SRN='PES2UG25CS617'
export PS1='[$SRN] \w\$ '
```

| Screenshot | Command | What It Demonstrates |
|---|---|---|
| **S01** | `pwd; echo $SRN` | Terminal environment, SRN prompt, and working directory |
| **S02** | `gcc --version; make --version` | GCC compiler and Make build tool availability |
| **S03** | `ls -la` | Project directory layout, source files, and Makefile |
| **S04** | `make clean; make` | Clean build from source with zero compiler warnings |
| **S05** | `./campuscompute --help` | CLI usage, flags, and available commands |
| **S06** | `./campuscompute --fcfs` | FCFS scheduling order, completion, TAT, and waiting times |
| **S07** | `./campuscompute --rr` | Round Robin scheduling, quantum, timeline, and metrics |
| **S08** | `./campuscompute --priority` | Priority scheduling, tie-breaking rule, and metrics |
| **S09** | `./campuscompute --compare` | Side-by-side comparison of FCFS, Priority, and Round Robin |
| **S10** | `./campuscompute --logger` | Concurrent producer-consumer activity and queue blocking |
| **S11** | `./campuscompute --logger` | Thread synchronization and orderly thread termination |
| **S12** | `./campuscompute --ipc` | Inter-process communication via POSIX shared memory |
| **S13** | `./campuscompute --ipc` | Named semaphore coordination and clean resource unlinking |
| **S14** | `./campuscompute --banker-safe` | Banker's algorithm safe state and safe sequence $\langle P_1, P_3, P_4, P_0, P_2 \rangle$ |
| **S15** | `./campuscompute --banker-unsafe`| Banker's algorithm identifying an unsafe state with deadlock |
| **S16** | `./campuscompute --worker-ok` | Worker process creation via `fork()` and normal completion |
| **S17** | `./campuscompute --worker-fail` | Controlled simulated failure and detection via `waitpid()` |
| **S18** | `./campuscompute --rlimit` | CPU resource limit demonstration and kernel `SIGXCPU` delivery |
| **S19** | `./campuscompute --bogus` | Input validation and error handling for invalid CLI option |
| **S20** | `./campuscompute --cleanup; ls /dev/shm \| grep cc_` | Verification that all processes, threads, and IPC objects are released |
| **S21** | `./campuscompute --demo` | Integrated demonstration running all tests with PASS summary |
| **S22** | `cat campuscompute.log` | Activity log file generated by the multithreaded logger |
| **S23** | `ls -la` | Final compiled executable, source files, and build assets |
| **S24** | `make zip` | Submission ZIP creation and archive integrity verification |

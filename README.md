# CampusCompute — Intelligent Job Scheduling and Resource Management

> **Quickstart Guides:**
> - [VIVA_QUICKSTART.md](VIVA_QUICKSTART.md) — 2-page rapid viva cheat sheet, system calls, formulas, and live-coding commands.
> - [DEMO_WALKTHROUGH.md](DEMO_WALKTHROUGH.md) — 5-minute practical review walkthrough script for Dr. Gokulakrishnan S.
> - [PROJECT_STUDY_GUIDE.md](PROJECT_STUDY_GUIDE.md) — Deep conceptual architecture and source code walkthrough.
> - [VIVA_GUIDE.md](VIVA_GUIDE.md) — Top 25 Viva Voce technical questions and model answers.

[![Language](https://img.shields.io/badge/Language-C99-00599C?logo=c)](#)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%2F%20Ubuntu%20%2F%20WSL-E95420?logo=ubuntu)](https://ubuntu.com)
[![Standards](https://img.shields.io/badge/Standard-POSIX.1--2008-black)](#)
[![Build](https://img.shields.io/badge/Build-Make%20%7C%20GCC-success)](#)
[![Course](https://img.shields.io/badge/Course-UE25CS242A%20Operating%20Systems-blue)](#)
[![Repository](https://img.shields.io/badge/GitHub-Y--astro%2FOS--mini--project-181717?logo=github)](https://github.com/Y-astro/OS-mini-project)

> **Level 3 Mini-Project — Operating Systems (UE25CS242A)**  
> **Course Faculty**: Dr. Gokulakrishnan S  
> **Institution**: PES University  
> **Team Members**:
> - **Yaduveer Pavan** (`PES2UG25CS609`)
> - **Yatin R** (`PES2UG25CS617`)  
> **Repository**: [https://github.com/Y-astro/OS-mini-project](https://github.com/Y-astro/OS-mini-project)

---

## 1. Project Overview & Scenario

In a shared university high-performance computing facility, students and researchers submit diverse compute jobs (batch simulations, model training, analytical scripts). These jobs compete for limited CPU cores, memory buffers, and hardware resources.

**CampusCompute** is an industrial-grade, modular Linux command-line application implemented in C (C99 standard, POSIX.1-2008). It directly addresses all 8 core Functional Requirements (FR1–FR8) mandated by the Level 3 Mini-Project curriculum:

- **FR1 — Job Lifecycle & Process Representation**: Validated job intake, unique identifiers, arrival times, CPU burst requirements, priorities, and runtime state tracking (`READY` $\rightarrow$ `RUNNING` $\rightarrow$ `COMPLETED`).
- **FR2 — CPU Scheduling Algorithms**: Implementation of First Come First Serve (FCFS), Non-preemptive Priority, and preemptive Round Robin (with configurable time quantum). Features Gantt charts, Completion Time ($CT$), Turnaround Time ($TAT$), Waiting Time ($WT$), Response Time ($RT$), CPU Utilization %, and Throughput.
- **FR3 — Concurrent Activity Logger**: Multithreaded bounded circular buffer implementing the classic Producer-Consumer synchronization problem using POSIX threads (`pthread`), a mutual exclusion lock (`pthread_mutex_t`), and condition variables (`pthread_cond_t`). Includes interactive thread and event configuration.
- **FR4 — Inter-Process Communication (IPC)**: Communication between parent and child processes using POSIX shared memory (`shm_open`, `ftruncate`, `mmap`) and POSIX named semaphores (`sem_open`, `sem_timedwait`, `sem_post`) with zero-leak resource unlinking.
- **FR5 — Resource-Safety Analysis (Banker's Algorithm)**: Deadlock avoidance through Banker's Safety Algorithm. Calculates the dynamic Need matrix ($\text{Need} = \text{Max} - \text{Alloc}$) and differentiates safe states (yielding a safe execution sequence) from unsafe states. Supports custom matrix input via text files.
- **FR6 — Worker Process Management & Failure Detection**: Process creation using `fork()`, status monitoring and reaping via `waitpid()`, and parent-side evaluation of exit codes (`WIFEXITED`, `WEXITSTATUS`) to distinguish normal completion from controlled simulated failures.
- **FR7 — Resource Quotas & System Cleanup**: Kernel CPU quota enforcement using `setrlimit(RLIMIT_CPU)` with `SIGXCPU` signal handling, accompanied by deterministic cleanup of all child processes, threads, shared memory segments, and semaphores.
- **FR8 — User Interface & Error Handling**: 30-command interactive terminal interface, standardized CLI flag parsing, strict input boundary validation, and comprehensive error reporting.

---

## 2. Directory Structure & Architecture

```
OS-mini-project/
├── common.h                 # Shared definitions, Job & Metrics structs, dynamic SRN resolver
├── input.c                  # Robust integer input parsing, boundary checking, buffer flushing
├── scheduler.h              # Scheduler interfaces (FCFS, RR, Priority, Comparison, Workload IO)
├── scheduler.c              # Scheduling algorithms, Gantt chart rendering, metrics calculation
├── logger.h                 # Multithreaded logger API
├── logger.c                 # Bounded circular buffer, POSIX threads, mutex & condition variables
├── ipc.h                    # Shared memory & semaphore IPC definitions
├── ipc.c                    # POSIX shm_open, mmap, named semaphores with timeout protection
├── banker.h                 # Banker's algorithm interface
├── banker.c                 # Safety algorithm, Need matrix calculation, safe/unsafe evaluations
├── worker.h                 # Worker process interface
├── worker.c                 # fork() + waitpid() execution, normal exit & failure simulation
├── rlimit.h                 # Resource limits interface
├── rlimit.c                 # setrlimit(RLIMIT_CPU) and SIGXCPU signal handling
├── main.c                   # CLI entry point, 30-option menu, argument parsing, demo runner
├── Makefile                 # Build automation (-Wall -Wextra), make demo, make test, make zip
├── samples/
│   ├── jobs_lab.txt         # Benchmark 5-job workload file for instant loading
│   └── banker_unsafe.txt    # Unsafe state matrix sample demonstrating deadlock potential
├── tests/
│   ├── test_campuscompute.py   # Unit test suite verifying core CLI behaviors
│   └── rigorous_evaluation.py # 19-test automated test suite covering all FRs and live-coding
├── DEMO_WALKTHROUGH.md      # 5-minute presentation script for faculty review
├── VIVA_QUICKSTART.md       # Quick-reference viva cheat sheet (commands, formulas, APIs)
├── VIVA_GUIDE.md            # Comprehensive Viva Voce preparation guide (Top 25 Q&As)
├── PROJECT_STUDY_GUIDE.md   # Complete conceptual architecture and code walkthrough
└── README.md                # Project documentation and official screenshot checklist
```

### System Calls & POSIX APIs Used

| System Call / API | Header | Purpose in CampusCompute |
|---|---|---|
| `fork()` | `<unistd.h>` | Creates isolated child processes for workers, IPC receiver, and resource limit tests. |
| `waitpid()` | `<sys/wait.h>` | Suspends parent until child changes state; inspects status (`WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED`, `WTERMSIG`). |
| `setrlimit()` | `<sys/resource.h>` | Enforces a strict 1-second CPU limit; the Linux kernel terminates runaway jobs via `SIGXCPU`. |
| `shm_open()` | `<sys/mman.h>`, `<fcntl.h>` | Creates or opens a POSIX shared memory object under `/dev/shm`. |
| `ftruncate()` | `<unistd.h>` | Sets the physical byte size of the shared memory segment to `sizeof(Packet)`. |
| `mmap()` / `munmap()` | `<sys/mman.h>` | Maps and unmaps shared memory pages into the virtual address spaces of parent and child. |
| `shm_unlink()` | `<sys/mman.h>` | Removes the shared memory object from the OS namespace upon completion. |
| `sem_open()` / `sem_close()` | `<semaphore.h>` | Creates, opens, and closes POSIX named semaphores for synchronization. |
| `sem_timedwait()` | `<semaphore.h>` | Decrements semaphore with a timeout to prevent parent deadlocks if a child fails. |
| `sem_post()` | `<semaphore.h>` | Increments semaphore, unblocking waiting processes. |
| `sem_unlink()` | `<semaphore.h>` | Removes named semaphores from the system. |
| `pthread_create()` / `pthread_join()` | `<pthread.h>` | Spawns and joins producer and consumer threads. |
| `pthread_mutex_lock()` / `unlock()` | `<pthread.h>` | Enforces Mutual Exclusion over the bounded circular log queue. |
| `pthread_cond_wait()` / `signal()` | `<pthread.h>` | Coordinates producer (`not_full`) and consumer (`not_empty`) buffer availability. |

---

## 3. Build & Execution Instructions

### Prerequisites
Standard C compiler, Make, and POSIX development headers (available on Ubuntu 20.04/22.04/24.04 and WSL):
```bash
sudo apt update && sudo apt install -y build-essential gcc make zip unzip python3
```

### Environment Configuration
Before capturing demonstration screenshots or executing tests, configure your SRN to match your terminal prompt and application banner:
```bash
# For Yaduveer Pavan:
export SRN='PES2UG25CS609'
export PS1='[$SRN] \w\$ '

# For Yatin R:
export SRN='PES2UG25CS617'
export PS1='[$SRN] \w\$ '
```

### Compilation
```bash
make clean
make
```
Compiled with strict compiler flags (`-Wall -Wextra -g -std=c99 -pthread -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE`). Builds with 0 warnings and 0 errors.

### Running CampusCompute
```bash
# 1. Interactive Menu
./campuscompute
# or:
make run

# 2. View Command-Line Help
./campuscompute --help

# 3. Automated Integrated Demonstration (14 checks with PASS/FAIL status)
./campuscompute --demo
# or:
make demo

# 4. Independent Python Regression Tests
make test
# or full 19-test evaluation:
python3 tests/rigorous_evaluation.py

# 5. Standalone CLI Flags
./campuscompute --fcfs              # Run FCFS scheduling
./campuscompute --rr                # Run Round Robin (default quantum 2)
./campuscompute --rr 4              # Run Round Robin with custom quantum 4
./campuscompute --priority          # Run Non-preemptive Priority scheduling
./campuscompute --compare           # Compare all 3 algorithms on the current workload
./campuscompute --logger            # Multithreaded producer-consumer logger
./campuscompute --ipc               # Shared memory & named semaphore IPC
./campuscompute --banker-safe       # Banker's algorithm safe state check
./campuscompute --banker-unsafe     # Banker's algorithm unsafe state check
./campuscompute --worker-ok         # Normal child process execution
./campuscompute --worker-fail       # Simulated worker failure detection
./campuscompute --rlimit            # CPU resource limit demonstration (SIGXCPU)
./campuscompute --cleanup           # Cleanup verification of processes, threads & IPC

# 6. Create Submission ZIP Archive with CRC Integrity Check
make zip
# or for teammate submission:
make zip SRN=PES2UG25CS617
```

---

## 4. Interactive CLI Menu Reference

```
CampusCompute | Job Scheduling & Resource Management | PES2UG25CS609

Commands (type the number at the prompt, or run ./campuscompute --<flag>):
   1  Input custom jobs (replace current list)       --input
   2  Load jobs from a file (arrival burst priority) --jobs
   3  Generate random jobs (env SEED=n to reproduce) --random
   4  Load default workload (5 jobs)                 --default
   5  Add a new job to current workload              --add-job
   6  Change an existing job's priority              --edit-priority
   7  Set Round Robin time quantum                   --set-quantum
   8  Display current jobs                           --show
   9  FCFS scheduling                                --fcfs
  10  Round Robin scheduling                         --rr
  11  Priority scheduling (non-preemptive)           --priority
  12  Compare all scheduling policies                --compare
  13  Producer-consumer logger (default benchmark)   --logger
  14  Producer-consumer logger (custom threads)      --logger-custom
  15  Logger: submit custom message to queue         --logger-msg
  16  Shared memory + semaphore IPC (benchmark)      --ipc
  17  Shared memory IPC: send custom job packet      --ipc-custom
  18  Banker's algorithm: safe state                 --banker-safe
  19  Banker's algorithm: unsafe state               --banker-unsafe
  20  Banker's algorithm: load state from file       --banker-file
  21  Banker's algorithm: enter your own state       --banker-input
  22  Worker process: normal completion              --worker-ok
  23  Worker process: simulated failure              --worker-fail
  24  Worker process: custom simulated exit code     --worker-custom
  25  Resource limit demo (RLIMIT_CPU)               --rlimit
  26  Integrated demonstration                       --demo
  27  Verify cleanup of threads/IPC/processes        --cleanup
  28  Toggle step-by-step scheduling trace           --trace
  29  Toggle actual scheduling event logger          --log-schedule
  30  Workload dashboard and policy comparison       --dashboard
   0  Clean up and exit
   ?  Show this menu

Chain commands in a single invocation, e.g. --trace --jobs samples/jobs_lab.txt --rr 3
```

---

## 5. CPU Scheduling Algorithms & Formulas

### Metric Definitions
1. **Completion Time ($CT$)**: Timestamp when a job finishes its entire CPU burst.
2. **Turnaround Time ($TAT$)**: Total elapsed time from arrival to completion:
   $$TAT = CT - AT$$
3. **Waiting Time ($WT$)**: Total time a job spent waiting in the ready queue:
   $$WT = TAT - BT$$
4. **Response Time ($RT$)**: Time from arrival until the job first gets CPU allocation:
   $$RT = \text{First Run Time} - AT$$
5. **CPU Utilization %**: Percentage of total makespan during which CPU was actively executing jobs:
   $$\text{CPU Utilization} = \frac{\sum BT}{\text{Makespan}} \times 100\%$$
6. **Throughput**: Jobs completed per unit time:
   $$\text{Throughput} = \frac{n}{\text{Makespan}}$$

### Tie-Breaking Rules
- **FCFS**: Jobs execute strictly in order of arrival time ($AT$). If simultaneous, the lower Job ID executes first.
- **Priority (Non-preemptive)**: Lower numerical priority value indicates higher scheduling priority ($1 > 2 > 3$).
  - Tie-break 1: Earlier arrival time wins.
  - Tie-break 2: Lower Job ID wins.
- **Round Robin (Preemptive)**:
  - User-configurable time quantum $q$ (default $q=2$).
  - When a job's time slice expires at time $t$, **newly arriving jobs arriving at or before $t$ are enqueued before the preempted job is re-appended to the ready queue**.
  - Simultaneous arrivals are enqueued in ascending order of arrival time, then Job ID.

### Benchmark Workload Comparison (Default 5 Jobs)
Workload: J1 ($AT=0, BT=5, Pri=2$), J2 ($AT=1, BT=3, Pri=1$), J3 ($AT=2, BT=8, Pri=4$), J4 ($AT=3, BT=6, Pri=2$), J5 ($AT=4, BT=4, Pri=2$).

| Policy | Execution Timeline | Avg Turnaround | Avg Waiting | Avg Response | Key Advantage |
|---|---|---|---|---|---|
| **FCFS** | `[J1 0-5] [J2 5-8] [J3 8-16] [J4 16-22] [J5 22-26]` | 13.40 | 8.20 | 8.20 | Zero scheduling overhead; fair FIFO order |
| **Priority** | `[J1 0-5] [J2 5-8] [J4 8-14] [J5 14-18] [J3 18-26]` | **12.20** | **7.00** | **7.00** | **Lowest Avg WT & TAT**; favors critical tasks |
| **Round Robin ($q=2$)** | Slices: `[J1 0-2] [J2 2-4] [J3 4-6] [J1 6-8] [J4 8-10]...` | 17.80 | 12.60 | **3.80** | **Lowest response latency**; interactive fairness |
| **Round Robin ($q=4$)** | Slices: `[J1 0-4] [J2 4-7] [J3 7-11] [J4 11-15] [J5 15-19]...` | 17.20 | 12.00 | 4.80 | Balanced context switches vs. responsiveness |

---

## 6. Banker's Algorithm & Resource Safety

### Safety Analysis
- **Available $[m]$**: Units of each resource type currently unallocated in the system.
- **Max $[n][m]$**: Maximum resource claim declared by each process.
- **Allocation $[n][m]$**: Units currently allocated to each process.
- **Need $[n][m]$**: Remaining resources required for process completion:
  $$\text{Need}[i][j] = \text{Max}[i][j] - \text{Allocation}[i][j]$$

### Safe State Verification
Given 5 processes ($P_0$–$P_4$), 3 resource types ($R_0, R_1, R_2$), and initial $\text{Available} = [3, 3, 2]$:
1. $P_1$ needs $[1, 2, 2] \le [3, 3, 2] \implies \text{Work} = [3, 3, 2] + [2, 0, 0] = [5, 3, 2]$.
2. $P_3$ needs $[0, 1, 1] \le [5, 3, 2] \implies \text{Work} = [5, 3, 2] + [2, 1, 1] = [7, 4, 3]$.
3. $P_4$ needs $[4, 3, 1] \le [7, 4, 3] \implies \text{Work} = [7, 4, 3] + [0, 0, 2] = [7, 4, 5]$.
4. $P_0$ needs $[7, 4, 3] \le [7, 4, 5] \implies \text{Work} = [7, 4, 5] + [0, 1, 0] = [7, 5, 5]$.
5. $P_2$ needs $[6, 0, 0] \le [7, 5, 5] \implies \text{Work} = [7, 5, 5] + [3, 0, 2] = [10, 5, 7]$.
- **Valid Safe Sequence**: $\langle P_1, P_3, P_4, P_0, P_2 \rangle$. The state is verified **SAFE**.

### Unsafe State Verification
Given 4 processes, 3 resource types, and $\text{Available} = [0, 1, 0]$ (or loaded from `samples/banker_unsafe.txt`):
- Every active process requires at least 2 units of $R_0$ and 1 unit of $R_2$.
- With 0 units of $R_0$ and $R_2$ available, no process can satisfy $\text{Need} \le \text{Work}$.
- Program classifies the state as **UNSAFE** (deadlock is possible if processes demand maximum claims).

---

## 7. Practical Demonstration & Live Coding Quick Guide

When the faculty asks live coding or practical questions during the review, use these exact commands:

| Faculty Prompt | Command / Menu Option | What Happens / What to Explain |
|---|---|---|
| **1. Add a new job and run FCFS** | Option `5` (`--add-job`), enter $AT=5, BT=4, Pri=1$. Then Option `9` (`--fcfs`). | Adds Job 6 to the active workload without overwriting existing jobs. Runs FCFS showing Job 6 executing at $t=26 \rightarrow 30$. |
| **2. Change RR quantum and compare** | `./campuscompute --rr 2`<br>`./campuscompute --rr 4` | Demonstrates that increasing quantum from 2 to 4 drops timeline slices from 14 to 8, cutting preemption overhead and lowering average turnaround time. |
| **3. Change job priority and run Priority** | Option `6` (`--edit-priority`), select Job 4, set priority to `1`. Then Option `11` (`--priority`). | Job 4 now has Priority 1. At $t=5$, Job 2 ($AT=1$) and Job 4 ($AT=3$) both have Priority 1. By arrival tie-breaking, Job 2 runs first, then Job 4 runs at $t=8$. |
| **4. Compare all 3 algorithms on same workload** | `./campuscompute --compare` | Runs FCFS, Priority, and Round Robin on the identical job set and displays comparative tables for turnaround, waiting, and response times. |
| **5. Demonstrate Producer-Consumer Logger** | `./campuscompute --logger`<br>or custom: `./campuscompute --logger-custom` | Shows producer threads filling the circular queue, queue-full blocking (`queue full (8/8), waiting for consumer`), condition variable signaling, and clean thread joins. |
| **6. Demonstrate Banker's safe & unsafe states** | `./campuscompute --banker-safe`<br>`./campuscompute --banker-file samples/banker_unsafe.txt` | Shows safe sequence $\langle P_1, P_3, P_4, P_0, P_2 \rangle$ for the safe state, and clear deadlock-risk detection for the unsafe state. |
| **7. Demonstrate Worker Failure Detection** | `./campuscompute --worker-fail`<br>or custom: `./campuscompute --worker-custom` | Worker child exits with status 42 (or user-defined code e.g. 88). Parent detects non-zero exit code via `waitpid()` and `WEXITSTATUS()` macros. |
| **8. Demonstrate Resource Limit Enforcement** | `./campuscompute --rlimit` | Sets 1-second CPU limit via `setrlimit(RLIMIT_CPU)`. When worker enters a CPU compute loop, the Linux kernel terminates it via `SIGXCPU` (signal 24). |

---

## 8. Official Screenshot Checklist (S01 to S24)

> [!IMPORTANT]
> Configure your prompt before taking screenshots:
> ```bash
> export SRN='PES2UG25CS609'
> export PS1='[$SRN] \w\$ '
> ```
> Combine all screenshots sequentially into a single PDF named `<YOUR_SRN>.pdf` (e.g., `PES2UG25CS609.pdf`). Each screenshot must be accompanied by the exact one-sentence explanation below.

| Screenshot # | Execution Command | Required One-Line Explanation |
|---|---|---|
| **S01** | `pwd; echo $SRN` | S01 – Environment and SRN prompt: Demonstrates the Ubuntu/WSL terminal, full SRN in the prompt, and current working directory. |
| **S02** | `gcc --version; make --version` | S02 – Compiler and build tools: Confirms availability of GCC C99 compiler and Make build utility. |
| **S03** | `ls -la` | S03 – Project files: Displays the project directory structure, source files, header files, and Makefile. |
| **S04** | `make clean; make` | S04 – Clean build: Demonstrates clean compilation from source with all compiler warnings enabled (`-Wall -Wextra`) and zero errors. |
| **S05** | `./campuscompute --help` | S05 – CLI help/usage: Displays available command-line flags, options, and usage instructions. |
| **S06** | `./campuscompute --fcfs` | S06 – FCFS scheduling: Shows FCFS execution order, completion time, turnaround time, waiting time, and calculated averages. |
| **S07** | `./campuscompute --rr` | S07 – Round Robin scheduling: Shows Round Robin execution order, time quantum of 2, and calculated scheduling metrics. |
| **S08** | `./campuscompute --priority` | S08 – Priority scheduling: Demonstrates non-preemptive priority scheduling, tie-breaking rules, and calculated metrics. |
| **S09** | `./campuscompute --compare` | S09 – Scheduling comparison: Compares FCFS, Priority, and Round Robin algorithms using the exact same job workload. |
| **S10** | `./campuscompute --logger` | S10 – Producer-consumer logger: Shows producer threads populating the bounded buffer and queue-full waiting states. |
| **S11** | `./campuscompute --logger` | S11 – Thread synchronization and termination: Demonstrates orderly consumer extraction, condition variable signaling, and clean thread joins. |
| **S12** | `./campuscompute --ipc` | S12 – Shared-memory IPC: Demonstrates inter-process communication between parent and child processes via POSIX shared memory. |
| **S13** | `./campuscompute --ipc` | S13 – Semaphore coordination and cleanup: Shows synchronization using POSIX named semaphores and unlinking of IPC resources. |
| **S14** | `./campuscompute --banker-safe` | S14 – Banker's safe state: Demonstrates Banker's safety algorithm identifying a safe resource state with a valid safe sequence. |
| **S15** | `./campuscompute --banker-unsafe` | S15 – Banker's unsafe state: Demonstrates Banker's algorithm correctly detecting an unsafe state with deadlock potential. |
| **S16** | `./campuscompute --worker-ok` | S16 – Normal worker process: Shows child process creation using `fork()` and successful normal completion with exit status 0. |
| **S17** | `./campuscompute --worker-fail` | S17 – Simulated worker failure: Demonstrates simulated worker failure exit code 42 and parent-side detection via `waitpid()`. |
| **S18** | `./campuscompute --rlimit` | S18 – Resource-limit demonstration: Demonstrates process CPU quota enforcement using `setrlimit()` and termination by kernel `SIGXCPU`. |
| **S19** | `./campuscompute --bogus` | S19 – Invalid input/command: Shows error handling and helpful usage messages when invalid command-line arguments are provided. |
| **S20** | `./campuscompute --cleanup; ls /dev/shm \| grep cc_` | S20 – Cleanup verification: Verifies that all created child processes have ended and all program IPC objects are removed from `/dev/shm`. |
| **S21** | `./campuscompute --demo` | S21 – Integrated execution: Shows the comprehensive automated test suite verifying all 14 project modules with PASS status. |
| **S22** | `cat campuscompute.log` | S22 – Generated logs: Displays the persistent timestamped log file created by the multithreaded logger module. |
| **S23** | `ls -la` | S23 – Final source and build files: Shows the final project directory with compiled binary, source files, and build assets. |
| **S24** | `make zip` | S24 – Submission ZIP: Demonstrates automated generation of the submission ZIP archive and verification of archive integrity. |

---

## 9. Submission Verification

To prepare the final submission archive:
```bash
make zip
```
Output:
```
rm -f PES2UG25CS609.zip
zip -r PES2UG25CS609.zip samples tests main.c input.c scheduler.c logger.c ipc.c banker.c worker.c rlimit.c common.h scheduler.h logger.h ipc.h banker.h worker.h rlimit.h Makefile README.md DEMO_WALKTHROUGH.md VIVA_GUIDE.md PROJECT_STUDY_GUIDE.md VIVA_QUICKSTART.md
Verifying archive integrity:
unzip -t PES2UG25CS609.zip
No errors detected in compressed data of PES2UG25CS609.zip.
```

For teammate Yatin R (`PES2UG25CS617`):
```bash
make zip SRN=PES2UG25CS617
```

---

## 10. Live Demonstration Without Hardcoded Data

The default 5-job workload and built-in Banker states are provided for convenience. For live faculty demonstration, you can feed arbitrary data on the fly:

```bash
# 1. Load an arbitrary workload dictated by the examiner (format: arrival burst priority per line)
./campuscompute --jobs samples/jobs_lab.txt --compare
./campuscompute --jobs samples/jobs_lab.txt --rr 3

# 2. Generate an unpredictable random workload (SEED printed for reproducibility)
./campuscompute --random 6 --compare
SEED=42 ./campuscompute --random 5 --fcfs

# 3. Load custom Banker's state matrix from file
./campuscompute --banker-file samples/banker_unsafe.txt

# 4. Enable step-by-step CPU execution tick tracing
./campuscompute --trace --jobs samples/jobs_lab.txt --priority
```

---

## 11. Authors & Acknowledgments

- **Yaduveer Pavan** (`PES2UG25CS609`) — Department of Computer Science and Engineering, PES University
- **Yatin R** (`PES2UG25CS617`) — Department of Computer Science and Engineering, PES University
- **Course Instructor**: Dr. Gokulakrishnan S, Department of Computer Science and Engineering, PES University
- **Course**: UE25CS242A — Operating Systems (Level 3 Mini-Project)

# CampusCompute — Viva quickstart (revised fork)

## Build and run (Ubuntu / WSL)

```bash
sudo apt install build-essential python3 zip unzip
git clone https://github.com/Y-astro/OS-mini-project.git
cd OS-mini-project
make clean && make
make test
make run
```

Use your actual SRN via `export SRN=YOUR_SRN`. Use `make zip SRN=YOUR_SRN` to package the submission. No internet needed after dependencies and source are available. Run `./campuscompute --help` for the authoritative menu; avoid memorizing older menu numbers.

## Live demo

| Command | Explain |
|---|---|
| `./campuscompute --dashboard` | Workload, last simulated job state, policy recommendations based on measured simulation metrics |
| `./campuscompute --trace --log-schedule --rr 2` | Arrivals, circular queue, dispatch, preemption, completion; real pthread log events |
| `./campuscompute --rr 4` | Larger quantum changes slices and response/turnaround |
| `./campuscompute --jobs samples/jobs_lab.txt --compare` | File input, same jobs across policies |
| `SEED=7 ./campuscompute --random 8 --compare` | Reproducible randomized workloads |
| `./campuscompute --logger` | Three producers, five events each, two system events = 17 |
| `./campuscompute --ipc --cleanup` | POSIX shared memory, two named semaphores, checked cleanup in the same process |
| `./campuscompute --banker-safe --banker-unsafe` | Safe sequence vs unsafe state, not necessarily deadlock |
| `./campuscompute --worker-ok --worker-fail --rlimit` | Exit 0, deliberate exit 42, kernel SIGXCPU |
| `./campuscompute --rr 4abc` | Invalid input, nonzero exit |

Interactive mode: add jobs, edit priority, set quantum, run policies, display statuses. All data and toggles are process-local. Chain flags in a single invocation; a new process resets defaults. Trace and log flags toggle once per invocation. Logging applies to individual scheduling runs, not comparison; log file is overwritten on each logger initialization. Disable colors with `NO_COLOR=1`.

## Study in this order

1. **main.c/common.h/input.c**: command table, Job and Metrics structs, strict strtol parsing, ranges, process-local data; explain why fork buffers are flushed and why _exit is used.
2. **scheduler.c**: pick(), better(), simulate_nonpreemptive(), simulate_rr(), admit_arrivals(), queue_push/pop(), finish(). Dry run all three algorithms. RR requeue changes status back to READY. Trace is emitted from the actual simulation. Logical time is NOT Linux scheduling time.
3. **Metrics**: CT = last slice end; TAT = CT - arrival; WT = TAT - burst; response = first dispatch - arrival; CPU utilization = 100 * busy / makespan; throughput = n / makespan (clock starts at zero). Slice count differs from direct job-to-job switches, which exclude idle transitions and same-job repetitions. No context-switch duration is simulated.
4. **logger.c**: bounded circular buffer, lock around count/head/tail, while loops for spurious wakeups; cond_wait releases/reacquires lock; stop sentinel, join all producers before stopping consumer; writes and flushes checked. Scheduler logs real simulation transitions; worker demos are separate. Do not fork while the logger thread is running.
5. **ipc.c**: shm_open(O_CREAT|O_EXCL), ftruncate, mmap(MAP_SHARED), sem_open initial 0, fork, parent writes and posts ready, child reads/writes and posts done; sem_timedwait, waitpid, WIFEXITED before WEXITSTATUS, munmap/close/sem_close/unlink. Names use PID; ownership flags prevent removing other instances. Cleanup verifies named objects for the current PID only. Forced parent death may leave objects; inspect /dev/shm manually, never delete peers' resources.
6. **banker.c**: calculate Need=Max-Allocation, Work=Available; finish a feasible process and add its allocation; repeat until all finish or no progress. Safety check only, not a real resource admission controller. Strict file tokens, bounds and trailing input validation.
7. **worker.c/rlimit.c**: fork returns 0 in child, PID in parent, -1 on error. waitpid reaps child; retry EINTR. Nonzero exit is an application failure but normal OS termination; signal death is abnormal. RLIMIT_CPU soft 1 second of CPU time, hard 2; default SIGXCPU action terminates child, parent unaffected.
8. **Makefile/tests**: compilation vs linking, -pthread, -lrt, -Wall/-Wextra, make test invokes Python unittest on compiled C executable. make demo is a smoke test, not an independent proof of scheduler correctness. make clean preserves submission ZIPs.

## Expected default workload results

| Policy | Average WT | Average TAT | Average response | Slices |
|---|---:|---:|---:|---:|
| FCFS | 8.20 | 13.40 | 8.20 | 5 |
| Priority | 7.00 | 12.20 | 7.00 | 5 |
| RR q=2 | 12.60 | 17.80 | 2.80 | 14 |
| RR q=4 | 12.00 | 17.20 | 5.40 | 8 |

Safe sequence for built-in Banker state: P1, P3, P4, P0, P2. These are expected values, not a claim that the executable has been tested on your machine.

## Official 5 Live Demonstration Tasks (from OS_Viva.pdf)

1. **Add three jobs and execute FCFS**:
   - Menu Option `5` (`--add-job`): J6 ($AT=5, BT=4, Pri=1$), J7 ($AT=6, BT=2, Pri=3$), J8 ($AT=7, BT=5, Pri=2$).
   - Menu Option `9` (`--fcfs`): Runs FCFS; J1–J5 complete at $t=26$; J6 runs $26 \rightarrow 30$, J7 runs $30 \rightarrow 32$, J8 runs $32 \rightarrow 37$.
2. **Change RR time quantum**:
   - `./campuscompute --rr 2` vs `./campuscompute --rr 4`.
   - $q=2$ gives 14 slices (responsive, high context switches); $q=4$ drops to 8 slices (turnaround drops from 17.80 to 17.20).
3. **Demonstrate Producer-Consumer synchronization**:
   - `./campuscompute --logger` (or `--logger-custom`).
   - Point out `[Producer] queue full (8/8), waiting for consumer`; explain `pthread_cond_wait(&not_full, &lock)`.
4. **Run Banker's Algorithm with safe & unsafe state**:
   - Safe: `./campuscompute --banker-safe` $\implies$ Safe sequence $\langle P_1, P_3, P_4, P_0, P_2 \rangle$.
   - Unsafe: `./campuscompute --banker-file samples/banker_unsafe.txt` $\implies$ Available $[0, 1, 0]$ cannot satisfy any process; flagged UNSAFE.
5. **Simulate worker failure & parent detection**:
   - `./campuscompute --worker-fail` (or `--worker-custom`).
   - Child calls `exit(42)`; parent calls `waitpid()` and checks `WIFEXITED(status)` and `WEXITSTATUS(status) == 42`.

## 25 Viva Questions Quick Reference (Syllabus Mapping)

| # | Topic | Key Answer / Formula / System Call |
|---|---|---|
| **Q1** | Problem solved | University shared compute facility; scheduling, IPC, concurrency, deadlock avoidance, process safety |
| **Q2** | Architecture | 8 C modules coordinated by `main.c`: `scheduler`, `logger`, `ipc`, `banker`, `worker`, `rlimit`, `input`, `common.h` |
| **Q3** | Job representation | `struct Job` in `common.h`: `id`, `arrival`, `burst`, `remaining`, `priority`, `state` (`READY/RUNNING/COMPLETED`), metrics |
| **Q4** | Input validation | `input.c` using `fgets()` + `strtol()`, range `[min, max]`, boundary checks, flushing stdin, looping on error |
| **Q5** | Job lifecycle | `JOB_READY` (queue) $\rightarrow$ `JOB_RUNNING` (CPU dispatch, $RT$) $\rightarrow$ preempt/requeue $\rightarrow$ `JOB_COMPLETED` ($CT, TAT, WT$) |
| **Q6** | FCFS algorithm | Non-preemptive FIFO by arrival time; J1–J5: order `J1->J2->J3->J4->J5`, Avg WT=8.20, Avg TAT=13.40 |
| **Q7** | FCFS vs RR vs Priority | FCFS: non-preemptive arrival; RR: preemptive time quantum; Priority: non-preemptive priority rank ($1 > 2$) |
| **Q8** | RR preemption | CPU forcibly interrupted at quantum $q$; running job requeued behind newly arrived jobs |
| **Q9** | CT, TAT, WT calculation | $TAT = CT - AT$; $WT = TAT - BT$. Job 2 ($AT=1, BT=3$): runs $5 \rightarrow 8$, $CT=8, TAT=7, WT=4$ |
| **Q10** | Priority tie-breaking | 1) Earlier arrival time wins. 2) Lower Job ID wins (`scheduler.c` in `pick_priority_job()`) |
| **Q11** | Lowest Avg WT algorithm | **Priority** (Avg WT=7.00) because high-priority short jobs (J2, J4, J5) run before long J3 ($BT=8$) |
| **Q12** | POSIX threads for logger | Decouples CPU execution from slow disk I/O; concurrent in-memory logging with background consumer file flush |
| **Q13** | Producer-Consumer | 3 worker threads produce 5 logs each into bounded buffer (size 8); 1 consumer thread writes to `campuscompute.log` |
| **Q14** | Mutex purpose | `pthread_mutex_t` prevents race conditions on `tail`, `head`, and corrupted non-atomic updates to `count` |
| **Q15** | Condition variables | `not_full` and `not_empty` prevent busy-waiting; always in `while` loop to safeguard against spurious wakeups |
| **Q16** | IPC & Shared memory | High-speed zero-copy IPC; memory mapped directly into virtual address space, bypassing kernel buffer copies |
| **Q17** | Shm exchange flow | `shm_open` $\rightarrow$ `ftruncate` $\rightarrow$ `mmap` $\rightarrow$ write packet $\rightarrow$ `sem_post(ready)` $\rightarrow$ child reads $\rightarrow$ `sem_post(done)` $\rightarrow$ `munmap`/`unlink` |
| **Q18** | Semaphore vs Mutex | Mutex has ownership, binary, intra-process; Semaphore has no ownership, can be counting, operates across processes |
| **Q19** | Banker's matrices | Available (1D), Allocation (2D), Max (2D), $\text{Need}[i][j] = \text{Max}[i][j] - \text{Allocation}[i][j]$ |
| **Q20** | Safe vs Unsafe state | Safe: $\exists$ Safe Sequence guaranteeing no deadlock. Unsafe: no sequence; deadlock possible if max claimed |
| **Q21** | `fork()` & `waitpid()` | `fork()` returns child PID to parent, 0 to child; `waitpid()` reaps child, `WIFEXITED`, `WEXITSTATUS`, `WIFSIGNALED` |
| **Q22** | Simulated vs OS failure | Simulated: `WIFEXITED` is true, `WEXITSTATUS == 42`. OS crash: `WIFSIGNALED` is true, killed by signal (e.g. `SIGSEGV`) |
| **Q23** | `setrlimit()` effect | `RLIMIT_CPU` soft=1s; kernel sends `SIGXCPU` (signal 24) terminating runaway CPU spin loop |
| **Q24** | IPC error cleanup | Rollback mechanism in `ipc.c`: `sem_unlink()`, `munmap()`, `shm_unlink()`; `--cleanup` cleans PID-scoped objects |
| **Q25** | Adding SJF without impact | Add `schedule_sjf()` in `scheduler.h/c` (pick smallest $BT$ among arrived), wire flag in `main.c`; other policies untouched |

## Limits of this implementation

Scheduling and Banker calculations are simulations; IPC, threads, child processes and resource limits are real POSIX operations. The dashboard is a terminal summary, not a kernel monitor. The modules are not a fully connected resource allocator executing every scheduled job. No fabricated runtime results should be presented.

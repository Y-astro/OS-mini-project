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
| RR q=2 | 12.60 | 17.80 | 3.20 | 14 |
| RR q=4 | 12.00 | 17.20 | 7.20 | 8 |

Safe sequence for built-in Banker state: P1, P3, P4, P0, P2. These are expected values, not a claim that the executable has been tested on your machine.

## Live coding practice

- Add J6 (arrival 5, burst 4, priority 1); predict FCFS finish at 30.
- Modify RR quantum and explain how arrivals enter before requeue.
- Set J4 priority to 1; J2 still wins the tie due to earlier arrival.
- Change available resources in a custom Banker state and manually find a sequence.
- Explain why the consumer cannot access an empty queue and why a mutex alone is insufficient.
- Explain why exit(42) can be a PASS in the controlled failure demo.
- Run make test; investigate rather than ignore failing assertions.

## Limits of this implementation

Scheduling and Banker calculations are simulations; IPC, threads, child processes and resource limits are real POSIX operations. The dashboard is a terminal summary, not a kernel monitor. The modules are not a fully connected resource allocator executing every scheduled job. No fabricated runtime results should be presented.

# CampusCompute (UE25CS242A Level 3 Mini-Project)

SRN: `PES2UG25CS586`. C on Linux/Ubuntu. Every result is computed at run time. The demonstration summary reports real PASS/FAIL results.

## Prerequisites
`gcc`, `make`, POSIX threads and `librt` (standard on Ubuntu/WSL).

## Build, run, clean
```bash
make                      # build ./campuscompute
./campuscompute           # interactive menu
./campuscompute --help    # list commands
./campuscompute --demo    # integrated demonstration (exit code 0 = all checks passed)
./campuscompute --cleanup # remove this program's shared memory/semaphores, verify nothing is left
make clean                # remove objects, binary and log
```
Every menu entry also works as a flag, for example `./campuscompute --fcfs` or `./campuscompute --banker-safe`.

## Files
| File | Purpose |
|---|---|
| `main.c` | Command table, menu, flags, integrated demo, cleanup check (FR8) |
| `scheduler.c` | Jobs, FCFS, Round Robin, Priority, comparison (FR1, FR2) |
| `logger.c` | Bounded producer-consumer logger: pthreads, mutex, condition variables (FR3) |
| `ipc.c` | POSIX shared memory + named semaphores between parent and child (FR4) |
| `banker.c` | Banker's safety algorithm: two test cases and custom input (FR5) |
| `worker.c` | `fork()` + `waitpid()`, normal and simulated failure (FR6) |
| `rlimit.c` | `setrlimit(RLIMIT_CPU)` and its observed effect (FR7) |
| `input.c` | Validated integer input shared by all modules |

## Design notes
- Round Robin: quantum 2. New arrivals join the queue before a preempted job.
- Priority (non-preemptive): lower number wins. Ties go to the earlier arrival, then the lower job ID.
- FCFS: ties on arrival go to the lower job ID.
- Limits: up to 20 jobs, arrival at most 1000, burst at most 100.
- Worker failure is simulated with `exit(42)` and always labelled "SIMULATED". It is not a real OS fault.
- Only objects named `/cc_*_PES2UG25CS586` are created and removed.

## Menu numbers
| # | Command | # | Command |
|---|---|---|---|
| 1 | input custom jobs | 10 | banker-safe |
| 2 | load default jobs | 11 | banker-unsafe |
| 3 | show jobs | 12 | banker-input |
| 4 | fcfs | 13 | worker-ok |
| 5 | rr | 14 | worker-fail |
| 6 | priority | 15 | rlimit |
| 7 | compare | 16 | demo |
| 8 | logger | 17 | cleanup |
| 9 | ipc | 0 | exit |

## Screenshots
Set the prompt first: `export SRN='PES2UG25CS586'; export PS1='[$SRN] \w\$ '`

| Shot | Command |
|---|---|
| S01 | `pwd; echo $SRN` |
| S02 | `gcc --version; make --version` |
| S03 | `ls -la` |
| S04 | `make clean; make` |
| S05 | `./campuscompute --help` |
| S06-S09 | `./campuscompute --fcfs`, `--rr`, `--priority`, `--compare` |
| S10-S11 | `./campuscompute --logger` (queue-full waits, then orderly join) |
| S12-S13 | `./campuscompute --ipc` (shared memory exchange, semaphores, cleanup) |
| S14-S15 | `./campuscompute --banker-safe`, `--banker-unsafe` |
| S16-S17 | `./campuscompute --worker-ok`, `--worker-fail` |
| S18 | `./campuscompute --rlimit` |
| S19 | `./campuscompute --bogus`, or type `abc` at the menu prompt |
| S20 | `./campuscompute --cleanup; ls /dev/shm \| grep cc_` |
| S21 | `./campuscompute --demo` |
| S22 | `cat campuscompute.log` |
| S23 | `ls -la` |
| S24 | `make clean; zip PES2UG25CS586.zip *.c *.h Makefile README.md; unzip -l PES2UG25CS586.zip; unzip -t PES2UG25CS586.zip` |

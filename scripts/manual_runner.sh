#!/usr/bin/env bash
# CampusCompute — Interactive Manual Screenshot Helper
# Run this inside your real Kitty/Alacritty terminal on workspace 5!

set -e
cd "$(dirname "$0")/.."

export SRN="${SRN:-PES2UG25CS609}"
export PS1="[$SRN] \w\$ "
mkdir -p screenshots

echo "======================================================================"
echo "CampusCompute — Interactive Manual Screenshot Runner"
echo "Active SRN: $SRN"
echo "Screenshots will be saved to: $(pwd)/screenshots/S01.png ... S24.png"
echo "======================================================================"
echo ""

run_step() {
    local num="$1"
    local title="$2"
    local cmd="$3"
    
    clear
    echo "[$SRN] $(pwd)\$ $cmd"
    echo "----------------------------------------------------------------------"
    eval "$cmd"
    echo "----------------------------------------------------------------------"
    echo ">> [STEP $num/24]: $title"
    echo ">> Action: Capture your terminal window now and save as: screenshots/$num.png"
    echo ""
    read -p "Press [Enter] when saved to proceed to next command (or Ctrl+C to stop)... " _
}

run_step "S01" "Environment & SRN prompt" 'pwd; echo "Logged in user: $(whoami)"; echo "Active SRN: $SRN"'
run_step "S02" "Compiler and build tools" 'gcc --version | head -n 1; make --version | head -n 1'
run_step "S03" "Project directory and source files" 'ls -la'
run_step "S04" "Clean build from source" 'make clean && make'
run_step "S05" "CLI help and menu options" './campuscompute --help'
run_step "S06" "FCFS scheduling execution order and metrics" './campuscompute --fcfs'
run_step "S07" "Round Robin scheduling with quantum 2" './campuscompute --rr'
run_step "S08" "Priority scheduling and tie-breaking" './campuscompute --priority'
run_step "S09" "Policy comparison on same workload" './campuscompute --compare'
run_step "S10" "Producer-consumer logger queue filling" './campuscompute --logger'
run_step "S11" "Thread synchronization and termination" './campuscompute --logger'
run_step "S12" "Shared-memory IPC data exchange" './campuscompute --ipc'
run_step "S13" "Semaphore coordination and cleanup" './campuscompute --ipc'
run_step "S14" "Banker'\''s safe state and safe sequence" './campuscompute --banker-safe'
run_step "S15" "Banker'\''s unsafe state detection" './campuscompute --banker-file samples/banker_unsafe.txt'
run_step "S16" "Worker normal completion status" './campuscompute --worker-ok'
run_step "S17" "Controlled worker failure detection" './campuscompute --worker-fail'
run_step "S18" "Resource quota limit (RLIMIT_CPU)" './campuscompute --rlimit'
run_step "S19" "Invalid command and error handling" './campuscompute --bogus || true'
run_step "S20" "System and IPC cleanup verification" './campuscompute --cleanup && (ls /dev/shm | grep cc_ || echo "Zero lingering IPC objects in /dev/shm")'
run_step "S21" "Integrated execution summary" './campuscompute --demo'
run_step "S22" "Generated log file sample" 'head -n 25 campuscompute.log'
run_step "S23" "Final project files inventory" 'ls -lh campuscompute common.h main.c input.c scheduler.c logger.c ipc.c banker.c worker.c rlimit.c Makefile'
run_step "S24" "Submission ZIP contents and check" 'make zip && unzip -l $SRN.zip | head -n 18 && unzip -t $SRN.zip'

echo ""
echo "======================================================================"
echo "All 24 steps completed!"
echo "Now run: python3 scripts/build_deliverables.py to compile your PDF!"
echo "======================================================================"

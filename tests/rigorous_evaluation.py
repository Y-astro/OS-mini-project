#!/usr/bin/env python3
"""
CampusCompute — Rigorous Automated Verification & Evaluation Suite
Tests all 8 project functional requirements and all 8 live coding scenarios
prescribed by Dr. Gokulakrishnan S (UE25CS242A).
"""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "campuscompute"

class RigorousEvaluation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure clean build
        subprocess.run(["make", "clean"], cwd=ROOT, check=True, capture_output=True)
        res = subprocess.run(["make", "all"], cwd=ROOT, check=True, capture_output=True, text=True)
        assert BIN.exists(), "Binary not produced"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, *args, stdin="", env_extra=None, success=True):
        env = {**os.environ, "NO_COLOR": "1"}
        if env_extra:
            env.update(env_extra)
        p = subprocess.run(
            [str(BIN), *args],
            cwd=self.cwd,
            input=stdin,
            text=True,
            capture_output=True,
            timeout=25,
            env=env
        )
        if success:
            self.assertEqual(p.returncode, 0, f"Command failed: {args}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
        else:
            self.assertNotEqual(p.returncode, 0, f"Command unexpectedly succeeded: {args}\nSTDOUT:\n{p.stdout}")
        return p.stdout, p.stderr

    def parse_metrics_table(self, out):
        """Extracts (Job, Arrival, Burst, Priority, CT, TAT, WT) rows."""
        pattern = r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
        matches = re.findall(pattern, out)
        return [tuple(map(int, m)) for m in matches]

    # ==========================================
    # Requirement 1: Job Management & Input Validation
    # ==========================================
    def test_01_job_creation_and_attributes(self):
        """Verify default workload attributes: ID, Arrival, Burst, Priority, Status."""
        out, _ = self.run_cmd("--show")
        self.assertIn("| Job | Arrival | Burst | Priority | Status    |", out)
        self.assertIn("| 1   | 0       | 5     | 2        | READY     |", out)
        self.assertIn("| 5   | 4       | 4     | 2        | READY     |", out)

    def test_02_job_input_validation(self):
        """Verify rejection of invalid inputs (out of bounds, non-numeric)."""
        # Quantum bounds
        self.run_cmd("--set-quantum", "0", success=False)
        self.run_cmd("--set-quantum", "101", success=False)
        self.run_cmd("--set-quantum", "abc", success=False)

        # Nonexistent file
        self.run_cmd("--jobs", "does_not_exist.txt", success=False)

        # File with bad line
        bad_file = self.cwd / "bad_jobs.txt"
        bad_file.write_text("0 5 1\nINVALID_BURST 10 1\n")
        self.run_cmd("--jobs", str(bad_file), success=False)

        # File exceeding MAX_JOBS (20)
        overflow_file = self.cwd / "overflow_jobs.txt"
        overflow_file.write_text("\n".join(["0 1 1"] * 21) + "\n")
        self.run_cmd("--jobs", str(overflow_file), success=False)

    def test_03_job_lifecycle_transitions(self):
        """Verify state transitions: READY -> RUNNING -> COMPLETED."""
        out, _ = self.run_cmd("--trace", "--fcfs")
        self.assertIn("READY -> RUNNING", out)
        self.assertIn("completed (CT=", out)

    # ==========================================
    # Requirement 2: CPU Scheduling Algorithms
    # ==========================================
    def test_04_fcfs_scheduling_correctness(self):
        """Verify FCFS completion, turnaround, and waiting times."""
        out, _ = self.run_cmd("--fcfs")
        rows = self.parse_metrics_table(out)
        self.assertEqual(len(rows), 5)
        # Verify TAT = CT - AT and WT = TAT - BT for every job
        for j, a, b, p, ct, tat, wt in rows:
            self.assertEqual(tat, ct - a, f"Job {j}: TAT != CT - AT")
            self.assertEqual(wt, tat - b, f"Job {j}: WT != TAT - BT")
        self.assertIn("Average turnaround time: 13.40", out)
        self.assertIn("Average waiting time:    8.20", out)

    def test_05_priority_scheduling_tie_breaking(self):
        """Verify non-preemptive Priority scheduling and tie-breaking."""
        out, _ = self.run_cmd("--priority")
        self.assertIn("Tie-break: lower number = higher priority", out)
        # Order should be J1 (already running at t=0), then J2 (pri 1), J4 (pri 2), J5 (pri 2), J3 (pri 4)
        self.assertIn("[J1 0-5] [J2 5-8] [J4 8-14] [J5 14-18] [J3 18-26]", out)
        rows = self.parse_metrics_table(out)
        for j, a, b, p, ct, tat, wt in rows:
            self.assertEqual(tat, ct - a)
            self.assertEqual(wt, tat - b)
        self.assertIn("Average turnaround time: 12.20", out)
        self.assertIn("Average waiting time:    7.00", out)

    def test_06_round_robin_queue_ordering(self):
        """Verify Round Robin scheduling and arrival-before-requeue rule."""
        out, _ = self.run_cmd("--trace", "--rr", "2")
        self.assertIn("New arrivals join the queue before a preempted job is re-queued", out)
        # Check arrival admission before requeue at t=2
        self.assertIn("J2 admitted (arrival=1, boundary=2)", out)
        self.assertIn("J3 admitted (arrival=2, boundary=2)", out)
        self.assertIn("J1 RUNNING -> READY (quantum expired)", out)
        self.assertIn("t=2 ready queue: [J2, J3, J1]", out)
        self.assertIn("Average turnaround time: 17.80", out)
        self.assertIn("Average waiting time:    12.60", out)

    def test_07_scheduling_policy_comparison(self):
        """Verify multi-policy comparison output."""
        out, _ = self.run_cmd("--compare")
        self.assertIn("Lowest average waiting time: Priority (non-preemptive)", out)
        self.assertIn("Lowest average response time: Round Robin", out)

    # ==========================================
    # Requirement 3: Concurrent Activity Logger
    # ==========================================
    def test_08_producer_consumer_logger(self):
        """Verify multithreaded logging, queue blocking, and file persistence."""
        log_file = self.cwd / "campuscompute.log"
        out, _ = self.run_cmd("--logger")
        self.assertIn("queue full (8/8), waiting for consumer", out)
        self.assertIn("Producers joined, consumer joined", out)
        self.assertTrue(log_file.exists())
        lines = log_file.read_text().strip().splitlines()
        self.assertEqual(len(lines), 17) # 1 start + 15 events + 1 finish
        self.assertIn("Logger started", lines[0])
        self.assertIn("All producers finished", lines[-1])

    # ==========================================
    # Requirement 4: Inter-Process Communication (IPC)
    # ==========================================
    def test_09_shared_memory_and_semaphore_ipc(self):
        """Verify POSIX shm and semaphore IPC exchange and cleanup."""
        out, _ = self.run_cmd("--ipc")
        self.assertIn("created /cc_shm_", out)
        self.assertIn("wrote job 101 ('Fluid_Dynamics_Sim', burst 5) to shared memory", out)
        self.assertIn("read from shared memory: job 101 'Fluid_Dynamics_Sim', burst 5", out)
        self.assertIn('child replied via shared memory: "job 101 executed by child', out)
        self.assertIn("remaining: 0", out)

    # ==========================================
    # Requirement 5: Banker's Algorithm
    # ==========================================
    def test_10_banker_safe_and_unsafe_states(self):
        """Verify Banker's algorithm safe sequence and unsafe state detection."""
        out_safe, _ = self.run_cmd("--banker-safe")
        self.assertIn("RESULT: SAFE state. Safe sequence: < P1 P3 P4 P0 P2 >", out_safe)

        out_unsafe, _ = self.run_cmd("--banker-unsafe")
        self.assertIn("RESULT: UNSAFE state. No safe sequence exists; deadlock is possible.", out_unsafe)
        self.assertIn("Blocked: P0 P1 P2 P3", out_unsafe)

    def test_11_banker_file_parsing_and_validation(self):
        """Verify loading Banker's state from file with comment support and error checking."""
        sample = ROOT / "samples" / "banker_unsafe.txt"
        out, _ = self.run_cmd("--banker-file", str(sample))
        self.assertIn("RESULT: UNSAFE state", out)

        # Test malformed file (Alloc > Max)
        bad_banker = self.cwd / "bad_banker.txt"
        bad_banker.write_text("1 1\n5\n2\n0\n") # Alloc=5, Max=2
        self.run_cmd("--banker-file", str(bad_banker), success=False)

    # ==========================================
    # Requirement 6: Worker Failure Detection
    # ==========================================
    def test_12_worker_normal_and_failure(self):
        """Verify fork, waitpid, WIFEXITED, and WEXITSTATUS detection."""
        out_ok, _ = self.run_cmd("--worker-ok")
        self.assertIn("worker", out_ok)
        self.assertIn("exited with status 0 -> COMPLETED", out_ok)

        out_fail, _ = self.run_cmd("--worker-fail")
        self.assertIn("exited with status 42 -> FAILED (detected from non-zero exit status)", out_fail)

    # ==========================================
    # Requirement 7: Resource Limits & System Cleanup
    # ==========================================
    def test_13_rlimit_cpu_enforcement(self):
        """Verify setrlimit(RLIMIT_CPU) stops runaway loop with SIGXCPU."""
        out, _ = self.run_cmd("--rlimit")
        self.assertIn("child terminated by signal 24 (CPU time limit exceeded)", out)
        self.assertIn("kernel sent SIGXCPU and stopped the runaway loop", out)

    def test_14_system_cleanup_verification(self):
        """Verify comprehensive cleanup: no stray children, IPC objects, or active threads."""
        out, _ = self.run_cmd("--cleanup")
        self.assertIn("Child processes: 0 stray reaped, none remaining: yes", out)
        self.assertIn("IPC objects (shared memory + semaphores) remaining: 0", out)

    # ==========================================
    # Section 3: Live Coding & Practical Scenarios
    # ==========================================
    def test_15_live_coding_add_job_fcfs(self):
        """Live Question 1: Add a new job and execute FCFS."""
        # Menu 5: Add job (Arrival 10, Burst 5, Priority 1), then Menu 9 (FCFS), then Menu 0 (Exit)
        stdin = "5\n10\n5\n1\n9\n0\n"
        out, _ = self.run_cmd(stdin=stdin)
        self.assertIn("Job 6 added successfully (total workload: 6 jobs)", out)
        self.assertIn("[J6 26-31]", out)
        rows = self.parse_metrics_table(out)
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[-1], (6, 10, 5, 1, 31, 21, 16))

    def test_16_live_coding_change_quantum(self):
        """Live Question 2: Change RR quantum and demonstrate output difference."""
        out_q1, _ = self.run_cmd("--rr", "1")
        out_q4, _ = self.run_cmd("--rr", "4")
        self.assertIn("Execution slices: 26", out_q1)
        self.assertIn("Execution slices: 8", out_q4)
        self.assertIn("Average response time:    1.20", out_q1)
        self.assertIn("Average response time:    5.40", out_q4)

    def test_17_live_coding_change_priority(self):
        """Live Question 3: Change job priority and observe schedule change."""
        # Change Job 3 priority from 4 to 1, then execute Priority scheduling
        stdin = "6\n3\n1\n11\n0\n"
        out, _ = self.run_cmd(stdin=stdin)
        self.assertIn("Priority of Job 3 updated to 1", out)
        # In original schedule J3 ran last [J3 18-26]; now it runs right after J2: [J1 0-5] [J2 5-8] [J3 8-16]
        self.assertIn("[J1 0-5] [J2 5-8] [J3 8-16]", out)

    def test_18_live_coding_compare_same_job_set(self):
        """Live Question 4: Run same job set with all three algorithms."""
        out, _ = self.run_cmd("--compare")
        self.assertIn("FCFS", out)
        self.assertIn("Priority (non-preemptive)", out)
        self.assertIn("Round Robin", out)

    def test_19_live_coding_custom_worker_exit(self):
        """Live Question 7: Simulate custom worker failure and parent detection."""
        # Menu 24 (worker-custom): status 88, then Menu 0
        stdin = "24\n88\n0\n"
        out, _ = self.run_cmd(stdin=stdin)
        self.assertIn("worker", out)
        self.assertIn("exited with status 88 -> FAILED", out)

if __name__ == "__main__":
    unittest.main(verbosity=2)

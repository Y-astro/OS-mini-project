"""Regression checks against the compiled C program. No third-party packages."""
import os
import pathlib
import re
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BIN = ROOT / "campuscompute"

class CampusCompute(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = pathlib.Path(self.tmp.name)

    def run_cli(self, *args, success=True, stdin=None):
        p = subprocess.run([str(BIN), *args], cwd=self.cwd, input=stdin,
                           text=True, capture_output=True, timeout=30,
                           env={**os.environ, "NO_COLOR": "1"})
        self.assertEqual(p.returncode == 0, success, p.stdout + p.stderr)
        return p.stdout

    def metrics(self, out):
        return [(int(a), int(c), int(t), int(w))
                for a,c,t,w in re.findall(
                    r"(?m)^\|\s*(\d+)\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", out)]

    def test_default_metrics(self):
        cases = [
            (["--fcfs"], [(1,5,5,0),(2,8,7,4),(3,16,14,6),(4,22,19,13),(5,26,22,18)]),
            (["--priority"], [(1,5,5,0),(2,8,7,4),(3,26,24,16),(4,14,11,5),(5,18,14,10)]),
            (["--rr","2"], [(1,16,16,11),(2,13,12,9),(3,26,24,16),(4,24,21,15),(5,20,16,12)]),
            (["--rr","4"], [(1,20,20,15),(2,7,6,3),(3,24,22,14),(4,26,23,17),(5,19,15,11)])
        ]
        for args, expected in cases:
            with self.subTest(args=args):
                self.assertEqual(self.metrics(self.run_cli(*args)), expected)

    def test_idle_and_ties(self):
        p = self.cwd / "jobs.txt"
        p.write_text("3 4 2\n3 2 2\n10 1 1\n")
        out = self.run_cli("--jobs", str(p), "--rr", "100")
        self.assertIn("[IDLE 0-3]", out)
        self.assertIn("[IDLE 9-10]", out)
        self.assertEqual(self.metrics(out), [(1,7,4,0),(2,9,6,4),(3,11,1,0)])
        self.assertEqual(self.metrics(out), self.metrics(self.run_cli("--jobs",str(p),"--priority")))

    def test_invalid_arguments(self):
        for args in [("--rr","4abc"),("--rr","0"),("--random","5x"),
                     ("--jobs",),("--unknown",),("--fcfs","garbage")]:
            with self.subTest(args=args):
                self.run_cli(*args,success=False)
        p = self.cwd / "bad.txt"
        p.write_text("0 5 1\ninvalid\n")
        self.run_cli("--jobs",str(p),success=False)
        p.write_text("1 1\n0\n1\n0\nextra\n")
        self.run_cli("--banker-file",str(p),success=False)

    def test_trace_logging(self):
        out = self.run_cli("--trace","--log-schedule","--rr","2")
        self.assertIn("RUNNING -> READY",out)
        self.assertIn("ready queue:",out)
        log = (self.cwd / "campuscompute.log").read_text()
        self.assertEqual(log.count("completed (CT="),5)
        self.assertIn("quantum expired",log)

    def test_os_modules(self):
        self.assertIn("SAFE state. Safe sequence",self.run_cli("--banker-safe"))
        self.assertIn("UNSAFE state",self.run_cli("--banker-unsafe"))
        self.assertIn("FAILED",self.run_cli("--worker-fail"))
        self.assertIn("COMPLETED",self.run_cli("--worker-ok"))
        self.run_cli("--logger")
        self.assertEqual(len((self.cwd / "campuscompute.log").read_text().splitlines()),17)
        self.assertIn("remaining: 0",self.run_cli("--ipc","--ipc","--cleanup"))
        self.assertIn("SIGXCPU",self.run_cli("--rlimit"))

if __name__ == "__main__":
    unittest.main(verbosity=2)

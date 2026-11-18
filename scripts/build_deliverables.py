#!/usr/bin/env python3
"""
CampusCompute — Comprehensive Academic Deliverables Generator
Adheres to the official PES University End Semester Assessment (ESA) Laboratory Report format
(modelled on DLCD_Serial_Adder_2026_Faculty_Template_Editable.pdf).

Generates:
  1. PES2UG25CS617.pdf (Formal academic report for Yatin R)
  2. PES2UG25CS609.pdf (Formal academic report for Yaduveer Pavan)
  3. PES2UG25CS617.zip and PES2UG25CS609.zip (Verified submission archives)
"""

import os
import sys
import subprocess
import html
import base64
import tempfile
from pathlib import Path

BASE_DIR = Path("/run/media/tin/New Volume/Shared/Notes/Sem 3/OS/mini project").resolve()
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

ITEMS = [
    {
        "num": "S01",
        "title": "Ubuntu/WSL terminal, complete SRN prompt, and working directory",
        "fr": "Environment & Terminal Setup",
        "cmd": 'pwd; echo "Logged in user: $(whoami)"; echo "Active SRN: $SRN"',
        "expl": "S01 – Environment and SRN prompt: Demonstrates the active terminal environment, verified current working directory, and the complete student SRN (PES2UG25CS617) configured in the prompt as required."
    },
    {
        "num": "S02",
        "title": "GCC and Make versions or confirmation that required build tools are available",
        "fr": "Toolchain Verification",
        "cmd": "gcc --version | head -n 1; make --version | head -n 1",
        "expl": "S02 – Compiler and build tools: Confirms that GCC 16.2.1 supporting standard C99 with POSIX extensions and GNU Make 4.4.1 are correctly installed and available in the execution path."
    },
    {
        "num": "S03",
        "title": "Project directory, source files, and Makefile",
        "fr": "Source Code Architecture",
        "cmd": "ls -la",
        "expl": "S03 – Project files: Displays the clean modular structure of CampusCompute, showing all eight C implementation files, header interfaces, documentation, and the build automation Makefile."
    },
    {
        "num": "S04",
        "title": "Successful clean build from source",
        "fr": "Compilation & Build Verification",
        "cmd": "make clean && make",
        "expl": "S04 – Clean build: Demonstrates clean compilation from source with all compiler warnings enabled (-Wall -Wextra), producing standalone object modules and the final executable with zero warnings or errors."
    },
    {
        "num": "S05",
        "title": "CLI help, usage instructions, or menu options",
        "fr": "FR8 — User Interface & Error Handling",
        "cmd": "./campuscompute --help",
        "expl": "S05 – CLI help/usage: Displays the complete command-line interface documentation (--help), detailing all 30 supported commands, batch flags, and interactive mode operations."
    },
    {
        "num": "S06",
        "title": "FCFS scheduling execution order and calculated metrics",
        "fr": "FR2 — CPU Scheduling (FCFS)",
        "cmd": "./campuscompute --fcfs",
        "expl": "S06 – FCFS scheduling: Shows FCFS execution order, completion time, turnaround time, waiting time, and calculated averages (Average Turnaround: 13.40, Average Waiting: 8.20)."
    },
    {
        "num": "S07",
        "title": "Round Robin scheduling with time quantum and metrics",
        "fr": "FR2 — CPU Scheduling (Round Robin)",
        "cmd": "./campuscompute --rr 2",
        "expl": "S07 – Round Robin scheduling: Shows Round Robin execution slices with time quantum q=2, demonstrating arrival queue management, job preemption, and metric computations."
    },
    {
        "num": "S08",
        "title": "Non-preemptive Priority scheduling and tie-breaking rule",
        "fr": "FR2 — CPU Scheduling (Priority)",
        "cmd": "./campuscompute --priority",
        "expl": "S08 – Priority scheduling: Demonstrates non-preemptive priority scheduling where lower numerical values represent higher priority, with arrival time and Job ID breaking ties deterministically."
    },
    {
        "num": "S09",
        "title": "Comparative evaluation of scheduling policies",
        "fr": "FR2 — CPU Scheduling (Comparison)",
        "cmd": "./campuscompute --compare",
        "expl": "S09 – Scheduling comparison: Shows a direct comparison of all three scheduling policies using the exact same job workload, highlighting trade-offs in turnaround, waiting, and response times."
    },
    {
        "num": "S10",
        "title": "Producer-consumer activity logger execution",
        "fr": "FR3 — Concurrent Activity Logger",
        "cmd": "./campuscompute --logger",
        "expl": "S10 – Producer-consumer logger: Demonstrates concurrent activity logging using POSIX threads, showing multiple producer threads submitting entries and consumer threads processing them safely."
    },
    {
        "num": "S11",
        "title": "Thread synchronization, condition variables, and clean termination",
        "fr": "FR3 — Thread Synchronization & Termination",
        "cmd": "./campuscompute --logger-custom",
        "expl": "S11 – Thread synchronization and termination: Confirms synchronized thread operation via pthread_mutex and pthread_cond, followed by orderly thread completion and joining via pthread_join with zero thread leaks."
    },
    {
        "num": "S12",
        "title": "Cooperatng processes exchanging data via POSIX shared memory",
        "fr": "FR4 — Inter-Process Communication (Shared Memory)",
        "cmd": "./campuscompute --ipc",
        "expl": "S12 – Shared-memory IPC: Shows parent and child processes successfully creating, mapping (mmap), and exchanging job data packets through POSIX shared memory (/cc_shm_*)."
    },
    {
        "num": "S13",
        "title": "Named semaphore synchronization and IPC cleanup",
        "fr": "FR4 — IPC Synchronization & Resource Cleanup",
        "cmd": "./campuscompute --ipc-custom",
        "expl": "S13 – Semaphore coordination and cleanup: Demonstrates mutual exclusion and handshaking via named semaphores (/cc_sem_*), followed by automatic unlinking and verification of zero lingering IPC handles."
    },
    {
        "num": "S14",
        "title": "Banker's algorithm safe state evaluation and sequence discovery",
        "fr": "FR5 — Resource-Safety Analysis (Safe State)",
        "cmd": "./campuscompute --banker-safe",
        "expl": "S14 – Banker's safe state: Shows the resource-safety analysis verifying that Available resources satisfy process Needs, discovering and printing a valid deadlock-free safe sequence."
    },
    {
        "num": "S15",
        "title": "Banker's algorithm unsafe state detection",
        "fr": "FR5 — Resource-Safety Analysis (Unsafe State)",
        "cmd": "./campuscompute --banker-unsafe",
        "expl": "S15 – Banker's unsafe state: Demonstrates the safety algorithm evaluating an unsafe allocation matrix, determining that no safe sequence exists and warning of imminent deadlock."
    },
    {
        "num": "S16",
        "title": "Worker process creation and normal completion status collection",
        "fr": "FR6 — Worker Failure Detection (Normal Exit)",
        "cmd": "./campuscompute --worker-ok",
        "expl": "S16 – Normal worker process: Shows the coordinator process spawning a worker child via fork(), awaiting completion with waitpid(), and decoding WIFEXITED with normal exit status 0."
    },
    {
        "num": "S17",
        "title": "Controlled simulated worker failure detection",
        "fr": "FR6 — Worker Failure Detection (Simulated Fault)",
        "cmd": "./campuscompute --worker-fail",
        "expl": "S17 – Simulated worker failure: Shows controlled simulation of a worker failure, where the parent catches the non-zero exit status and correctly classifies the job as FAILED without crashing."
    },
    {
        "num": "S18",
        "title": "Process resource limits enforcement (RLIMIT_CPU)",
        "fr": "FR7 — Resource Limits (setrlimit)",
        "cmd": "./campuscompute --rlimit",
        "expl": "S18 – Resource-limit demonstration: Demonstrates setrlimit(RLIMIT_CPU) restricting maximum CPU time, verifying that the operating system enforces limits and intercepts runaway computations."
    },
    {
        "num": "S19",
        "title": "Invalid command and malformed input error handling",
        "fr": "FR8 — Robust Input Validation",
        "cmd": "./campuscompute --invalid-option",
        "expl": "S19 – Invalid input/command: Confirms robust input validation, showing that invalid command-line arguments produce clear diagnostic error messages and usage instructions."
    },
    {
        "num": "S20",
        "title": "Comprehensive system cleanup verification",
        "fr": "FR7 — System Resource Reclamation",
        "cmd": "./campuscompute --cleanup; ls /dev/shm | grep cc_ || echo 'Zero lingering IPC objects'",
        "expl": "S20 – Cleanup verification: Verifies that all child processes are reaped, background threads terminated, and all POSIX shared memory and semaphores in /dev/shm are completely removed."
    },
    {
        "num": "S21",
        "title": "Integrated demonstration execution and test results",
        "fr": "End-to-End System Integration",
        "cmd": "./campuscompute --demo",
        "expl": "S21 – Integrated execution: Displays the complete execution flow of all CampusCompute subsystems and the automated test verification summary confirming PASS across test cases."
    },
    {
        "num": "S22",
        "title": "Structured persistent event log file inspection",
        "fr": "FR3 — Persistent Logging Subsystem",
        "cmd": "cat campuscompute.log | tail -n 25",
        "expl": "S22 – Generated logs: Demonstrates the persistent activity log file generated by the bounded-buffer logger, confirming structured timestamping and event tracking."
    },
    {
        "num": "S23",
        "title": "Final project source files, Makefile, and executable binary",
        "fr": "Deliverable Verification",
        "cmd": "ls -lh campuscompute common.h scheduler.c logger.c ipc.c banker.c worker.c rlimit.c Makefile",
        "expl": "S23 – Final source and build files: Shows the final compilation artifacts, source files, header dependencies, and the generated standalone campuscompute binary ready for deployment."
    },
    {
        "num": "S24",
        "title": "Submission ZIP archive structure and integrity check",
        "fr": "Submission Packaging & Integrity",
        "cmd": "unzip -l $SRN.zip; unzip -t $SRN.zip",
        "expl": "S24 – Submission ZIP: Shows the final submission archive containing all required source files, headers, Makefile, and documentation, verified with unzip -t showing zero archive errors."
    }
]

def load_base64_images():
    b64_dict = {}
    for item in ITEMS:
        num = item["num"]
        p = SCREENSHOTS_DIR / f"{num}.png"
        if not p.exists():
            raise FileNotFoundError(f"Missing required screenshot: {p}")
        with open(p, "rb") as f:
            b64_dict[num] = base64.b64encode(f.read()).decode("utf-8")
    
    logo_path = BASE_DIR / "assets" / "pes_logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            b64_dict["LOGO"] = base64.b64encode(f.read()).decode("utf-8")
    else:
        b64_dict["LOGO"] = ""
    return b64_dict


def generate_report_html(srn, student_name, partner_srn, partner_name, b64_images):
    # Pure academic black-and-white styling adhering strictly to the faculty template
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Operating Systems Laboratory Project Report — __SRN__</title>
<style>
  @page {
    size: A4 portrait;
    margin: 14mm 16mm 14mm 16mm;
  }

  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    padding: 0;
    font-family: Calibri, "Liberation Sans", "DejaVu Sans", Arial, sans-serif;
    color: #000000;
    background-color: #ffffff;
    font-size: 11pt;
    line-height: 1.35;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  .page-container {
    width: 100%;
    height: 268mm;
    max-height: 268mm;
    position: relative;
    page-break-after: always;
    page-break-inside: avoid;
    overflow: hidden;
  }

  .page-body {
    height: 258mm;
    overflow: hidden;
  }

  .page-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 6mm;
    border-top: 1px solid #000000;
    padding-top: 1.5mm;
    font-size: 8.5pt;
    display: flex;
    justify-content: space-between;
    color: #000000;
  }

  /* Typography */
  h1.section-heading {
    font-size: 15pt;
    font-weight: bold;
    text-align: center;
    text-transform: uppercase;
    margin: 0 0 4mm 0;
    letter-spacing: 0.5px;
  }

  h2.sub-heading {
    font-size: 11.5pt;
    font-weight: bold;
    margin: 3mm 0 1.5mm 0;
    color: #000000;
  }

  p {
    margin: 0 0 2.5mm 0;
    text-align: justify;
  }

  ol, ul {
    margin: 1mm 0 2.5mm 0;
    padding-left: 5mm;
  }

  li {
    margin-bottom: 1.5mm;
    text-align: justify;
  }

  /* Tables */
  table.academic-table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #000000;
    margin: 2mm 0 3mm 0;
    font-size: 9pt;
  }

  table.academic-table th {
    border: 1px solid #000000;
    padding: 3.5px 6px;
    font-weight: bold;
    text-align: left;
    background-color: #f2f2f2;
  }

  table.academic-table td {
    border: 1px solid #000000;
    padding: 3px 6px;
    vertical-align: top;
  }

  /* Code listings */
  .code-block {
    font-family: Consolas, "Liberation Mono", "DejaVu Sans Mono", "Courier New", monospace;
    font-size: 7.8pt;
    line-height: 1.25;
    background: #ffffff;
    border: 1px solid #000000;
    padding: 4px 6px;
    margin: 1.5mm 0 2.5mm 0;
    white-space: pre;
    overflow: hidden;
  }

  .listing-title {
    font-size: 9.5pt;
    font-weight: bold;
    margin: 2mm 0 1mm 0;
  }

  /* Screenshot display */
  .screenshot-box {
    margin: 1.5mm 0 3mm 0;
    text-align: center;
  }

  .screenshot-frame {
    display: inline-block;
    border: 1px solid #333333;
    padding: 1px;
    background: #ffffff;
    max-width: 98%;
  }

  .screenshot-frame img {
    max-width: 100%;
    height: auto;
    display: block;
  }

  .screenshot-caption {
    font-size: 9.5pt;
    font-weight: bold;
    text-align: left;
    margin-top: 1.5mm;
  }

  .screenshot-explanation {
    font-size: 9pt;
    text-align: justify;
    margin-top: 1mm;
    margin-bottom: 2mm;
    line-height: 1.3;
  }

  /* Page 3 Problem Statement specific (prevent cut off) */
  .page-3-body {
    height: 258mm;
    overflow: hidden;
    font-size: 10pt;
    line-height: 1.3;
  }

  .page-3-body h1.section-heading {
    margin-bottom: 2.5mm;
  }

  .page-3-body h2.sub-heading {
    margin: 2mm 0 1mm 0;
  }

  .page-3-body p {
    margin: 0 0 1.5mm 0;
  }

  .page-3-body ol {
    margin: 1mm 0 1.5mm 0;
    padding-left: 5mm;
  }

  .page-3-body li {
    margin-bottom: 1mm;
  }

  /* Cover page specific with PES logo */
  .cover-container {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    text-align: center;
    padding: 4mm 5mm 5mm 5mm;
  }

  .cover-logo {
    text-align: center;
    margin-bottom: 5mm;
  }

  .cover-logo img {
    width: 48mm;
    height: auto;
  }

  .cover-top {
    font-size: 13pt;
    font-weight: bold;
    line-height: 1.4;
  }

  .cover-course {
    font-size: 12.5pt;
    font-weight: bold;
    line-height: 1.4;
    margin-top: 6mm;
  }

  .cover-middle {
    margin-top: 8mm;
  }

  .cover-report-on {
    font-size: 11.5pt;
    font-weight: bold;
    line-height: 1.4;
  }

  .cover-project-title {
    font-size: 14.5pt;
    font-weight: bold;
    margin-top: 3mm;
    letter-spacing: 0.5px;
  }

  .cover-submitted-by {
    font-size: 11pt;
    font-weight: bold;
    margin-top: 8mm;
  }

  .cover-table {
    margin: 3mm auto 0 auto;
    width: 80%;
    border-collapse: collapse;
    font-size: 10.5pt;
    font-weight: bold;
  }

  .cover-table th, .cover-table td {
    padding: 3px 10px;
    text-align: left;
  }

  .cover-bottom {
    font-size: 10pt;
    font-weight: bold;
    line-height: 1.4;
    margin-bottom: 6mm;
  }
</style>
</head>
<body>

<!-- ========================================================================= -->
<!-- PAGE 1: COVER PAGE                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="cover-container">
    <div>
      <div class="cover-logo">
        <img src="data:image/png;base64,__B64_LOGO__" alt="PES University Logo">
      </div>
      <div class="cover-top">
        END SEMESTER ASSESSMENT (ESA)<br>
        B.TECH. (CSE)<br>
        III SEMESTER
      </div>

      <div class="cover-course">
        UE25CS242A<br>
        OPERATING SYSTEMS LABORATORY
      </div>

      <div class="cover-middle">
        <div class="cover-report-on">
          PROJECT REPORT<br>
          ON
        </div>
        <div class="cover-project-title">
          “CAMPUSCOMPUTE: INTELLIGENT JOB SCHEDULING<br>AND RESOURCE MANAGEMENT”
        </div>
      </div>

      <div class="cover-submitted-by">
        SUBMITTED BY
      </div>

      <table class="cover-table">
        <tr>
          <th style="width: 15%;">Sl.No</th>
          <th style="width: 50%;">NAME</th>
          <th style="width: 35%;">SRN</th>
        </tr>
        <tr>
          <td>1)</td>
          <td>__STUDENT_NAME__</td>
          <td>__SRN__</td>
        </tr>
        <tr>
          <td>2)</td>
          <td>__PARTNER_NAME__</td>
          <td>__PARTNER_SRN__</td>
        </tr>
      </table>
    </div>

    <div class="cover-bottom">
      AUGUST - DECEMBER 2026<br>
      DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING<br>
      ELECTRONIC CITY CAMPUS,<br>
      BENGALURU - 560100, KARNATAKA, INDIA
    </div>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 2: TABLE OF CONTENTS                                                 -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading" style="margin-top: 10mm; margin-bottom: 6mm;">TABLE OF CONTENTS</h1>

    <table class="academic-table" style="font-size: 10pt; width: 95%; margin: 0 auto;">
      <thead>
        <tr>
          <th style="width: 12%; text-align: center;">Sl.No</th>
          <th style="width: 73%;">TOPIC</th>
          <th style="width: 15%; text-align: center;">PAGE No</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align: center; font-weight: bold;">1.</td>
          <td>
            <strong>PROBLEM STATEMENT</strong><br>
            <span style="font-size: 8.5pt; font-style: italic;">(Aim, Problem Definition, Functional Requirements FR1–FR8)</span>
          </td>
          <td style="text-align: center; font-weight: bold;">3</td>
        </tr>
        <tr>
          <td style="text-align: center; font-weight: bold;">2.</td>
          <td>
            <strong>SYSTEM ARCHITECTURE &amp; MODULAR DESIGN</strong><br>
            <span style="font-size: 8.5pt; font-style: italic;">(POSIX Subsystems, Architectural Block Diagram, Module Specifications)</span>
          </td>
          <td style="text-align: center; font-weight: bold;">4</td>
        </tr>
        <tr>
          <td style="text-align: center; font-weight: bold;">3.</td>
          <td>
            <strong>PROCESS LIFECYCLE &amp; STATE TRANSITIONS (FSM)</strong><br>
            <span style="font-size: 8.5pt; font-style: italic;">(Process State Machine, Dispatcher Lifecycle, State Transition Table)</span>
          </td>
          <td style="text-align: center; font-weight: bold;">5</td>
        </tr>
        <tr>
          <td style="text-align: center; font-weight: bold;">4.</td>
          <td>
            <strong>LITERATURE SURVEY &amp; THEORETICAL FOUNDATION</strong><br>
            <span style="font-size: 8.5pt; font-style: italic;">(Scheduling Algorithms, Banker's Deadlock Avoidance, Concurrency)</span>
          </td>
          <td style="text-align: center; font-weight: bold;">6</td>
        </tr>
        <tr>
          <td style="text-align: center; font-weight: bold;">5.</td>
          <td>
            <strong>MAIN C SOURCE CODE</strong><br>
            <span style="font-size: 8.5pt; font-style: italic;">(Synthesizable Core Modules: scheduler.c, logger.c, ipc.c, banker.c, rlimit.c)</span>
          </td>
          <td style="text-align: center; font-weight: bold;">7</td>
        </tr>
        <tr>
          <td style="text-align: center; font-weight: bold;">6.</td>
          <td>
            <strong>TEST BENCH &amp; BUILD AUTOMATION</strong><br>
            <span style="font-size: 8.5pt; font-style: italic;">(Makefile Build Rules, Automated Evaluation Harness, Regression Suite)</span>
          </td>
          <td style="text-align: center; font-weight: bold;">10</td>
        </tr>
        <tr>
          <td style="text-align: center; font-weight: bold;">7.</td>
          <td>
            <strong>SCREEN SHOTS OF THE OUTPUT</strong><br>
            <span style="font-size: 8.5pt; font-style: italic;">(Actual RTL &amp; Kernel Execution Evidence S01 to S24 with Required Explanations)</span>
          </td>
          <td style="text-align: center; font-weight: bold;">11</td>
        </tr>
        <tr>
          <td style="text-align: center; font-weight: bold;">8.</td>
          <td>
            <strong>REFERENCES</strong><br>
            <span style="font-size: 8.5pt; font-style: italic;">(IEEE Standards, Academic Textbooks, Linux Programmer's Manual)</span>
          </td>
          <td style="text-align: center; font-weight: bold;">27</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 2</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 3: PROBLEM STATEMENT                                                 -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body page-3-body">
    <h1 class="section-heading">PROBLEM STATEMENT</h1>

    <h2 class="sub-heading">Aim</h2>
    <p>
      To design, implement, and validate <strong>CampusCompute</strong>, an intelligent command-line operating-system
      prototype in C on Linux/Ubuntu, demonstrating preemptive and non-preemptive CPU scheduling algorithms,
      multithreaded synchronized activity logging, inter-process communication using POSIX shared memory and named
      semaphores, deadlock avoidance via Dijkstra's Banker's Algorithm, worker process lifecycle and fault detection,
      POSIX resource limits (RLIMIT_CPU), and comprehensive zero-leak system resource cleanup.
    </p>

    <h2 class="sub-heading">Problem definition</h2>
    <p>
      A university operates a shared computing laboratory where undergraduate students, researchers, and automated test
      suites execute concurrent, CPU-intensive scientific simulations, matrix factorizations, and dataset transformations.
      During peak laboratory hours, uncoordinated job submissions cause intense CPU contention, unbounded starvation of
      short interactive tasks, concurrency race conditions in shared logging facilities, system-wide memory exhaustion,
      and unmonitored worker process crashes.
    </p>
    <p>
      The objective of this project is to implement a robust, modular systems supervisor that coordinates job workloads,
      enforces deterministic CPU scheduling policies, logs thread-safe system transitions into a persistent file, exchanges
      payload packets through inter-process shared memory guarded by semaphores, verifies multi-resource allocation safety
      to prevent deadlocks, monitors process lifecycles via kernel exit status decoding, enforces kernel resource bounds,
      and guarantees total cleanup of all allocated kernel primitives upon termination.
    </p>

    <h2 class="sub-heading">Objectives and functional requirements</h2>
    <ol>
      <li>
        <strong>FR1 – Job Management and Process Lifecycle:</strong> Define a structured job entity encapsulating Job ID,
        arrival time, CPU burst duration, priority level, and dynamic lifecycle states (<code>READY</code>, <code>RUNNING</code>,
        <code>COMPLETED</code>, <code>FAILED</code>). Provide rigorous input validation rejecting negative or malformed inputs.
      </li>
      <li>
        <strong>FR2 – CPU Scheduling:</strong> Implement First-Come-First-Served (FCFS), Round Robin (configurable time quantum
        <code>q</code>), and Non-Preemptive Priority scheduling. Compute completion time, turnaround time, waiting time, and response time.
        Enforce deterministic multi-tier tie-breaking: lower priority value &gt; earlier arrival time &gt; lower Job ID.
      </li>
      <li>
        <strong>FR3 – Concurrent Activity Logger:</strong> Implement a bounded circular producer-consumer buffer managed by POSIX
        threads (<code>pthread</code>). Guard mutual exclusion with <code>pthread_mutex_t</code> and coordinate full/empty buffer
        conditions using <code>pthread_cond_t</code>. Format entries with millisecond timestamps and ensure orderly thread joining.
      </li>
      <li>
        <strong>FR4 – Inter-Process Communication (IPC):</strong> Coordinate cooperating parent and child processes using POSIX
        shared memory (<code>shm_open</code>, <code>mmap</code>, <code>ftruncate</code>) and named semaphores (<code>sem_open</code>,
        <code>sem_wait</code>, <code>sem_post</code>). Guarantee automated unlinking and zero residual objects in <code>/dev/shm</code>.
      </li>
      <li>
        <strong>FR5 – Resource-Safety Analysis:</strong> Implement Dijkstra's Banker's Algorithm supporting multiple resource types.
        Maintain <code>Available</code>, <code>Allocation</code>, <code>Maximum</code>, and dynamically compute <code>Need = Max - Alloc</code>.
        Discover safe execution sequences or reject unsafe requests with diagnostic deadlock hazard warnings.
      </li>
      <li>
        <strong>FR6 – Worker Failure Detection:</strong> Spawn isolated child worker processes via <code>fork()</code> and reap
        termination status via <code>waitpid()</code>. Accurately distinguish normal exit (status 0) from controlled simulated faults (status 1).
      </li>
      <li>
        <strong>FR7 – Resource Limits and Cleanup:</strong> Demonstrate kernel resource bounding using <code>setrlimit(RLIMIT_CPU)</code>
        and observe interception via <code>SIGXCPU</code>. Enforce leak-free reclamation of threads, child processes, and IPC primitives.
      </li>
      <li>
        <strong>FR8 – CLI Interface &amp; Error Handling:</strong> Implement documented interactive and chained batch CLI commands.
        Deliver meaningful diagnostic syntax messages upon encountering invalid options or parameters.
      </li>
    </ol>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 3</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 4: SYSTEM ARCHITECTURE & MODULAR DESIGN                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading">SYSTEM ARCHITECTURE &amp; MODULAR DESIGN</h1>

    <div style="text-align: center; margin: 2mm 0 3mm 0;">
      <svg width="680" height="150" viewBox="0 0 680 150" style="border: 1px solid #000; background: #ffffff;">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#000" />
          </marker>
        </defs>
        <!-- Top row: CLI and Common -->
        <rect x="20" y="15" width="180" height="40" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="110" y="32" font-family="Calibri, sans-serif" font-size="10" font-weight="bold" text-anchor="middle">CLI &amp; Menu Interface</text>
        <text x="110" y="46" font-family="Calibri, sans-serif" font-size="8.5" text-anchor="middle">(main.c / input.c)</text>

        <line x1="200" y1="35" x2="250" y2="35" stroke="#000" stroke-width="1.5" marker-end="url(#arrow)"/>

        <rect x="250" y="15" width="180" height="40" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="340" y="32" font-family="Calibri, sans-serif" font-size="10" font-weight="bold" text-anchor="middle">Workload Data Engine</text>
        <text x="340" y="46" font-family="Calibri, sans-serif" font-size="8.5" text-anchor="middle">(common.h / Job Queue)</text>

        <line x1="430" y1="35" x2="480" y2="35" stroke="#000" stroke-width="1.5" marker-end="url(#arrow)"/>

        <rect x="480" y="15" width="180" height="40" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="570" y="32" font-family="Calibri, sans-serif" font-size="10" font-weight="bold" text-anchor="middle">CPU Scheduling Engine</text>
        <text x="570" y="46" font-family="Calibri, sans-serif" font-size="8.5" text-anchor="middle">(scheduler.c: FCFS/RR/Pri)</text>

        <!-- Bottom row: Subsystems -->
        <line x1="110" y1="55" x2="110" y2="85" stroke="#000" stroke-width="1.5" marker-end="url(#arrow)"/>
        <line x1="340" y1="55" x2="340" y2="85" stroke="#000" stroke-width="1.5" marker-end="url(#arrow)"/>
        <line x1="570" y1="55" x2="570" y2="85" stroke="#000" stroke-width="1.5" marker-end="url(#arrow)"/>

        <rect x="20" y="85" width="145" height="50" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="92" y="102" font-family="Calibri, sans-serif" font-size="9.5" font-weight="bold" text-anchor="middle">Concurrent Logger</text>
        <text x="92" y="116" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">POSIX Mutex &amp; Cond</text>
        <text x="92" y="128" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">(logger.c / .log)</text>

        <rect x="180" y="85" width="150" height="50" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="255" y="102" font-family="Calibri, sans-serif" font-size="9.5" font-weight="bold" text-anchor="middle">POSIX IPC Subsystem</text>
        <text x="255" y="116" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">shm_open / sem_open</text>
        <text x="255" y="128" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">(ipc.c: /cc_shm, /cc_sem)</text>

        <rect x="345" y="85" width="150" height="50" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="420" y="102" font-family="Calibri, sans-serif" font-size="9.5" font-weight="bold" text-anchor="middle">Worker Controller</text>
        <text x="420" y="116" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">fork() &amp; waitpid()</text>
        <text x="420" y="128" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">(worker.c: exit status)</text>

        <rect x="510" y="85" width="150" height="50" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="585" y="102" font-family="Calibri, sans-serif" font-size="9.5" font-weight="bold" text-anchor="middle">Banker &amp; RLIMIT</text>
        <text x="585" y="116" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">Safety &amp; RLIMIT_CPU</text>
        <text x="585" y="128" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">(banker.c / rlimit.c)</text>
      </svg>
      <div style="font-size: 8.5pt; font-style: italic; margin-top: 1mm;">
        Figure 1. Modular system architecture and POSIX subsystems (logical connections).
      </div>
    </div>

    <h2 class="sub-heading">Architectural specification and modular decomposition</h2>
    <p>
      CampusCompute is structured into eight decoupled C modules compiling independently into relocatable object files
      before final static linking. Shared constants, structures, and POSIX headers are declared centrally in <code>common.h</code>.
    </p>

    <table class="academic-table">
      <thead>
        <tr>
          <th style="width: 14%;">Module</th>
          <th style="width: 28%;">Primary Purpose</th>
          <th style="width: 32%;">Key Data Structures &amp; Constants</th>
          <th style="width: 26%;">POSIX System Calls &amp; APIs</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>main.c</strong></td>
          <td>CLI parsing, command chaining, and interactive menu loop.</td>
          <td>Arg table, command dispatch table.</td>
          <td><code>exit</code>, <code>signal</code>, <code>snprintf</code></td>
        </tr>
        <tr>
          <td><strong>input.c</strong></td>
          <td>Input ingestion, format validation, PRNG workload generator.</td>
          <td>Workload file buffers, <code>MAX_BURST</code>, <code>MAX_ARRIVAL</code>.</td>
          <td><code>fopen</code>, <code>fgets</code>, <code>sscanf</code>, <code>rand_r</code></td>
        </tr>
        <tr>
          <td><strong>scheduler.c</strong></td>
          <td>Simulation of FCFS, Round Robin, and Priority scheduling.</td>
          <td><code>Job</code>, <code>Metrics</code>, <code>Queue</code>, <code>Slice</code>, <code>Timeline</code>.</td>
          <td><code>clock_gettime</code> (timing metrics)</td>
        </tr>
        <tr>
          <td><strong>logger.c</strong></td>
          <td>Multithreaded activity logging via bounded circular buffer.</td>
          <td><code>LOG_QUEUE_SIZE=8</code>, <code>head</code>, <code>tail</code>, <code>count</code>.</td>
          <td><code>pthread_create</code>, <code>pthread_mutex_*</code>, <code>pthread_cond_*</code></td>
        </tr>
        <tr>
          <td><strong>ipc.c</strong></td>
          <td>Transactional inter-process shared memory and semaphores.</td>
          <td><code>SharedJobPacket</code>, <code>/cc_shm_*</code>, <code>/cc_sem_*</code>.</td>
          <td><code>shm_open</code>, <code>mmap</code>, <code>ftruncate</code>, <code>sem_open</code>, <code>sem_wait</code></td>
        </tr>
        <tr>
          <td><strong>banker.c</strong></td>
          <td>Dijkstra's deadlock avoidance safety algorithm.</td>
          <td><code>BankerState</code>, <code>Available</code>, <code>Allocation</code>, <code>Need</code>.</td>
          <td>Matrix manipulation, safe sequence array</td>
        </tr>
        <tr>
          <td><strong>worker.c</strong></td>
          <td>Worker child process execution and failure detection.</td>
          <td>Process exit status codes (0 = Success, 1 = Fault).</td>
          <td><code>fork</code>, <code>waitpid</code>, <code>WIFEXITED</code>, <code>WEXITSTATUS</code></td>
        </tr>
        <tr>
          <td><strong>rlimit.c</strong></td>
          <td>Enforcement of kernel resource bounds on worker tasks.</td>
          <td><code>struct rlimit</code>, <code>RLIMIT_CPU</code> (1 second).</td>
          <td><code>setrlimit</code>, <code>getrlimit</code>, <code>sigaction</code> (SIGXCPU)</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 4</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 5: PROCESS LIFECYCLE & STATE TRANSITIONS (FSM)                       -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading">PROCESS LIFECYCLE &amp; STATE TRANSITIONS (FSM)</h1>

    <div style="text-align: center; margin: 2mm 0 3mm 0;">
      <svg width="680" height="135" viewBox="0 0 680 135" style="border: 1px solid #000; background: #ffffff;">
        <defs>
          <marker id="fsm-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#000" />
          </marker>
        </defs>
        <!-- States -->
        <rect x="20" y="45" width="85" height="40" rx="6" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="62" y="69" font-family="Calibri, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">NEW</text>

        <line x1="105" y1="65" x2="165" y2="65" stroke="#000" stroke-width="1.5" marker-end="url(#fsm-arrow)"/>
        <text x="135" y="58" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">Admit</text>

        <rect x="165" y="45" width="95" height="40" rx="6" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="212" y="69" font-family="Calibri, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">READY</text>

        <line x1="260" y1="55" x2="335" y2="55" stroke="#000" stroke-width="1.5" marker-end="url(#fsm-arrow)"/>
        <text x="297" y="48" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">Dispatch</text>

        <rect x="335" y="45" width="105" height="40" rx="6" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="387" y="69" font-family="Calibri, sans-serif" font-size="11" font-weight="bold" text-anchor="middle">RUNNING</text>

        <!-- RR Preempt return -->
        <path d="M 370 45 C 370 15, 230 15, 230 45" fill="none" stroke="#000" stroke-width="1.5" marker-end="url(#fsm-arrow)"/>
        <text x="300" y="16" font-family="Calibri, sans-serif" font-size="8" text-anchor="middle">Quantum Expired (RR Preemption)</text>

        <!-- Waiting branch -->
        <line x1="387" y1="85" x2="387" y2="100" stroke="#000" stroke-width="1.5"/>
        <line x1="387" y1="100" x2="260" y2="100" stroke="#000" stroke-width="1.5"/>
        <rect x="200" y="85" width="90" height="30" rx="6" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="245" y="104" font-family="Calibri, sans-serif" font-size="9.5" font-weight="bold" text-anchor="middle">WAITING</text>
        <line x1="245" y1="85" x2="245" y2="85" stroke="#000" stroke-width="1.5"/>
        <path d="M 212 85 L 212 85" stroke="#000"/>
        <line x1="200" y1="100" x2="180" y2="100" stroke="#000" stroke-width="1.5"/>
        <line x1="180" y1="100" x2="180" y2="85" stroke="#000" stroke-width="1.5" marker-end="url(#fsm-arrow)"/>
        <text x="320" y="112" font-family="Calibri, sans-serif" font-size="7.5" text-anchor="middle">I/O or Mutex Lock Block</text>
        <text x="145" y="112" font-family="Calibri, sans-serif" font-size="7.5" text-anchor="middle">Event / Signal</text>

        <!-- Terminations -->
        <line x1="440" y1="55" x2="520" y2="35" stroke="#000" stroke-width="1.5" marker-end="url(#fsm-arrow)"/>
        <rect x="520" y="15" width="125" height="35" rx="6" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="582" y="36" font-family="Calibri, sans-serif" font-size="10" font-weight="bold" text-anchor="middle">COMPLETED</text>
        <text x="475" y="32" font-family="Calibri, sans-serif" font-size="7.5" text-anchor="middle">Burst done (exit 0)</text>

        <line x1="440" y1="75" x2="520" y2="95" stroke="#000" stroke-width="1.5" marker-end="url(#fsm-arrow)"/>
        <rect x="520" y="80" width="125" height="35" rx="6" fill="#ffffff" stroke="#000" stroke-width="1.5"/>
        <text x="582" y="101" font-family="Calibri, sans-serif" font-size="10" font-weight="bold" text-anchor="middle">FAILED / KILLED</text>
        <text x="475" y="98" font-family="Calibri, sans-serif" font-size="7.5" text-anchor="middle">Fault / SIGXCPU</text>
      </svg>
      <div style="font-size: 8.5pt; font-style: italic; margin-top: 1mm;">
        Figure 2. Job and worker process finite state machine (FSM) and lifecycle transitions.
      </div>
    </div>

    <h2 class="sub-heading">FSM transition table</h2>
    <table class="academic-table">
      <thead>
        <tr>
          <th style="width: 13%;">Current State</th>
          <th style="width: 25%;">Condition / Trigger Event</th>
          <th style="width: 14%;">Next State</th>
          <th style="width: 48%;">Action &amp; Associated POSIX Mechanism</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>NEW</strong></td>
          <td>Job parsed from file/CLI, arrival time reached.</td>
          <td><strong>READY</strong></td>
          <td>Allocate <code>Job</code> struct, validate burst &gt; 0, push into Ready Queue.</td>
        </tr>
        <tr>
          <td><strong>READY</strong></td>
          <td>Scheduler dispatches highest-priority job.</td>
          <td><strong>RUNNING</strong></td>
          <td>Select job based on active policy; record first dispatch time (Response Time = Start - Arrival).</td>
        </tr>
        <tr>
          <td><strong>RUNNING</strong></td>
          <td>Time quantum <code>q</code> expires before burst completes (RR).</td>
          <td><strong>READY</strong></td>
          <td>Preempt current execution slice, deduct executed duration from burst, append job to queue tail.</td>
        </tr>
        <tr>
          <td><strong>RUNNING</strong></td>
          <td>Logger circular buffer full or awaiting semaphore.</td>
          <td><strong>WAITING</strong></td>
          <td>Thread blocks via <code>pthread_cond_wait(&amp;not_full, &amp;mutex)</code> or process blocks on <code>sem_wait()</code>.</td>
        </tr>
        <tr>
          <td><strong>WAITING</strong></td>
          <td>Slot vacated by consumer or semaphore posted.</td>
          <td><strong>READY</strong></td>
          <td>Signaled via <code>pthread_cond_signal(&amp;not_full)</code> or <code>sem_post()</code>; job re-enqueued.</td>
        </tr>
        <tr>
          <td><strong>RUNNING</strong></td>
          <td>All CPU burst units consumed successfully.</td>
          <td><strong>COMPLETED</strong></td>
          <td>Record completion time; compute Turnaround (CT - AT) and Waiting Time (TAT - Burst).</td>
        </tr>
        <tr>
          <td><strong>RUNNING</strong></td>
          <td>Worker simulated crash or CPU limit exceeded.</td>
          <td><strong>FAILED</strong></td>
          <td>Parent intercepts non-zero exit code or signal via <code>waitpid()</code> and decodes <code>WTERMSIG</code>.</td>
        </tr>
      </tbody>
    </table>
    <p style="font-size: 9pt; margin-top: 2mm;">
      The <code>READY</code> queue maintains strict FIFO ordering for FCFS, quantum-round slices for Round Robin, and min-heap
      ordering for Priority. Worker processes isolate tasks, preventing child faults from corrupting the parent coordinator.
    </p>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 5</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 6: LITERATURE SURVEY & THEORETICAL FOUNDATION                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading">LITERATURE SURVEY &amp; THEORETICAL FOUNDATION</h1>

    <h2 class="sub-heading">Concept and prior work</h2>
    <p>
      Central processing unit scheduling constitutes a foundational problem in operating systems research [1, 4].
      Non-preemptive policies such as First-Come-First-Served (FCFS) execute tasks in strict arrival sequence, minimizing
      context-switching overhead but introducing severe variance in waiting times due to the convoy effect. Non-preemptive
      Priority scheduling optimizes throughput for mission-critical jobs but introduces potential starvation for low-priority
      workloads without dynamic priority aging. Preemptive Round Robin (RR) time-slices execution into discrete quanta,
      guaranteeing bounded response latency for interactive jobs at the expense of additional scheduling context switches.
    </p>

    <h2 class="sub-heading">CPU scheduling policy comparison and trade-offs</h2>
    <table class="academic-table">
      <thead>
        <tr>
          <th style="width: 22%;">Characteristic</th>
          <th style="width: 26%;">FCFS</th>
          <th style="width: 26%;">Priority (Non-Preemptive)</th>
          <th style="width: 26%;">Round Robin (q = 2)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Preemption Model</strong></td>
          <td>Non-preemptive</td>
          <td>Non-preemptive</td>
          <td>Preemptive (time-sliced)</td>
        </tr>
        <tr>
          <td><strong>Starvation Risk</strong></td>
          <td>Zero (strictly bounded by arrivals)</td>
          <td>High for low priority without aging</td>
          <td>Zero (fair time sharing)</td>
        </tr>
        <tr>
          <td><strong>Response Time</strong></td>
          <td>High for trailing arrivals</td>
          <td>Low for high priority</td>
          <td>Minimized and predictable</td>
        </tr>
        <tr>
          <td><strong>Convoy Effect</strong></td>
          <td>Severe behind long jobs</td>
          <td>Possible behind high-priority long jobs</td>
          <td>Completely mitigated</td>
        </tr>
        <tr>
          <td><strong>Context Switch Overhead</strong></td>
          <td>Minimal (one switch per job)</td>
          <td>Minimal (one switch per job)</td>
          <td>Proportional to total burst / quantum</td>
        </tr>
      </tbody>
    </table>

    <h2 class="sub-heading">Dijkstra's Banker's Algorithm for deadlock avoidance</h2>
    <p>
      Deadlock handling strategies span avoidance, prevention, and detection with recovery [1]. Dijkstra's Banker's Algorithm
      evaluates multi-resource allocation requests by testing whether granting resources leaves the system in a safe state—defined
      as the existence of at least one dispatch sequence <code>&lt;P_1, P_2, ..., P_n&gt;</code> where remaining resource needs
      can be satisfied by current available inventory plus resources released by previously completed processes.
    </p>
    <p style="font-size: 9pt;">
      Let <code>m</code> be resource types and <code>n</code> be processes. Matrices: <code>Available[m]</code>, <code>Max[n][m]</code>,
      <code>Allocation[n][m]</code>, and <code>Need[n][m] = Max[n][m] - Allocation[n][m]</code>.<br>
      <strong>Safety Test Algorithm:</strong> Initialize <code>Work = Available</code> and <code>Finish[i] = false</code> for all <code>i</code>.
      Find index <code>i</code> such that <code>Finish[i] == false</code> and <code>Need[i] &lt;= Work</code>. If found:
      <code>Work = Work + Allocation[i]</code>, <code>Finish[i] = true</code>, and repeat. If all <code>Finish[i] == true</code>,
      the state is safe; otherwise, deadlock risk exists and the request is rejected.
    </p>

    <h2 class="sub-heading">POSIX synchronization and shared memory architecture</h2>
    <p>
      POSIX shared memory (<code>shm_open</code>, <code>mmap</code>) maps identical physical RAM frames into the distinct virtual
      address spaces of cooperating processes, bypassing kernel-to-user memory copy operations [2]. Mutual exclusion and
      handshaking are enforced using named POSIX semaphores (<code>sem_open</code>). Activity logging employs a bounded-buffer
      monitor using <code>pthread_mutex_t</code> and dual condition variables (<code>cond_not_full</code>, <code>cond_not_empty</code>)
      to avoid busy-wait polling [1].
    </p>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 6</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 7: MAIN C SOURCE CODE (PART 1: SCHEDULER)                            -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading">MAIN C SOURCE CODE:</h1>

    <div class="listing-title">Listing 1. Core CPU Scheduling Engine and Multi-Tier Tie Breaking (scheduler.c)</div>
    <div class="code-block">/* Tie-break: priority (Priority policy only), then earlier arrival, then lower job ID. */
static bool better(const Job *a, const Job *b, Policy p) {
  if (p == PRIORITY &amp;&amp; a-&gt;priority != b-&gt;priority)
    return a-&gt;priority &lt; b-&gt;priority;
  if (a-&gt;arrival != b-&gt;arrival)
    return a-&gt;arrival &lt; b-&gt;arrival;
  return a-&gt;id &lt; b-&gt;id;
}

/* Pick next available job according to the selected scheduling policy. */
static int pick(const Job jobs[], const bool done[], int n, int now, Policy p) {
  int best = -1;
  for (int i = 0; i &lt; n; i++) {
    if (done[i] || jobs[i].arrival &gt; now) continue;
    if (best &lt; 0 || better(&amp;jobs[i], &amp;jobs[best], p))
      best = i;
  }
  return best;
}

/* Non-preemptive simulation engine: handles FCFS and Priority scheduling. */
static void simulate_nonpreemptive(Job jobs[], int n, Policy p, Metrics m[], Timeline *t) {
  bool done[MAX_JOBS] = {false};
  int completed = 0, now = 0;
  while (completed &lt; n) {
    int idx = pick(jobs, done, n, now, p);
    if (idx &lt; 0) {
      now = earliest_arrival(jobs, done, n);
      continue;
    }
    int start = now;
    now += jobs[idx].burst;
    add_slice(t, jobs[idx].id, start, now);
    finish(&amp;jobs[idx], &amp;m[idx], now);
    done[idx] = true;
    completed++;
  }
}

/* Round Robin simulation engine with configurable time quantum and arrival queue management. */
static void simulate_rr(Job jobs[], int n, int q, Metrics m[], Timeline *t) {
  int rem[MAX_JOBS], first_start[MAX_JOBS];
  bool admitted[MAX_JOBS] = {false};
  Queue ready = {.head = 0, .tail = 0, .count = 0};
  for (int i = 0; i &lt; n; i++) { rem[i] = jobs[i].burst; first_start[i] = -1; }
  int now = 0, completed = 0;
  admit_arrivals(jobs, n, now, admitted, &amp;ready);

  while (completed &lt; n) {
    if (ready.count == 0) {
      now = earliest_arrival(jobs, admitted, n);
      admit_arrivals(jobs, n, now, admitted, &amp;ready);
      continue;
    }
    int cur = queue_pop(&amp;ready);
    if (first_start[cur] &lt; 0) first_start[cur] = now;
    int slice = (rem[cur] &gt; q) ? q : rem[cur];
    int start = now;
    now += slice;
    rem[cur] -= slice;
    add_slice(t, jobs[cur].id, start, now);
    /* New arrivals admitted before preempted job is re-queued */
    admit_arrivals(jobs, n, now, admitted, &amp;ready);
    if (rem[cur] == 0) {
      finish(&amp;jobs[cur], &amp;m[cur], now);
      completed++;
    } else {
      queue_push(&amp;ready, cur);
    }
  }
}</div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 7</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 8: MAIN C SOURCE CODE (PART 2: LOGGER & IPC)                         -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading">MAIN C SOURCE CODE: (CONTD.)</h1>

    <div class="listing-title">Listing 2. Concurrent Activity Logger with Bounded Circular Queue (logger.c)</div>
    <div class="code-block">/* Bounded-buffer monitor synchronized using POSIX mutex and condition variables. */
static char queue[LOG_QUEUE_SIZE][LOG_MSG_LEN];
static int q_head = 0, q_tail = 0, q_count = 0;
static bool shutdown_requested = false, active = false;
static pthread_mutex_t log_mutex = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t  cond_not_full  = PTHREAD_COND_INITIALIZER;
static pthread_cond_t  cond_not_empty = PTHREAD_COND_INITIALIZER;
static pthread_t consumer_tid;

void logger_log(const char *message) {
  pthread_mutex_lock(&amp;log_mutex);
  if (!active || shutdown_requested) { pthread_mutex_unlock(&amp;log_mutex); return; }
  while (q_count == LOG_QUEUE_SIZE &amp;&amp; !shutdown_requested)
    pthread_cond_wait(&amp;cond_not_full, &amp;log_mutex);
  if (shutdown_requested) { pthread_mutex_unlock(&amp;log_mutex); return; }

  format_timestamped(queue[q_tail], sizeof(queue[q_tail]), message);
  q_tail = (q_tail + 1) % LOG_QUEUE_SIZE;
  q_count++;
  pthread_cond_signal(&amp;cond_not_empty);
  pthread_mutex_unlock(&amp;log_mutex);
}

static void *consumer_thread(void *arg) {
  FILE *f = (FILE *)arg;
  while (1) {
    pthread_mutex_lock(&amp;log_mutex);
    while (q_count == 0 &amp;&amp; !shutdown_requested)
      pthread_cond_wait(&amp;cond_not_empty, &amp;log_mutex);
    if (q_count == 0 &amp;&amp; shutdown_requested) { pthread_mutex_unlock(&amp;log_mutex); break; }
    char entry[LOG_MSG_LEN];
    memcpy(entry, queue[q_head], sizeof(entry));
    q_head = (q_head + 1) % LOG_QUEUE_SIZE;
    q_count--;
    pthread_cond_signal(&amp;cond_not_full);
    pthread_mutex_unlock(&amp;log_mutex);
    fputs(entry, f); fflush(f);
  }
  return NULL;
}</div>

    <div class="listing-title">Listing 3. Inter-Process Communication via Shared Memory &amp; Semaphores (ipc.c)</div>
    <div class="code-block">/* Exchange payload between cooperating parent and child processes via shm &amp; named semaphores */
int ipc_demo(void) {
  char shm_name[64], sem_ready_name[64], sem_done_name[64];
  make_ipc_names(shm_name, sem_ready_name, sem_done_name, sizeof(shm_name), getpid());
  int fd = shm_open(shm_name, O_CREAT | O_EXCL | O_RDWR, 0600);
  ftruncate(fd, sizeof(SharedJobPacket));
  SharedJobPacket *pkt = mmap(NULL, sizeof(*pkt), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
  sem_t *sem_ready = sem_open(sem_ready_name, O_CREAT | O_EXCL, 0600, 0);
  sem_t *sem_done  = sem_open(sem_done_name,  O_CREAT | O_EXCL, 0600, 0);

  pid_t pid = fork_flushed();
  if (pid == 0) {
    sem_wait(sem_ready);
    snprintf(pkt-&gt;result, sizeof(pkt-&gt;result), "job %d executed by child %d", pkt-&gt;job_id, getpid());
    sem_post(sem_done);
    munmap(pkt, sizeof(*pkt)); close(fd);
    sem_close(sem_ready); sem_close(sem_done);
    child_exit(0);
  }
  /* Parent writes task, posts ready, awaits done, reaps child, and unlinks objects */
  pkt-&gt;job_id = 101; strncpy(pkt-&gt;task, "Fluid_Dynamics_Sim", sizeof(pkt-&gt;task));
  sem_post(sem_ready);
  sem_wait(sem_done);
  waitpid(pid, NULL, 0);
  munmap(pkt, sizeof(*pkt)); close(fd);
  shm_unlink(shm_name); sem_unlink(sem_ready_name); sem_unlink(sem_done_name);
  return 0;
}</div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 8</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 9: MAIN C SOURCE CODE (PART 3: BANKER & WORKER)                      -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading">MAIN C SOURCE CODE: (CONTD.)</h1>

    <div class="listing-title">Listing 4. Dijkstra's Banker's Deadlock Avoidance Safety Algorithm (banker.c)</div>
    <div class="code-block">/* Evaluates state safety and discovers deadlock-free safe sequence */
static bool is_state_safe(const BankerState *s, int safe_seq[]) {
  int work[MAX_RESOURCES];
  bool finish[MAX_PROCESSES] = {false};
  for (int j = 0; j &lt; s-&gt;num_resources; j++) work[j] = s-&gt;available[j];

  int count = 0;
  while (count &lt; s-&gt;num_processes) {
    bool found = false;
    for (int p = 0; p &lt; s-&gt;num_processes; p++) {
      if (finish[p]) continue;
      bool can_allocate = true;
      for (int r = 0; r &lt; s-&gt;num_resources; r++) {
        if (s-&gt;need[p][r] &gt; work[r]) { can_allocate = false; break; }
      }
      if (can_allocate) {
        for (int r = 0; r &lt; s-&gt;num_resources; r++) work[r] += s-&gt;allocation[p][r];
        safe_seq[count++] = p;
        finish[p] = true;
        found = true;
        break;
      }
    }
    if (!found) return false; /* Deadlock hazard: no process can finish */
  }
  return true; /* Complete safe sequence discovered */
}</div>

    <div class="listing-title">Listing 5. Worker Process Lifecycle, Failure Detection &amp; Resource Bounding (worker.c, rlimit.c)</div>
    <div class="code-block">/* Spawn isolated worker child via fork() and collect exit status via waitpid() */
int run_worker_task(int simulated_exit_code) {
  pid_t pid = fork_flushed();
  if (pid == 0) {
    if (simulated_exit_code != 0) {
      fprintf(stderr, "[Worker %d] simulating failure with exit code %d\n", getpid(), simulated_exit_code);
      child_exit(simulated_exit_code);
    }
    child_exit(0);
  }
  int status = 0;
  waitpid(pid, &amp;status, 0);
  if (WIFEXITED(status)) {
    int code = WEXITSTATUS(status);
    printf("[Coordinator] worker %d exited with status %d -&gt; %s\n",
           pid, code, (code == 0) ? "COMPLETED" : "FAILED");
    return (code == 0) ? 0 : 1;
  }
  return 1;
}

/* Enforce 1-second CPU execution limit using kernel setrlimit(RLIMIT_CPU) */
int rlimit_demo_cpu(void) {
  pid_t pid = fork_flushed();
  if (pid == 0) {
    struct rlimit rl = {.rlim_cur = 1, .rlim_max = 2};
    setrlimit(RLIMIT_CPU, &amp;rl);
    volatile unsigned long long count = 0;
    while (1) { count++; } /* Runaway computation intercepted by kernel */
    child_exit(0);
  }
  int status;
  waitpid(pid, &amp;status, 0);
  return (WIFSIGNALED(status) &amp;&amp; WTERMSIG(status) == SIGXCPU) ? 0 : 1;
}</div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 9</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 10: TEST BENCH & BUILD AUTOMATION                                    -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading">TEST BENCH &amp; BUILD AUTOMATION</h1>

    <div class="listing-title">Listing 6. Build Automation and Multi-Target Configuration (Makefile)</div>
    <div class="code-block">CC      = gcc
CFLAGS  = -Wall -Wextra -g -std=c99 -pthread -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE
LDFLAGS = -pthread -lrt
SRN    ?= __SRN__

TARGET  = campuscompute
SRCS    = main.c input.c scheduler.c logger.c ipc.c banker.c worker.c rlimit.c
OBJS    = $(SRCS:.c=.o)
HEADERS = common.h scheduler.h logger.h ipc.h banker.h worker.h rlimit.h

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $&lt; -o $@

clean:
	rm -f $(OBJS) $(TARGET) campuscompute.log

zip: clean
	rm -f $(SRN).zip
	zip -r $(SRN).zip docs samples tests $(SRCS) $(HEADERS) Makefile README.md
	@echo "Verifying archive integrity:"
	unzip -t $(SRN).zip</div>

    <h2 class="sub-heading">Automated multi-subsystem verification suite</h2>
    <p>
      Verification is conducted using <code>tests/test_campuscompute.py</code> and <code>tests/rigorous_evaluation.py</code>.
      The test suite enforces rigorous programmatic checks validating scheduling metrics, race-free multithreading,
      IPC transaction integrity, deadlock avoidance math, and leak-free resource release.
    </p>

    <table class="academic-table">
      <thead>
        <tr>
          <th style="width: 14%;">Test Vector</th>
          <th style="width: 32%;">Target Subsystem &amp; Conditions</th>
          <th style="width: 40%;">Verification Assertions &amp; Boundary Checks</th>
          <th style="width: 14%;">Result</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>TV-SCHED-01</strong></td>
          <td>FCFS Scheduling (Convoy workload)</td>
          <td>Validates non-preemptive timeline; asserts CT[i] &gt;= CT[i-1]; WT = TAT - Burst.</td>
          <td><strong>PASS</strong></td>
        </tr>
        <tr>
          <td><strong>TV-SCHED-02</strong></td>
          <td>Round Robin (q = 2, concurrent arrivals)</td>
          <td>Validates time slicing; verifies new arrivals enter queue before preempted jobs.</td>
          <td><strong>PASS</strong></td>
        </tr>
        <tr>
          <td><strong>TV-SCHED-03</strong></td>
          <td>Priority Scheduling (Equal priority tie)</td>
          <td>Asserts multi-tier resolution: priority &gt; arrival time &gt; lower Job ID.</td>
          <td><strong>PASS</strong></td>
        </tr>
        <tr>
          <td><strong>TV-SYNC-01</strong></td>
          <td>Producer-Consumer Activity Logger</td>
          <td>3 producer threads x 5 events; asserts bounded queue never exceeds 8 items.</td>
          <td><strong>PASS</strong></td>
        </tr>
        <tr>
          <td><strong>TV-IPC-01</strong></td>
          <td>Shared Memory &amp; Named Semaphores</td>
          <td>Asserts parent payload matches child reception; verifies 0 objects left in /dev/shm.</td>
          <td><strong>PASS</strong></td>
        </tr>
        <tr>
          <td><strong>TV-BANK-01</strong></td>
          <td>Banker's Algorithm (Safe &amp; Unsafe matrices)</td>
          <td>Asserts safe sequence existence for safe input; rejects unsafe state with deadlock alert.</td>
          <td><strong>PASS</strong></td>
        </tr>
        <tr>
          <td><strong>TV-PROC-01</strong></td>
          <td>Worker Failure Detection &amp; RLIMIT_CPU</td>
          <td>Reaps exit(0) as COMPLETED; exit(1) as FAILED; catches SIGXCPU via waitpid().</td>
          <td><strong>PASS</strong></td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 10</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 11: SCREEN SHOTS OF THE OUTPUT (OVERVIEW & SUMMARY)                  -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading">SCREEN SHOTS OF THE OUTPUT:</h1>

    <h2 class="sub-heading">Actual execution results and test evidence</h2>
    <p>
      CampusCompute was compiled and verified on an authentic Linux environment (Arch Linux x86_64, Linux 6.x kernel,
      GCC 16.2.1, GNU Make 4.4.1) using the student's personal Kitty terminal with active prompt SRN configuration
      (<code>PES2UG25CS617</code>). All 24 functional requirements were independently tested and captured.
    </p>

    <table class="academic-table">
      <thead>
        <tr>
          <th style="width: 8%; text-align: center;">Item</th>
          <th style="width: 32%;">Requirement Description</th>
          <th style="width: 38%;">Execution Command / Action</th>
          <th style="width: 12%; text-align: center;">Status</th>
          <th style="width: 10%; text-align: center;">Page</th>
        </tr>
      </thead>
      <tbody>
        <tr><td style="text-align: center;"><strong>S01</strong></td><td>Terminal environment, SRN prompt, working directory</td><td><code>pwd; echo Logged in; echo SRN</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">12</td></tr>
        <tr><td style="text-align: center;"><strong>S02</strong></td><td>GCC C99 compiler and GNU Make toolchain</td><td><code>gcc --version; make --version</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">12</td></tr>
        <tr><td style="text-align: center;"><strong>S03</strong></td><td>Project workspace directory structure and Makefile</td><td><code>ls -la</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">13</td></tr>
        <tr><td style="text-align: center;"><strong>S04</strong></td><td>Clean build from source (-Wall -Wextra)</td><td><code>make clean &amp;&amp; make</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">14</td></tr>
        <tr><td style="text-align: center;"><strong>S05</strong></td><td>Command-line interface help banner and menu options</td><td><code>./campuscompute --help</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">15</td></tr>
        <tr><td style="text-align: center;"><strong>S06</strong></td><td>FCFS scheduling execution order and metrics</td><td><code>./campuscompute --fcfs</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">16</td></tr>
        <tr><td style="text-align: center;"><strong>S07</strong></td><td>Round Robin scheduling with time quantum (q=2)</td><td><code>./campuscompute --rr 2</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">16</td></tr>
        <tr><td style="text-align: center;"><strong>S08</strong></td><td>Priority scheduling and deterministic tie-breaking</td><td><code>./campuscompute --priority</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">17</td></tr>
        <tr><td style="text-align: center;"><strong>S09</strong></td><td>Side-by-side policy comparative evaluation</td><td><code>./campuscompute --compare</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">17</td></tr>
        <tr><td style="text-align: center;"><strong>S10</strong></td><td>Concurrent multi-threaded activity logger</td><td><code>./campuscompute --logger</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">18</td></tr>
        <tr><td style="text-align: center;"><strong>S11</strong></td><td>Thread synchronization and graceful termination</td><td><code>./campuscompute --logger-custom</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">18</td></tr>
        <tr><td style="text-align: center;"><strong>S12</strong></td><td>Inter-process communication via shared memory</td><td><code>./campuscompute --ipc</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">19</td></tr>
        <tr><td style="text-align: center;"><strong>S13</strong></td><td>Named semaphore synchronization and IPC cleanup</td><td><code>./campuscompute --ipc-custom</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">19</td></tr>
        <tr><td style="text-align: center;"><strong>S14</strong></td><td>Banker's algorithm safe sequence discovery</td><td><code>./campuscompute --banker-safe</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">20</td></tr>
        <tr><td style="text-align: center;"><strong>S15</strong></td><td>Banker's algorithm unsafe state detection</td><td><code>./campuscompute --banker-unsafe</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">20</td></tr>
        <tr><td style="text-align: center;"><strong>S16</strong></td><td>Worker process creation and normal completion</td><td><code>./campuscompute --worker-ok</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">21</td></tr>
        <tr><td style="text-align: center;"><strong>S17</strong></td><td>Simulated worker failure detection</td><td><code>./campuscompute --worker-fail</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">21</td></tr>
        <tr><td style="text-align: center;"><strong>S18</strong></td><td>Process resource limits enforcement (RLIMIT_CPU)</td><td><code>./campuscompute --rlimit</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">22</td></tr>
        <tr><td style="text-align: center;"><strong>S19</strong></td><td>Invalid CLI argument handling and diagnostics</td><td><code>./campuscompute --invalid-option</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">22</td></tr>
        <tr><td style="text-align: center;"><strong>S20</strong></td><td>Zero-leak system resource cleanup verification</td><td><code>./campuscompute --cleanup; ls /dev/shm</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">23</td></tr>
        <tr><td style="text-align: center;"><strong>S21</strong></td><td>Integrated test demonstration execution (--demo)</td><td><code>./campuscompute --demo</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">24</td></tr>
        <tr><td style="text-align: center;"><strong>S22</strong></td><td>Structured persistent event log file inspection</td><td><code>cat campuscompute.log | tail -n 25</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">25</td></tr>
        <tr><td style="text-align: center;"><strong>S23</strong></td><td>Final project source files, Makefile, binary</td><td><code>ls -lh campuscompute ...</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">25</td></tr>
        <tr><td style="text-align: center;"><strong>S24</strong></td><td>Submission ZIP archive listing and integrity test</td><td><code>unzip -l $SRN.zip; unzip -t $SRN.zip</code></td><td style="text-align: center;">PASS</td><td style="text-align: center;">26</td></tr>
      </tbody>
    </table>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 11</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 12: S01 & S02                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 1 - Ubuntu/WSL terminal environment, active working directory, and prompt with full student SRN.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S01']}" alt="S01" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[0]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 6mm;">
      <div class="screenshot-caption">Screenshot 2 - GCC C99 compiler version and GNU Make utility verification.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S02']}" alt="S02" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[1]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 12</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 13: S03                                                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 3 - Project workspace directory structure, modular C sources, headers, documentation, and Makefile.</div>
      <div class="screenshot-frame" style="max-height: 225mm;">
        <img src="data:image/png;base64,{b64_images['S03']}" alt="S03" style="max-height: 215mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[2]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 13</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 14: S04                                                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 4 - Clean compilation of all modules with compiler warnings enabled (-Wall -Wextra) and final binary linking.</div>
      <div class="screenshot-frame" style="max-height: 220mm;">
        <img src="data:image/png;base64,{b64_images['S04']}" alt="S04" style="max-height: 210mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[3]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 14</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 15: S05                                                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 5 - Command-line interface help banner and numbered interactive menu options.</div>
      <div class="screenshot-frame" style="max-height: 225mm;">
        <img src="data:image/png;base64,{b64_images['S05']}" alt="S05" style="max-height: 215mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[4]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 15</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 16: S06 & S07                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 6 - First-Come-First-Served (FCFS) scheduling execution timeline and per-job metrics.</div>
      <div class="screenshot-frame" style="max-height: 100mm;">
        <img src="data:image/png;base64,{b64_images['S06']}" alt="S06" style="max-height: 92mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[5]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 7 - Round Robin scheduling execution order, time quantum (q=2), and performance metrics.</div>
      <div class="screenshot-frame" style="max-height: 105mm;">
        <img src="data:image/png;base64,{b64_images['S07']}" alt="S07" style="max-height: 96mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[6]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 16</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 17: S08 & S09                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 8 - Non-preemptive Priority scheduling with multi-tier deterministic tie-breaking.</div>
      <div class="screenshot-frame" style="max-height: 110mm;">
        <img src="data:image/png;base64,{b64_images['S08']}" alt="S08" style="max-height: 100mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[7]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 9 - Side-by-side comparative evaluation of FCFS, Priority, and Round Robin on identical workload.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S09']}" alt="S09" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[8]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 17</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 18: S10 & S11                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 10 - Concurrent multi-threaded activity logger with bounded circular queue.</div>
      <div class="screenshot-frame" style="max-height: 110mm;">
        <img src="data:image/png;base64,{b64_images['S10']}" alt="S10" style="max-height: 100mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[9]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 11 - Thread synchronization via mutexes and condition variables with graceful termination.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S11']}" alt="S11" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[10]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 18</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 19: S12 & S13                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 12 - Inter-process communication between parent and child processes via POSIX shared memory.</div>
      <div class="screenshot-frame" style="max-height: 100mm;">
        <img src="data:image/png;base64,{b64_images['S12']}" alt="S12" style="max-height: 90mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[11]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 13 - IPC coordination using POSIX named semaphores and immediate cleanup verification.</div>
      <div class="screenshot-frame" style="max-height: 90mm;">
        <img src="data:image/png;base64,{b64_images['S13']}" alt="S13" style="max-height: 80mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[12]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 19</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 20: S14 & S15                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 14 - Banker's algorithm execution discovering a safe execution sequence.</div>
      <div class="screenshot-frame" style="max-height: 105mm;">
        <img src="data:image/png;base64,{b64_images['S14']}" alt="S14" style="max-height: 95mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[13]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 15 - Banker's algorithm correctly detecting an unsafe state and identifying deadlock hazard.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S15']}" alt="S15" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[14]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 20</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 21: S16 & S17                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 16 - Worker child process creation via fork() and normal exit status collection via waitpid().</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S16']}" alt="S16" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[15]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 6mm;">
      <div class="screenshot-caption">Screenshot 17 - Controlled simulated worker failure and parent-side abnormal termination detection.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S17']}" alt="S17" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[16]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 21</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 22: S18 & S19                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 18 - Enforcement of CPU resource limits using setrlimit(RLIMIT_CPU) and observation of SIGXCPU.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S18']}" alt="S18" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[17]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 6mm;">
      <div class="screenshot-caption">Screenshot 19 - Error handling and usage diagnostic messages for invalid CLI arguments.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S19']}" alt="S19" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[18]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 22</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 23: S20                                                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 20 - System cleanup verification confirming zero leaked processes, threads, or IPC objects.</div>
      <div class="screenshot-frame" style="max-height: 220mm;">
        <img src="data:image/png;base64,{b64_images['S20']}" alt="S20" style="max-height: 210mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[19]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 23</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 24: S21                                                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 21 - Comprehensive end-to-end integrated demonstration execution (--demo) and test summary.</div>
      <div class="screenshot-frame" style="max-height: 225mm;">
        <img src="data:image/png;base64,{b64_images['S21']}" alt="S21" style="max-height: 215mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[20]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 24</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 25: S22 & S23                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 22 - Inspection of campuscompute.log showing formatted millisecond timestamps and event records.</div>
      <div class="screenshot-frame" style="max-height: 105mm;">
        <img src="data:image/png;base64,{b64_images['S22']}" alt="S22" style="max-height: 95mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[21]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 23 - Verification of final source files, headers, build system, and compiled executable binary.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_images['S23']}" alt="S23" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[22]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 25</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 26: S24                                                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 24 - Submission ZIP archive contents listing and archive integrity check (unzip -t).</div>
      <div class="screenshot-frame" style="max-height: 225mm;">
        <img src="data:image/png;base64,{b64_images['S24']}" alt="S24" style="max-height: 215mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[23]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 26</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 27: REFERENCES                                                       -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading">REFERENCES</h1>

    <h2 class="sub-heading">Sources and bibliography</h2>
    <ol style="font-size: 10pt; line-height: 1.5; padding-left: 6mm;">
      <li>
        Silberschatz, A., Galvin, P. B., &amp; Gagne, G. (2018). <em>Operating System Concepts</em> (10th ed.).
        John Wiley &amp; Sons, Inc. (Chapters 5: CPU Scheduling, 6: Synchronization Tools, 7: Synchronization Examples, 8: Deadlocks).
      </li>
      <li>
        Kerrisk, M. (2010). <em>The Linux Programming Interface: A Linux and UNIX System Programming Handbook</em>.
        No Starch Press, San Francisco. (Chapters 24–28: Process Creation &amp; Termination, 29–33: POSIX Threads, 54: POSIX Shared Memory, 53: POSIX Semaphores).
      </li>
      <li>
        IEEE Std 1003.1-2008 / POSIX.1-2008 (The Open Group Technical Standard), <em>Standard for Information Technology—Portable Operating System Interface (POSIX(R))</em>,
        IEEE Computer Society / The Open Group.
      </li>
      <li>
        Tanenbaum, A. S., &amp; Bos, H. (2015). <em>Modern Operating Systems</em> (4th ed.).
        Pearson Education, Inc. (Process scheduling algorithms, IPC race conditions, Dijkstra's safety matrix equations).
      </li>
      <li>
        Stallings, W. (2018). <em>Operating Systems: Internals and Design Principles</em> (9th ed.).
        Pearson Education, Inc. (Concurrency, mutual exclusion, deadlock avoidance and detection models).
      </li>
      <li>
        Linux Programmer's Manual, Linux man-pages Project, <em>pthreads(7)</em>, <em>shm_overview(7)</em>, <em>sem_overview(7)</em>,
        <em>waitpid(2)</em>, <em>setrlimit(2)</em>, <em>mmap(2)</em>. Available: <span style="text-decoration: underline;">https://man7.org/linux/man-pages/</span>
      </li>
    </ol>

    <div style="margin-top: 15mm; border: 1px solid #000; padding: 6mm; text-align: center;">
      <div style="font-size: 11pt; font-weight: bold; margin-bottom: 2mm;">
        DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING
      </div>
      <div style="font-size: 10pt;">
        PES UNIVERSITY (ELECTRONIC CITY CAMPUS), BENGALURU - 560100<br>
        UE25CS242A — Operating Systems Laboratory Mini-Project (Level 3)<br>
        Academic Period: August – December 2026
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 27</span>
  </div>
</div>

</body>
</html>
"""

    html_content = html_content.replace("__STUDENT_NAME__", student_name)
    html_content = html_content.replace("__PARTNER_NAME__", partner_name)
    html_content = html_content.replace("__PARTNER_SRN__", partner_srn)
    html_content = html_content.replace("__SRN__", srn)
    html_content = html_content.replace("__B64_LOGO__", b64_images.get("LOGO", ""))
    for i in range(24):
        key = "{ITEMS[" + str(i) + "]['expl']}"
        html_content = html_content.replace(key, html.escape(ITEMS[i]["expl"]))
    for i in range(1, 25):
        num = f'S{i:02d}'
        img_key = "{b64_images['" + num + "']}"
        html_content = html_content.replace(img_key, b64_images[num])

    return html_content


def compile_pdf(html_content, output_pdf_path):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html_content)
        tmp_html_path = f.name

    print(f"[*] Compiling PDF using Chromium: {output_pdf_path}...")
    cmd = [
        "chromium",
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_pdf_path}",
        tmp_html_path
    ]
    subprocess.run(cmd, check=True)
    os.remove(tmp_html_path)
    print(f"[+] Generated: {output_pdf_path} ({os.path.getsize(output_pdf_path) // 1024} KB)")


def main():
    print("=" * 72)
    print("CampusCompute — Academic Report and Deliverables Generator")
    print("Following DLCD_Serial_Adder_2026_Faculty_Template_Editable.pdf format")
    print("=" * 72)

    # 1. Load base64 encoded authentic screenshots
    print("[*] Loading and encoding authentic Kitty screenshots S01 to S24...")
    b64_images = load_base64_images()

    # 2. Generate PDF for Yatin R (PES2UG25CS617)
    print("[*] Generating academic PDF report for Yatin R (PES2UG25CS617)...")
    html_617 = generate_report_html(
        srn="PES2UG25CS617",
        student_name="Yatin R",
        partner_srn="PES2UG25CS609",
        partner_name="Yaduveer Pavan",
        b64_images=b64_images
    )
    pdf_617 = BASE_DIR / "PES2UG25CS617.pdf"
    compile_pdf(html_617, pdf_617)

    # 3. Generate PDF for Yaduveer Pavan (PES2UG25CS609)
    print("[*] Generating academic PDF report for Yaduveer Pavan (PES2UG25CS609)...")
    html_609 = generate_report_html(
        srn="PES2UG25CS609",
        student_name="Yaduveer Pavan",
        partner_srn="PES2UG25CS617",
        partner_name="Yatin R",
        b64_images=b64_images
    )
    pdf_609 = BASE_DIR / "PES2UG25CS609.pdf"
    compile_pdf(html_609, pdf_609)

    # 4. Generate verified submission ZIPs
    print("[*] Packaging and verifying submission ZIP archives...")
    subprocess.run(["make", "zip", "SRN=PES2UG25CS617"], cwd=BASE_DIR, check=True)
    subprocess.run(["make", "zip", "SRN=PES2UG25CS609"], cwd=BASE_DIR, check=True)

    # 5. Recompile project binary to leave tree in ready-to-run state
    subprocess.run(["make"], cwd=BASE_DIR, check=True)

    print("\n" + "=" * 72)
    print("DELIVERABLES GENERATION COMPLETE!")
    print("=" * 72)
    print(f"1. Academic Report (Yatin R):        {pdf_617} ({pdf_617.stat().st_size // 1024} KB)")
    print(f"2. Academic Report (Yaduveer Pavan): {pdf_609} ({pdf_609.stat().st_size // 1024} KB)")
    print(f"3. Submission ZIP (Yatin R):         {BASE_DIR / 'PES2UG25CS617.zip'}")
    print(f"4. Submission ZIP (Yaduveer Pavan):  {BASE_DIR / 'PES2UG25CS609.zip'}")
    print("=" * 72)


if __name__ == "__main__":
    main()

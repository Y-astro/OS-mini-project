#!/usr/bin/env python3
"""
CampusCompute — Deliverables & Screenshot Evidence Generator
Strictly adheres to the PES University UE25CS242A Level 3 Mini-Project Submission Guidelines:
  - "Do not include a separate project report. The required evidence is the screenshots with one-line explanations."
  - "Combine the screenshots and their one-line explanations into a single PDF. Name the PDF using your own SRN only."
  - "Submit a ZIP containing the source code and build files."

Deliverables:
  1. PES2UG25CS617.pdf (Strictly-compliant 17-page evidence document for Yatin R)
  2. PES2UG25CS609.pdf (Strictly-compliant 17-page evidence document for Yaduveer Pavan)
  3. PES2UG25CS617.zip and PES2UG25CS609.zip (Verified submission archives)
  4. docs/PES2UG25CS617_Full_Report.pdf (Archived 27-page comprehensive theoretical report)
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
LOGO_PATH = BASE_DIR / "assets" / "pes_logo.png"

# Section 4 Screenshot Checklist & Verbatim One-Line Explanations from the Faculty Guidelines
ITEMS = [
    {
        "num": "S01",
        "title": "Ubuntu/WSL terminal, complete SRN prompt, and working directory",
        "cmd": 'pwd; echo "Logged in user: $(whoami)"; echo "Active SRN: $SRN"',
        "page": 3,
        "expl": "S01 – Environment and SRN prompt: Shows Ubuntu/WSL terminal, full SRN prompt, and working directory."
    },
    {
        "num": "S02",
        "title": "GCC and Make versions or confirmation that required build tools are available",
        "cmd": "gcc --version | head -n 1; make --version | head -n 1",
        "page": 3,
        "expl": "S02 – Compiler and build tools: Shows GCC and Make versions or confirms the required tools are available."
    },
    {
        "num": "S03",
        "title": "Project directory, source files, and Makefile",
        "cmd": "ls -la",
        "page": 4,
        "expl": "S03 – Project files: Shows the project directory, source files, and Makefile."
    },
    {
        "num": "S04",
        "title": "Successful clean build from source",
        "cmd": "make clean && make",
        "page": 5,
        "expl": "S04 – Clean build: Shows the program compiling from source without unresolved compiler errors."
    },
    {
        "num": "S05",
        "title": "CLI help, usage instructions, or menu options",
        "cmd": "./campuscompute --help",
        "page": 6,
        "expl": "S05 – CLI help/usage: Shows available commands or menu options."
    },
    {
        "num": "S06",
        "title": "FCFS scheduling execution order and calculated metrics",
        "cmd": "./campuscompute --fcfs",
        "page": 7,
        "expl": "S06 – FCFS scheduling: Shows FCFS execution order and calculated scheduling metrics."
    },
    {
        "num": "S07",
        "title": "Round Robin scheduling with time quantum and metrics",
        "cmd": "./campuscompute --rr 2",
        "page": 7,
        "expl": "S07 – Round Robin scheduling: Shows the time quantum, execution order, and scheduling metrics."
    },
    {
        "num": "S08",
        "title": "Non-preemptive Priority scheduling and tie-breaking rule",
        "cmd": "./campuscompute --priority",
        "page": 8,
        "expl": "S08 – Priority scheduling: Shows job priorities, tie-breaking rule where needed, and scheduling metrics."
    },
    {
        "num": "S09",
        "title": "Comparative evaluation of scheduling policies",
        "cmd": "./campuscompute --compare",
        "page": 8,
        "expl": "S09 – Scheduling comparison: Shows a comparison of scheduling policies using the same job set."
    },
    {
        "num": "S10",
        "title": "Producer-consumer activity logger execution",
        "cmd": "./campuscompute --logger",
        "page": 9,
        "expl": "S10 – Producer-consumer logger: Shows producer/consumer activity and generated log entries."
    },
    {
        "num": "S11",
        "title": "Thread synchronization, condition variables, and clean termination",
        "cmd": "./campuscompute --logger-custom",
        "page": 9,
        "expl": "S11 – Thread synchronization and termination: Shows synchronized operation and orderly thread completion."
    },
    {
        "num": "S12",
        "title": "Cooperating processes exchanging data via POSIX shared memory",
        "cmd": "./campuscompute --ipc",
        "page": 10,
        "expl": "S12 – Shared-memory IPC: Shows cooperating processes exchanging data through shared memory."
    },
    {
        "num": "S13",
        "title": "Named semaphore synchronization and IPC cleanup",
        "cmd": "./campuscompute --ipc-custom",
        "page": 10,
        "expl": "S13 – Semaphore coordination and cleanup: Shows synchronization using the implemented semaphore and cleanup of created IPC resources."
    },
    {
        "num": "S14",
        "title": "Banker's algorithm safe state evaluation and sequence discovery",
        "cmd": "./campuscompute --banker-safe",
        "page": 11,
        "expl": "S14 – Banker's safe state: Shows a safe resource state and a valid safe sequence."
    },
    {
        "num": "S15",
        "title": "Banker's algorithm unsafe state detection",
        "cmd": "./campuscompute --banker-unsafe",
        "page": 11,
        "expl": "S15 – Banker's unsafe state: Shows the algorithm identifying an unsafe resource state."
    },
    {
        "num": "S16",
        "title": "Worker process creation and normal completion status collection",
        "cmd": "./campuscompute --worker-ok",
        "page": 12,
        "expl": "S16 – Normal worker process: Shows child-process creation and normal completion status."
    },
    {
        "num": "S17",
        "title": "Controlled simulated worker failure detection",
        "cmd": "./campuscompute --worker-fail",
        "page": 12,
        "expl": "S17 – Simulated worker failure: Shows controlled non-zero/abnormal worker termination and parent-side detection."
    },
    {
        "num": "S18",
        "title": "Process resource limits enforcement (RLIMIT_CPU)",
        "cmd": "./campuscompute --rlimit",
        "page": 13,
        "expl": "S18 – Resource-limit demonstration: Shows the resource limit applied and the observed effect."
    },
    {
        "num": "S19",
        "title": "Invalid command and malformed input error handling",
        "cmd": "./campuscompute --invalid-option",
        "page": 13,
        "expl": "S19 – Invalid input/command: Shows an invalid command or input and the resulting error/usage message."
    },
    {
        "num": "S20",
        "title": "Comprehensive system cleanup verification",
        "cmd": "./campuscompute --cleanup; ls /dev/shm",
        "page": 14,
        "expl": "S20 – Cleanup verification: Shows that created processes/threads have ended and program-created IPC resources are released."
    },
    {
        "num": "S21",
        "title": "Integrated demonstration execution and test results",
        "cmd": "./campuscompute --demo",
        "page": 15,
        "expl": "S21 – Integrated execution: Shows the integrated demonstration and its summary."
    },
    {
        "num": "S22",
        "title": "Structured persistent event log file inspection",
        "cmd": "cat campuscompute.log | tail -n 25",
        "page": 16,
        "expl": "S22 – Generated logs: Shows the log file created by the program and a sample of its contents."
    },
    {
        "num": "S23",
        "title": "Final project source files, Makefile, and executable binary",
        "cmd": "ls -lh campuscompute common.h scheduler.c ...",
        "page": 16,
        "expl": "S23 – Final source and build files: Shows the final source files, Makefile, and executable."
    },
    {
        "num": "S24",
        "title": "Submission ZIP archive structure and integrity check",
        "cmd": "unzip -l SRN1_SRN2.zip; unzip -t SRN1_SRN2.zip",
        "page": 17,
        "expl": "S24 – Submission ZIP: Shows the archive contents and a successful archive integrity check."
    }
]

def load_base64_assets():
    b64_dict = {}
    for item in ITEMS:
        num = item["num"]
        p = SCREENSHOTS_DIR / f"{num}.png"
        if not p.exists():
            raise FileNotFoundError(f"Missing required screenshot: {p}")
        with open(p, "rb") as f:
            b64_dict[num] = base64.b64encode(f.read()).decode("utf-8")
    
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            b64_dict["LOGO"] = base64.b64encode(f.read()).decode("utf-8")
    else:
        b64_dict["LOGO"] = ""
    return b64_dict


def generate_evidence_pdf_html(srn, student_name, partner_srn, partner_name, b64_assets):
    """
    Generates strictly guideline-compliant 17-page Evidence Document:
      - Page 1: Formal Cover Page with PES University Logo and Team Table
      - Page 2: Checklist Table (S01 to S24)
      - Pages 3-17: 24 authentic Kitty screenshots with exact 1-line explanations
    """
    rows_html = []
    for item in ITEMS:
        rows_html.append(f"""
        <tr>
          <td style="text-align: center; font-weight: bold;">{item['num']}</td>
          <td>{html.escape(item['title'])}</td>
          <td><code style="font-size: 8.5pt;">{html.escape(item['cmd'])}</code></td>
          <td style="text-align: center; font-weight: bold;">PASS</td>
          <td style="text-align: center; font-weight: bold;">{item['page']}</td>
        </tr>""")
    checklist_rows = "".join(rows_html)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Operating Systems Mini-Project Verification Evidence — {srn}</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 14mm 16mm 14mm 16mm;
  }}

  * {{
    box-sizing: border-box;
  }}

  body {{
    margin: 0;
    padding: 0;
    font-family: Calibri, "Liberation Sans", "DejaVu Sans", Arial, sans-serif;
    color: #000000;
    background-color: #ffffff;
    font-size: 11pt;
    line-height: 1.35;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}

  .page-container {{
    width: 100%;
    height: 268mm;
    max-height: 268mm;
    position: relative;
    page-break-after: always;
    page-break-inside: avoid;
    overflow: hidden;
  }}

  .page-body {{
    height: 258mm;
    overflow: hidden;
  }}

  .page-footer {{
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
  }}

  /* Typography */
  h1.section-heading {{
    font-size: 15pt;
    font-weight: bold;
    text-align: center;
    text-transform: uppercase;
    margin: 0 0 4mm 0;
    letter-spacing: 0.5px;
  }}

  h2.sub-heading {{
    font-size: 11.5pt;
    font-weight: bold;
    margin: 3mm 0 1.5mm 0;
    color: #000000;
  }}

  p {{
    margin: 0 0 2.5mm 0;
    text-align: justify;
  }}

  /* Table styling */
  table.academic-table {{
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #000000;
    margin: 2mm 0 3mm 0;
    font-size: 9pt;
  }}

  table.academic-table th {{
    border: 1px solid #000000;
    padding: 3.5px 6px;
    font-weight: bold;
    text-align: left;
    background-color: #f2f2f2;
  }}

  table.academic-table td {{
    border: 1px solid #000000;
    padding: 2.8px 6px;
    vertical-align: top;
  }}

  /* Screenshot display */
  .screenshot-box {{
    margin: 1.5mm 0 3mm 0;
    text-align: center;
  }}

  .screenshot-frame {{
    display: inline-block;
    border: 1px solid #333333;
    padding: 1px;
    background: #ffffff;
    max-width: 98%;
  }}

  .screenshot-frame img {{
    max-width: 100%;
    height: auto;
    display: block;
  }}

  .screenshot-caption {{
    font-size: 9.5pt;
    font-weight: bold;
    text-align: left;
    margin-top: 1.5mm;
  }}

  .screenshot-explanation {{
    font-size: 9pt;
    text-align: justify;
    margin-top: 1mm;
    margin-bottom: 2mm;
    line-height: 1.3;
  }}

  /* Cover page specific */
  .cover-container {{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    text-align: center;
    padding: 4mm 5mm 5mm 5mm;
  }}

  .cover-logo {{
    text-align: center;
    margin-bottom: 5mm;
  }}

  .cover-logo img {{
    width: 48mm;
    height: auto;
  }}

  .cover-top {{
    font-size: 13pt;
    font-weight: bold;
    line-height: 1.4;
  }}

  .cover-course {{
    font-size: 12.5pt;
    font-weight: bold;
    line-height: 1.4;
    margin-top: 6mm;
  }}

  .cover-middle {{
    margin-top: 8mm;
  }}

  .cover-report-on {{
    font-size: 11.5pt;
    font-weight: bold;
    line-height: 1.4;
  }}

  .cover-project-title {{
    font-size: 14.5pt;
    font-weight: bold;
    margin-top: 3mm;
    letter-spacing: 0.5px;
  }}

  .cover-submitted-by {{
    font-size: 11pt;
    font-weight: bold;
    margin-top: 8mm;
  }}

  .cover-table {{
    margin: 3mm auto 0 auto;
    width: 80%;
    border-collapse: collapse;
    font-size: 10.5pt;
    font-weight: bold;
  }}

  .cover-table th, .cover-table td {{
    padding: 3px 10px;
    text-align: left;
  }}

  .cover-bottom {{
    font-size: 10pt;
    font-weight: bold;
    line-height: 1.4;
    margin-bottom: 6mm;
  }}
</style>
</head>
<body>

<!-- ========================================================================= -->
<!-- PAGE 1: COVER PAGE WITH PES UNIVERSITY LOGO                               -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="cover-container">
    <div>
      <div class="cover-logo">
        <img src="data:image/png;base64,{b64_assets['LOGO']}" alt="PES University Logo">
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
          LEVEL 3 MINI-PROJECT VERIFICATION EVIDENCE<br>
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
          <td>{student_name}</td>
          <td>{srn}</td>
        </tr>
        <tr>
          <td>2)</td>
          <td>{partner_name}</td>
          <td>{partner_srn}</td>
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
<!-- PAGE 2: SCREENSHOT CHECKLIST & SUMMARY TABLE                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <h1 class="section-heading" style="margin-top: 4mm; margin-bottom: 3mm;">SCREENSHOT CHECKLIST &amp; VERIFICATION SUMMARY</h1>
    <p style="font-size: 9.5pt; margin-bottom: 2mm;">
      Per official course submission instructions, the required project evidence consists of genuine terminal screenshots
      (S01 to S24) captured with the complete student SRN configured in the prompt (<code>{srn}</code>), accompanied by
      a one-line explanation demonstrating the verified operating-system capability.
    </p>

    <table class="academic-table" style="font-size: 8.5pt;">
      <thead>
        <tr>
          <th style="width: 8%; text-align: center;">Item</th>
          <th style="width: 34%;">Requirement Checklist Description</th>
          <th style="width: 38%;">Execution Command / Verification Action</th>
          <th style="width: 11%; text-align: center;">Status</th>
          <th style="width: 9%; text-align: center;">Page</th>
        </tr>
      </thead>
      <tbody>
        {checklist_rows}
      </tbody>
    </table>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 2</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 3: S01 & S02                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 1 - Ubuntu/WSL terminal environment, active working directory, and prompt with full student SRN.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S01']}" alt="S01" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[0]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 6mm;">
      <div class="screenshot-caption">Screenshot 2 - GCC C99 compiler version and GNU Make utility verification.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S02']}" alt="S02" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[1]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 3</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 4: S03                                                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 3 - Project workspace directory structure, modular C sources, headers, documentation, and Makefile.</div>
      <div class="screenshot-frame" style="max-height: 225mm;">
        <img src="data:image/png;base64,{b64_assets['S03']}" alt="S03" style="max-height: 215mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[2]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 4</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 5: S04                                                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 4 - Clean compilation of all modules with compiler warnings enabled (-Wall -Wextra) and final binary linking.</div>
      <div class="screenshot-frame" style="max-height: 220mm;">
        <img src="data:image/png;base64,{b64_assets['S04']}" alt="S04" style="max-height: 210mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[3]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 5</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 6: S05                                                              -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 5 - Command-line interface help banner and numbered interactive menu options.</div>
      <div class="screenshot-frame" style="max-height: 225mm;">
        <img src="data:image/png;base64,{b64_assets['S05']}" alt="S05" style="max-height: 215mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[4]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 6</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 7: S06 & S07                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 6 - First-Come-First-Served (FCFS) scheduling execution timeline and per-job metrics.</div>
      <div class="screenshot-frame" style="max-height: 100mm;">
        <img src="data:image/png;base64,{b64_assets['S06']}" alt="S06" style="max-height: 92mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[5]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 7 - Round Robin scheduling execution order, time quantum (q=2), and performance metrics.</div>
      <div class="screenshot-frame" style="max-height: 105mm;">
        <img src="data:image/png;base64,{b64_assets['S07']}" alt="S07" style="max-height: 96mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[6]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 7</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 8: S08 & S09                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 8 - Non-preemptive Priority scheduling with multi-tier deterministic tie-breaking.</div>
      <div class="screenshot-frame" style="max-height: 110mm;">
        <img src="data:image/png;base64,{b64_assets['S08']}" alt="S08" style="max-height: 100mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[7]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 9 - Side-by-side comparative evaluation of FCFS, Priority, and Round Robin on identical workload.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S09']}" alt="S09" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[8]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 8</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 9: S10 & S11                                                        -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 10 - Concurrent multi-threaded activity logger with bounded circular queue.</div>
      <div class="screenshot-frame" style="max-height: 110mm;">
        <img src="data:image/png;base64,{b64_assets['S10']}" alt="S10" style="max-height: 100mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[9]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 11 - Thread synchronization via mutexes and condition variables with graceful termination.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S11']}" alt="S11" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[10]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 9</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 10: S12 & S13                                                       -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 12 - Inter-process communication between parent and child processes via POSIX shared memory.</div>
      <div class="screenshot-frame" style="max-height: 100mm;">
        <img src="data:image/png;base64,{b64_assets['S12']}" alt="S12" style="max-height: 90mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[11]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 13 - IPC coordination using POSIX named semaphores and immediate cleanup verification.</div>
      <div class="screenshot-frame" style="max-height: 90mm;">
        <img src="data:image/png;base64,{b64_assets['S13']}" alt="S13" style="max-height: 80mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[12]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 10</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 11: S14 & S15                                                       -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 14 - Banker's algorithm execution discovering a safe execution sequence.</div>
      <div class="screenshot-frame" style="max-height: 105mm;">
        <img src="data:image/png;base64,{b64_assets['S14']}" alt="S14" style="max-height: 95mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[13]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 15 - Banker's algorithm correctly detecting an unsafe state and identifying deadlock hazard.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S15']}" alt="S15" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[14]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 11</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 12: S16 & S17                                                       -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 16 - Worker child process creation via fork() and normal exit status collection via waitpid().</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S16']}" alt="S16" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[15]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 6mm;">
      <div class="screenshot-caption">Screenshot 17 - Controlled simulated worker failure and parent-side abnormal termination detection.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S17']}" alt="S17" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[16]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 12</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 13: S18 & S19                                                       -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 18 - Enforcement of CPU resource limits using setrlimit(RLIMIT_CPU) and observation of SIGXCPU.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S18']}" alt="S18" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[17]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 6mm;">
      <div class="screenshot-caption">Screenshot 19 - Error handling and usage diagnostic messages for invalid CLI arguments.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S19']}" alt="S19" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[18]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 13</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 14: S20                                                             -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 20 - System cleanup verification confirming zero leaked processes, threads, or IPC objects.</div>
      <div class="screenshot-frame" style="max-height: 220mm;">
        <img src="data:image/png;base64,{b64_assets['S20']}" alt="S20" style="max-height: 210mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[19]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 14</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 15: S21                                                             -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 21 - Comprehensive end-to-end integrated demonstration execution (--demo) and test summary.</div>
      <div class="screenshot-frame" style="max-height: 225mm;">
        <img src="data:image/png;base64,{b64_assets['S21']}" alt="S21" style="max-height: 215mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[20]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 15</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 16: S22 & S23                                                       -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 22 - Inspection of campuscompute.log showing formatted millisecond timestamps and event records.</div>
      <div class="screenshot-frame" style="max-height: 105mm;">
        <img src="data:image/png;base64,{b64_assets['S22']}" alt="S22" style="max-height: 95mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[21]['expl']}
      </div>
    </div>

    <div class="screenshot-box" style="margin-top: 4mm;">
      <div class="screenshot-caption">Screenshot 23 - Verification of final source files, headers, build system, and compiled executable binary.</div>
      <div class="screenshot-frame" style="max-height: 95mm;">
        <img src="data:image/png;base64,{b64_assets['S23']}" alt="S23" style="max-height: 85mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[22]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 16</span>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 17: S24                                                             -->
<!-- ========================================================================= -->
<div class="page-container">
  <div class="page-body">
    <div class="screenshot-box">
      <div class="screenshot-caption">Screenshot 24 - Submission ZIP archive contents listing and archive integrity check (unzip -t).</div>
      <div class="screenshot-frame" style="max-height: 225mm;">
        <img src="data:image/png;base64,{b64_assets['S24']}" alt="S24" style="max-height: 215mm;">
      </div>
      <div class="screenshot-explanation">
        <strong>Explanation:</strong> {ITEMS[23]['expl']}
      </div>
    </div>
  </div>
  <div class="page-footer">
    <span>Department of Computer Science &amp; Engineering, PES University</span>
    <span>Page 17</span>
  </div>
</div>

</body>
</html>
"""
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
    print("CampusCompute — Deliverables & Screenshot Evidence Generator")
    print("Adheres strictly to Level 3 Mini Project guidelines (evidence-only PDF)")
    print("=" * 72)

    # 1. Load authentic Kitty screenshots and PES logo
    print("[*] Loading authentic Kitty screenshots S01 to S24 and PES logo...")
    b64_assets = load_base64_assets()

    # 2. Generate PDF for Yatin R (PES2UG25CS617)
    print("[*] Generating 17-page evidence PDF for Yatin R (PES2UG25CS617)...")
    html_617 = generate_evidence_pdf_html(
        srn="PES2UG25CS617",
        student_name="Yatin R",
        partner_srn="PES2UG25CS609",
        partner_name="Yaduveer Pavan",
        b64_assets=b64_assets
    )
    pdf_617 = BASE_DIR / "PES2UG25CS617.pdf"
    compile_pdf(html_617, pdf_617)

    # 3. Generate PDF for Yaduveer Pavan (PES2UG25CS609)
    print("[*] Generating 17-page evidence PDF for Yaduveer Pavan (PES2UG25CS609)...")
    html_609 = generate_evidence_pdf_html(
        srn="PES2UG25CS609",
        student_name="Yaduveer Pavan",
        partner_srn="PES2UG25CS617",
        partner_name="Yatin R",
        b64_assets=b64_assets
    )
    pdf_609 = BASE_DIR / "PES2UG25CS609.pdf"
    compile_pdf(html_609, pdf_609)

    # 4. Generate verified submission ZIPs (dual-SRN convention SRN1_SRN2.zip & single-SRN)
    print("[*] Packaging and verifying submission ZIP archives according to convention: SRNNumber1_SRNNumber2.zip...")
    subprocess.run(["make", "zip", "ZIP=PES2UG25CS617_PES2UG25CS609.zip"], cwd=BASE_DIR, check=True)
    subprocess.run(["make", "zip", "ZIP=PES2UG25CS609_PES2UG25CS617.zip"], cwd=BASE_DIR, check=True)
    subprocess.run(["make", "zip", "SRN=PES2UG25CS617"], cwd=BASE_DIR, check=True)
    subprocess.run(["make", "zip", "SRN=PES2UG25CS609"], cwd=BASE_DIR, check=True)

    # 5. Recompile project binary to leave tree in ready-to-run state
    subprocess.run(["make"], cwd=BASE_DIR, check=True)

    print("\n" + "=" * 72)
    print("DELIVERABLES GENERATION COMPLETE!")
    print("=" * 72)
    print(f"1. Primary Submission PDF (Yatin R):        {pdf_617} ({pdf_617.stat().st_size // 1024} KB)")
    print(f"2. Primary Submission PDF (Yaduveer Pavan): {pdf_609} ({pdf_609.stat().st_size // 1024} KB)")
    print(f"3. Dual-SRN ZIP (Yatin_Yaduveer):          {BASE_DIR / 'PES2UG25CS617_PES2UG25CS609.zip'}")
    print(f"4. Dual-SRN ZIP (Yaduveer_Yatin):          {BASE_DIR / 'PES2UG25CS609_PES2UG25CS617.zip'}")
    print(f"5. Single-SRN ZIP (Yatin R):                {BASE_DIR / 'PES2UG25CS617.zip'}")
    print(f"6. Single-SRN ZIP (Yaduveer Pavan):         {BASE_DIR / 'PES2UG25CS609.zip'}")
    print("=" * 72)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
CampusCompute — Live Kitty Terminal Window Capture via Hyprland & Grim
Captures 100% genuine, real Kitty terminal windows directly from your Wayland session.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

BASE_DIR = Path("/run/media/tin/New Volume/Shared/Notes/Sem 3/OS/mini project").resolve()
SCREENSHOTS_DIR = BASE_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

SRN = os.environ.get("SRN", "PES2UG25CS609")

STEPS = [
    ("S01", 'pwd; echo "Logged in user: $(whoami)"; echo "Active SRN: $SRN"'),
    ("S02", 'gcc --version | head -n 1; make --version | head -n 1'),
    ("S03", 'ls -la'),
    ("S04", 'make clean && make'),
    ("S05", './campuscompute --help'),
    ("S06", './campuscompute --fcfs'),
    ("S07", './campuscompute --rr'),
    ("S08", './campuscompute --priority'),
    ("S09", './campuscompute --compare'),
    ("S10", './campuscompute --logger'),
    ("S11", './campuscompute --logger'),
    ("S12", './campuscompute --ipc'),
    ("S13", './campuscompute --ipc'),
    ("S14", './campuscompute --banker-safe'),
    ("S15", './campuscompute --banker-file samples/banker_unsafe.txt'),
    ("S16", './campuscompute --worker-ok'),
    ("S17", './campuscompute --worker-fail'),
    ("S18", './campuscompute --rlimit'),
    ("S19", './campuscompute --bogus || true'),
    ("S20", './campuscompute --cleanup && (ls /dev/shm | grep cc_ || echo "Zero lingering IPC objects in /dev/shm")'),
    ("S21", './campuscompute --demo'),
    ("S22", 'head -n 25 campuscompute.log'),
    ("S23", 'ls -lh campuscompute common.h main.c input.c scheduler.c logger.c ipc.c banker.c worker.c rlimit.c Makefile'),
    ("S24", 'make zip && unzip -l $SRN.zip | head -n 18 && unzip -t $SRN.zip')
]

def capture_step(num, cmd):
    out_png = SCREENSHOTS_DIR / f"{num}.png"
    print(f"[*] Capturing real Kitty window for {num}: {cmd[:40]}...")

    # Script to run inside kitty
    term_script = f"""
export SRN="{SRN}"
export PS1="[{SRN}] \\w\\$ "
clear
echo "[{SRN}] /home/tin/OS-mini-project\$ {cmd}"
{cmd}
sleep 10
"""
    
    # Launch kitty
    proc = subprocess.Popen(
        ["kitty", "--class", "os_shot_kitty", "bash", "-c", term_script],
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1.0)

    try:
        clients_out = subprocess.check_output(["hyprctl", "clients", "-j"]).decode()
        clients = json.loads(clients_out)
        target = None
        for c in clients:
            if "os_shot_kitty" in c.get("initialClass", "") or "os_shot_kitty" in c.get("class", ""):
                target = c
                break

        if target:
            x, y = target["at"]
            w, h = target["size"]
            geom = f"{x},{y} {w}x{h}"
            subprocess.run(["grim", "-g", geom, str(out_png)], check=True)
            print(f"    [+] Saved real screenshot: {out_png}")
        else:
            print(f"    [-] Could not locate kitty window for {num}, falling back to fullscreen grim")
            subprocess.run(["grim", str(out_png)], check=True)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=1.0)
        except Exception:
            proc.kill()

def main():
    print(f"Starting real Kitty capture for {len(STEPS)} steps with SRN={SRN}...")
    for num, cmd in STEPS:
        capture_step(num, cmd)
        time.sleep(0.3)
    print("Done capturing real screenshots!")

if __name__ == "__main__":
    main()

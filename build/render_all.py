import subprocess, os, sys, time

PY = r"C:\Users\HP\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
BUILD = r"C:\Users\HP\WorkBuddy\2026-10-20-13-13-49\build"
RENDER = os.path.join(BUILD, "render.py")

jobs = [
    ("photosynthesis", os.path.join(BUILD, "photosynthesis_script.json"),
     os.path.join(BUILD, "photosynthesis_1080p.mp4"), "0.5"),
    ("sleep_90s", os.path.join(BUILD, "sleep_script.json"),
     os.path.join(BUILD, "sleep_90s_v2.mp4"), "0.6"),
]

for name, script, out, fade in jobs:
    print(f"=== RENDER {name} -> {out}", flush=True)
    t0 = time.time()
    r = subprocess.run([PY, RENDER, "--script", script, "--out", out,
                        "--w", "1920", "--h", "1080", "--fps", "30", "--fade", fade])
    dt = time.time() - t0
    print(f"=== {name} exit={r.returncode} in {dt:.1f}s", flush=True)
    if r.returncode != 0:
        sys.exit(r.returncode)

# 报告时长
for _, _, out, _ in jobs:
    dur = subprocess.run(
        [r"C:\Users\HP\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffprobe.exe",
         "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out],
        capture_output=True, text=True).stdout.strip()
    print(f"DURATION {os.path.basename(out)} = {dur}s", flush=True)
print("ALL DONE", flush=True)

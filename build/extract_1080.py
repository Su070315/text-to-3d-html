import subprocess, os

FFMPEG = r"C:/Users/HP/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.2-full_build/bin/ffmpeg.exe"
BUILD = r"C:\Users\HP\WorkBuddy\2026-10-20-13-13-49\build"
OUTDIR = os.path.join(BUILD, "v2_frames_1080")
os.makedirs(OUTDIR, exist_ok=True)

# (source, time)
jobs = [
    ("photosynthesis_1080p.mp4", 41.75, "photo_network"),
    ("sleep_90s_v2.mp4", 34.55, "sleep_battery"),
    ("sleep_90s_v2.mp4", 47.95, "sleep_hex"),
    ("sleep_90s_v2.mp4", 7.75, "sleep_figure"),
]
for src, t, name in jobs:
    out = os.path.join(OUTDIR, f"{name}.jpg")
    cmd = [FFMPEG, "-y", "-v", "error", "-ss", f"{t:.2f}", "-i",
           os.path.join(BUILD, src), "-frames:v", "1", out]
    subprocess.run(cmd, check=True)
    print(f"{name:16s} {src} t={t:.2f}s -> {os.path.getsize(out)} bytes")

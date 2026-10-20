import subprocess, os

FFMPEG = r"C:/Users/HP/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.2-full_build/bin/ffmpeg.exe"
SRC = r"C:\Users\HP\WorkBuddy\2026-10-20-13-13-49\build\photo_v2_small.mp4"
OUTDIR = r"C:\Users\HP\WorkBuddy\2026-10-20-13-13-49\build\v2_frames"

# 实际合并时间轴 = 累加时长 - (i+1)*fade，fade=0.5
durs = [4.0, 6.0, 6.0, 6.0, 7.0, 7.0, 6.0, 7.0, 4.0]
fade = 0.5
starts, ends, acc = [], [], 0.0
for i, d in enumerate(durs):
    acc += d
    starts.append(acc - d - i * fade)   # = sum(durs[0..i-1]) - i*fade
    ends.append(acc - (i + 1) * fade)
def mid(i):
    return (starts[i] + ends[i]) / 2

times = {
    "icon_ch1": mid(1),
    "flow_ch2": mid(2),
    "icon_ch3": mid(3),
    "timeline_ch4": mid(4),
    "flow_ch5": mid(5),
    "network_ch7": mid(7),
}
os.makedirs(OUTDIR, exist_ok=True)
for name, t in times.items():
    out = os.path.join(OUTDIR, f"{name}.jpg")
    cmd = [FFMPEG, "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", SRC, "-frames:v", "1", out]
    subprocess.run(cmd, check=True)
    print(f"{name:14s} t={t:6.2f}s  {os.path.getsize(out)} bytes")

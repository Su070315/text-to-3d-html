import subprocess, os

FFMPEG = r"C:/Users/HP/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.2-full_build/bin/ffmpeg.exe"
SRC = r"C:/Users/HP/Desktop/20549fb7b180fc317995c952d1f68b5d.mp4"
OUT = r"C:/Users/HP/WorkBuddy/2026-10-20-13-13-49/ref_frames"
os.makedirs(OUT, exist_ok=True)

for t in [0, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 94]:
    dst = os.path.join(OUT, f"f_{t}.jpg")
    cmd = [FFMPEG, "-y", "-v", "error", "-ss", str(t), "-i", SRC,
           "-frames:v", "1", "-vf", "scale=360:-1", dst]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(t, "OK" if os.path.exists(dst) and os.path.getsize(dst) > 0 else f"FAIL {r.stderr[:120]}")
print("done", os.listdir(OUT))

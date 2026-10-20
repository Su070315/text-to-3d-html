import os, subprocess
FFMPEG = r"C:/Users/HP/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.2-full_build/bin/ffmpeg.exe"
src = r"C:/Users/HP/WorkBuddy/2026-10-20-13-13-49/build/demo_small.mp4"
out = r"C:/Users/HP/WorkBuddy/2026-10-20-13-13-49/build/vfy"
os.makedirs(out, exist_ok=True)
for t in [2.5, 6.5, 10.5, 14.5, 18.5]:
    dst = os.path.join(out, f"v_{t}.jpg")
    subprocess.run([FFMPEG, "-y", "-v", "error", "-ss", str(t), "-i", src,
                    "-frames:v", "1", dst], check=True)
    print(dst, os.path.exists(dst))

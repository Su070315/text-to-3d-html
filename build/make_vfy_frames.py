# -*- coding: utf-8 -*-
"""低分辨率逐章取样帧：用于版面/文字碰撞校验，不产出视频。"""
import importlib.util, json, os, sys
from PIL import Image, ImageDraw

BUILD = os.path.dirname(os.path.abspath(__file__))
RENDER = os.path.join(BUILD, "render.py")

script_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BUILD, "jurassic.json")
out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BUILD, "jurassic_vfy")
W, H = 960, 540

spec = importlib.util.spec_from_file_location("renderer", RENDER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

spec_data = json.load(open(script_path, encoding="utf-8"))
style = mod.resolve_style(spec_data)
R = mod.Renderer(W, H, 24)

os.makedirs(out_dir, exist_ok=True)
frames = []
for idx, ch in enumerate(spec_data["chapters"]):
    dur = float(ch["duration"])
    bg = R.make_bg(seed=1000 + idx * 7, style=style)
    R.make_ambient(seed=5000 + idx * 13)
    t = dur * 0.62
    frame = bg.copy()
    content = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    R._content = content
    dc = ImageDraw.Draw(content)
    R.draw_ambient(dc, t, style)
    R.draw_scene(dc, ch["scene"], t, dur, t / dur, style)
    R.draw_chrome(dc, ch, style)
    frame.alpha_composite(content)
    rgb = frame.convert("RGB")
    frames.append(rgb)
    rgb.save(os.path.join(out_dir, f"ch{idx:02d}.png"))

cols = 3
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (W * cols, H * rows), (0, 0, 0))
for i, f in enumerate(frames):
    sheet.paste(f, ((i % cols) * W, (i // cols) * H))
sheet.save(os.path.join(out_dir, "sheet.png"))
print("frames", len(frames), "->", out_dir)

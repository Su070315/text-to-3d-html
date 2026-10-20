#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
infographic-video-gen :: render.py  (v4 - 动态叙事 / 多元素互动)
================================================================
v4 目标：不再是"一张静态图 + 字幕"的 PPT，而是每帧都有多个元素在动、
在互相作用，用运动本身解释内容。

新增动效系统：
  * 环境粒子层：全片持续的漂浮微尘（每个镜头不同种子），画面永不静止
  * 声呐环 / 呼吸光晕：主体周围持续扩散
  * 绕轨卫星点：围绕主体的轨道粒子
  * 流动光点：沿连线/流程方向持续移动，表达"传输/因果"
  * 错峰入场：多元素依次出现（stagger），而不是整块同时出现
  * 数据增长：柱状图从 0 生长、数值渐显；折线逐段绘出
  * 关键字标签（tags）：围绕主体浮出的胶囊标签 + 细连线
"""
import os, sys, json, math, shutil, tempfile, argparse, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drawing

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

# ---------------- 字体 ----------------
def _pick_font(*cands):
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[0]

F_CN_B = _pick_font(r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf")
F_CN   = _pick_font(r"C:\Windows\Fonts\msyh.ttc",   r"C:\Windows\Fonts\simsun.ttc")
F_EN   = _pick_font(r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf")

def find_ffmpeg():
    p = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if p:
        return p
    for c in [
        r"C:/Users/HP/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1.2-full_build/bin/ffmpeg.exe",
        r"C:/ffmpeg/bin/ffmpeg.exe",
    ]:
        if os.path.exists(c):
            return c
    raise RuntimeError("找不到 ffmpeg，请设置 FFMPEG 环境变量")

FFMPEG = find_ffmpeg()

def _find_ffprobe():
    p = os.environ.get("FFPROBE") or shutil.which("ffprobe")
    if p:
        return p
    cand = os.path.join(os.path.dirname(FFMPEG), "ffprobe" + (os.path.splitext(FFMPEG)[1] or ".exe"))
    return cand if os.path.exists(cand) else "ffprobe"

FFPROBE = _find_ffprobe()

ACCENTS = {
    "amber": (245, 185, 66),
    "cyan":  (91, 214, 232),
    "teal":  (60, 205, 180),
    "gold":  (240, 200, 110),
    "violet":(150, 150, 240),
    "rose":  (232, 120, 140),
    "green": (120, 200, 110),
    "ember": (255, 140, 60),
}
WHITE = (255, 255, 255)

def lerp(a, b, t): return a + (b - a) * t
def clamp01(x): return max(0.0, min(1.0, x))
def ease_out(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3
def ease_in_out(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)
def stagger(t, i, start=0.15, step=0.28, dur=0.5):
    return ease_out((t - (start + i * step)) / dur)


# ---------------- 风格 ----------------
DEFAULT_STYLE = {
    "palette": {"bg_top": [7, 10, 22], "bg_mid": [10, 17, 40], "bg_bot": [2, 3, 9],
                "glow": ACCENTS["amber"], "vignette": 0.55},
    "bg": "deep-space",
    "accents": ["amber", "cyan"],
    "typeface": "sans",
}

def resolve_style(script):
    s = script.get("style") or {}
    pal = dict(DEFAULT_STYLE["palette"])
    pal.update(s.get("palette") or {})
    glow = pal.get("glow")
    if isinstance(glow, str):
        pal["glow"] = ACCENTS.get(glow, ACCENTS["amber"])
    accents = [ACCENTS.get(a, ACCENTS["amber"]) if isinstance(a, str) else a
               for a in (s.get("accents") or DEFAULT_STYLE["accents"])]
    top = pal["bg_top"]
    lum = 0.299 * top[0] + 0.587 * top[1] + 0.114 * top[2]
    return {
        "palette": pal, "bg": s.get("bg", "deep-space"), "accents": accents,
        "text_main": (18, 22, 30) if lum > 120 else WHITE,
        "text_dim": (120, 128, 145) if lum > 120 else (138, 148, 166),
        "text_note": (90, 98, 115) if lum > 120 else (176, 184, 198),
        "typeface": s.get("typeface", "sans"),
    }


class Renderer:
    def __init__(self, W, H, fps):
        self.W, self.H, self.fps = W, H, fps
        self.S = min(W, H)
        self._sc = ImageDraw.Draw(Image.new("L", (8, 8)))
        self._fc = {}
        self._glow_cache = {}
        self._content = None
        self._ambient_p = []
        self.vignette_base = self._make_vignette()

    def font(self, path, size):
        k = (path, size)
        if k not in self._fc:
            self._fc[k] = ImageFont.truetype(path, size, index=0)
        return self._fc[k]

    def meas(self, s, font):
        return self._sc.textlength(s, font=font)

    def bg_color(self, style):
        return tuple(style["palette"]["bg_mid"])

    # ---------- 背景 ----------
    def _make_vignette(self):
        W, H = self.W, self.H
        yy, xx = np.mgrid[0:H, 0:W]
        nx = (xx - W / 2) / (W / 2); ny = (yy - H / 2) / (H / 2)
        d = np.sqrt(nx * nx + ny * ny) / 1.414
        return 1.0 - 0.55 * np.clip(d * 1.15, 0, 1) ** 2

    def make_bg(self, seed, style):
        W, H = self.W, self.H
        pal = style["palette"]
        top = np.array(pal["bg_top"], float)
        mid = np.array(pal["bg_mid"], float)
        bot = np.array(pal["bg_bot"], float)
        ys = np.linspace(0, 1, H)
        t1 = np.clip(ys / 0.5, 0, 1); t2 = np.clip((ys - 0.5) / 0.5, 0, 1)
        below = ys < 0.5
        col = np.where(below[:, None], top + (mid - top) * t1[:, None],
                       mid + (bot - mid) * t2[:, None])
        arr = np.repeat(col[:, None, :], W, axis=1)
        glow = np.array(pal["glow"], float)
        yy, xx = np.mgrid[0:H, 0:W]
        cx, cy = W * 0.5, H * 0.55
        d = np.sqrt(((xx - cx) / W) ** 2 + ((yy - cy) / H) ** 2)
        g = np.clip(1 - d * 1.5, 0, 1) ** 2 * 0.11
        arr += glow[None, None, :] * g[..., None]
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
        self._bg_decor(img, style["bg"], seed, style)
        vig = pal.get("vignette", 0.55)
        if vig:
            arr2 = np.array(img)[:, :, :3].astype(float)
            arr2 *= self.vignette_base[..., None] * vig + (1 - vig)
            img = Image.fromarray(np.clip(arr2, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
        return img

    def _bg_decor(self, img, bg, seed, style):
        rng = np.random.default_rng(seed)
        d = ImageDraw.Draw(img)
        W, H = self.W, self.H
        if bg == "deep-space":
            n = 170
            xs = rng.integers(0, W, n); ys = rng.integers(0, int(H * 0.95), n)
            b = rng.uniform(8, 42, n)
            for x, y, bb in zip(xs, ys, b):
                img.putpixel((int(x), int(y)), (int(bb),) * 3 + (255,))
        elif bg == "ember":
            for _ in range(80):
                x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
                self._content = img
                self.paste_glow(d, (x, y), rng.uniform(2, 6), (255, 150, 70), alpha=120, power=2.0)
            self._content = None
        elif bg == "organic":
            cols = [(80, 200, 150), (120, 200, 110), (60, 205, 180)]
            for _ in range(7):
                c = (int(rng.integers(0, W)), int(rng.integers(int(H * 0.2), int(H * 0.9))))
                r = rng.uniform(self.S * 0.10, self.S * 0.30)
                self._content = img
                self.paste_glow(d, c, r, tuple(int(v) for v in cols[int(rng.integers(0, 3))]), alpha=55, power=2.4)
            for _ in range(50):
                img.putpixel((int(rng.integers(0, W)), int(rng.integers(0, H))), (150, 220, 170, 200))
            self._content = None
        elif bg == "grid":
            step = W / 16
            for i in range(1, 16):
                d.line([(i * step, 0), (i * step, H)], fill=(120, 140, 170, 22), width=1)
            for j in range(1, int(H / step)):
                d.line([(0, j * step), (W, j * step)], fill=(120, 140, 170, 22), width=1)
        elif bg == "calm":
            for _ in range(12):
                c = (int(rng.integers(0, W)), int(rng.integers(0, H)))
                r = rng.uniform(self.S * 0.05, self.S * 0.18)
                self._content = img
                self.paste_glow(d, c, r, (230, 230, 240), alpha=40, power=2.6)
            self._content = None
        elif bg == "clinical":
            step = W / 20
            for i in range(1, 20):
                d.line([(i * step, 0), (i * step, H)], fill=(150, 160, 175, 26), width=1)
            for j in range(1, int(H / step)):
                d.line([(0, j * step), (W, j * step)], fill=(150, 160, 175, 26), width=1)

    # ---------- 光晕 ----------
    def glow(self, size, color, power=2.0):
        size = max(16, (int(size) // 8) * 8)
        key = (size, tuple(color), power)
        img = self._glow_cache.get(key)
        if img is None:
            y, x = np.ogrid[-1:1:size * 1j, -1:1:size * 1j]
            dd = np.sqrt(x * x + y * y)
            a = np.clip(1 - dd, 0, 1) ** power
            arr = np.zeros((size, size, 4), np.uint8)
            arr[..., 0] = color[0]; arr[..., 1] = color[1]; arr[..., 2] = color[2]
            arr[..., 3] = (a * 255).astype(np.uint8)
            img = Image.fromarray(arr, "RGBA")
            self._glow_cache[key] = img
        return img

    def paste_glow(self, _dst, center, radius, color, alpha=140, power=2.0):
        sp = self.glow(int(radius * 2), color, power)
        if alpha < 255:
            sp = sp.copy()
            sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha / 255)))
        self._content.alpha_composite(sp, (int(center[0] - radius), int(center[1] - radius)))

    # ---------- 文本 ----------
    def text_c(self, dc, xy, s, font, fill):
        dc.text(xy, s, font=font, fill=fill, anchor="mm")

    def tracked(self, dc, xy, s, font, fill, tracking=0.0, center=True):
        widths = [self.meas(ch, font) for ch in s]
        total = sum(widths) + tracking * (max(1, len(s)) - 1)
        x = xy[0] - total / 2 if center else xy[0]
        for ch, w in zip(s, widths):
            dc.text((x, xy[1]), ch, font=font, fill=fill, anchor="lm")
            x += w + tracking

    def wrap(self, text, font, maxw):
        lines, cur = [], ""
        for ch in text:
            if not cur or self.meas(cur + ch, font) <= maxw:
                cur += ch
            else:
                lines.append(cur); cur = ch
        if cur: lines.append(cur)
        return lines

    # ---------- 图形原语 ----------
    def hexagon(self, dc, cx, cy, r, fill=None, outline=None, width=4):
        pts = [(cx + r * math.cos(math.pi / 180 * (60 * i - 30)),
                cy + r * math.sin(math.pi / 180 * (60 * i - 30))) for i in range(6)]
        dc.polygon(pts, fill=fill, outline=outline, width=width)

    def arrow(self, dc, x1, y, x2, color, w=5):
        dc.line([(x1, y), (x2 - 14, y)], fill=color, width=w)
        dc.line([(x2 - 14, y - 9), (x2, y), (x2 - 14, y + 9)], fill=color, width=w, joint="curve")

    def ring(self, dc, cx, cy, r, color, w=3):
        dc.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=w)

    def _glyph(self, dc, cx, cy, r, g, col):
        f = self.font(F_CN_B, int(r * 0.9))
        if g and len(g) <= 2:
            self.text_c(dc, (cx, cy), g, f, WHITE if sum(col) > 200 else col)
            return
        dc.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.28, cy + r * 0.28], fill=col)

    def _node(self, dc, cx, cy, r, col, it, t, bg):
        """节点：有 art 就画具体图形，否则回退到圆环+字。"""
        art = it.get("art")
        if art:
            drawing.draw_art(dc, art, cx, cy, r * 0.92, col, t, bg)
        else:
            self.ring(dc, cx, cy, r, col + (255,), w=4)
            self._glyph(dc, cx, cy, r, it.get("glyph", ""), col)

    # ---------- 动效原语 ----------
    def sonar(self, dc, cx, cy, base_r, color, t, n=2, speed=0.32):
        for k in range(n):
            ph = ((t * speed) + k / n) % 1.0
            rr = base_r * (1.02 + ph * 0.85)
            a = int(72 * (1 - ph))
            if a > 2:
                dc.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=color + (a,), width=3)

    def orbit_dots(self, dc, cx, cy, rx, ry, t, color, n=5, speed=0.5):
        for i in range(n):
            ang = t * (speed * 0.15 + 0.012 * i) * 6.0 + i * (2 * math.pi / n)
            x = cx + rx * math.cos(ang)
            y = cy + ry * math.sin(ang)
            r = 2.4 + (i % 3)
            dc.ellipse([x - r, y - r, x + r, y + r], fill=color + (165,))

    def rise_dots(self, dc, cx, cy, spread, height, t, color, n=6):
        for i in range(n):
            ph = ((t * 0.22) + i / n) % 1.0
            x = cx + math.sin(i * 2.1 + ph * 6.0) * spread
            y = cy + height * 0.5 - ph * height
            a = int(170 * (1 - ph) * (0.5 + 0.5 * math.sin(i + t)))
            if a > 8:
                dc.ellipse([x - 2, y - 2, x + 2, y + 2], fill=color + (a,))

    def dashed(self, dc, p1, p2, color, dash=14, gap=10, offset=0.0, width=3):
        x1, y1 = p1; x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        if L < 1: return
        ux, uy = dx / L, dy / L
        s = -(offset % (dash + gap))
        while s < L:
            a = max(0.0, s); b = min(L, s + dash)
            if b > a:
                dc.line([(x1 + ux * a, y1 + uy * a), (x1 + ux * b, y1 + uy * b)], fill=color, width=width)
            s += dash + gap

    def seg_dot(self, dc, p1, p2, t, color, n=2, speed=0.45, r=3, phase=0.0):
        x1, y1 = p1; x2, y2 = p2
        for k in range(n):
            u = ((t * speed + phase + k / n) % 1.0)
            x = x1 + (x2 - x1) * u
            y = y1 + (y2 - y1) * u
            a = int(220 * (0.35 + 0.65 * math.sin(u * math.pi)))
            dc.ellipse([x - r, y - r, x + r, y + r], fill=color + (max(40, a),))

    def pill(self, dc, cx, cy, text, font, fg, col, alpha):
        tw = self.meas(text, font)
        h = self.H * 0.042
        padx = h * 0.55
        w = tw + padx * 2
        dc.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=h / 2,
                             fill=col + (int(alpha * 0.16),), outline=col + (int(alpha),), width=2)
        self.text_c(dc, (cx, cy), text, font, fg + (int(alpha),))

    # ---------- 环境粒子层 ----------
    def make_ambient(self, seed):
        rng = np.random.default_rng(seed)
        W, H = self.W, self.H
        n = 38
        self._ambient_p = [dict(
            x=float(rng.integers(0, W)), y=float(rng.integers(0, H)),
            vx=float(rng.uniform(-7, 7)), vy=float(rng.uniform(-16, -5)),
            r=float(rng.uniform(1.2, 3.4)), a=int(rng.integers(18, 60)),
            ph=float(rng.uniform(0, 6.28))) for _ in range(n)]

    def draw_ambient(self, dc, t, style):
        W, H = self.W, self.H
        base = style["accents"][0]
        for p in self._ambient_p:
            x = (p["x"] + p["vx"] * t) % W
            y = (p["y"] + p["vy"] * t) % H
            tw = 0.55 + 0.45 * math.sin(t * 1.6 + p["ph"])
            a = int(p["a"] * tw)
            if a > 4:
                dc.ellipse([x - p["r"], y - p["r"], x + p["r"], y + p["r"]], fill=base + (a,))

    # ---------- 场景分派 ----------
    def draw_scene(self, dc, scene, t, dur, p, style):
        fn = getattr(self, "sc_" + scene.get("type", "icon"), self.sc_icon)
        fn(dc, scene, t, dur, p, style)

    def sc_title(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        cy = H * 0.44
        accent = style["accents"][0]
        self.paste_glow(dc, (W / 2, cy), S * (0.5 + 0.05 * math.sin(t * 1.2)), style["palette"]["glow"], alpha=60, power=2.4)
        self.sonar(dc, W / 2, cy, S * 0.30, accent, t, n=3, speed=0.22)
        self.text_c(dc, (W / 2, cy), s.get("title_cn", ""), self.font(F_CN_B, int(H * 0.062)), style["text_main"])
        en = s.get("title_en", "")
        if en:
            self.tracked(dc, (W / 2, cy + H * 0.075), en.upper(),
                         self.font(F_EN, int(H * 0.020)), accent, tracking=H * 0.006)
        lw = S * 0.08
        g = 0.6 + 0.4 * math.sin(t * 2.0)
        dc.line([(W / 2 - lw, cy + H * 0.115), (W / 2 + lw, cy + H * 0.115)], fill=accent + (int(120 + 120 * g),), width=3)
        self.seg_dot(dc, (W / 2 - lw, cy + H * 0.115), (W / 2 + lw, cy + H * 0.115), t, accent, n=1, speed=0.5, r=3)

    def sc_figure(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        accent = style["accents"][0]
        cx, cy = W / 2, H * 0.47
        hr = H * 0.036; bw, bh = S * 0.155, H * 0.205
        top = cy - bh / 2; head_cy = top + hr; gap = hr * 0.38
        torso_top = top + 2 * hr + gap; torso_h = bh - 2 * hr - gap
        self.paste_glow(dc, (cx, cy), S * 0.42, accent, alpha=70, power=2.2)
        self.sonar(dc, cx, cy, S * 0.24, accent, t, n=2, speed=0.3)
        self.orbit_dots(dc, cx, cy, S * 0.30, S * 0.20, t, accent, n=6, speed=1.0)
        dc.ellipse([cx - hr, head_cy - hr, cx + hr, head_cy + hr], fill=(255, 255, 255, 238))
        dc.rounded_rectangle([cx - bw / 2, torso_top, cx + bw / 2, torso_top + torso_h],
                             radius=bw * 0.45, fill=(255, 255, 255, 238))
        cy_core = torso_top + torso_h * 0.42
        br = 0.5 + 0.5 * math.sin(t * 2.2)
        self.paste_glow(dc, (cx, cy_core), S * 0.10, accent, alpha=int(150 + 70 * br), power=1.7)
        core_r = S * 0.017 * (1 + 0.10 * br)
        dc.ellipse([cx - core_r, cy_core - core_r, cx + core_r, cy_core + core_r], fill=accent + (255,))
        if s.get("clock"):
            ox, oy, r = W * 0.80, H * 0.28, S * 0.045
            self.ring(dc, ox, oy, r, (120, 150, 160, 220), w=3)
            dc.line([(ox, oy), (ox, oy - r * 0.55)], fill=(160, 190, 200, 230), width=3)
            dc.line([(ox, oy), (ox + r * 0.45, oy)], fill=(160, 190, 200, 230), width=3)

    # ===== 单图主导 + 多元素互动 =====
    def sc_art(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        accent = style["accents"][0]
        art = s.get("art", "moon")
        sz = S * s.get("size", 0.22)
        bg = self.bg_color(style)
        cx = W / 2
        cy = H * 0.45 + math.sin(t * 0.9) * S * 0.008

        if s.get("bigtext"):
            self.text_c(dc, (cx, cy), s["bigtext"], self.font(F_CN_B, int(H * 0.22)),
                        style["palette"]["glow"] + (40,))

        self.sonar(dc, cx, cy, sz * 0.95, accent, t, n=3, speed=0.26)
        self.paste_glow(dc, (cx, cy), sz * (2.3 + 0.15 * math.sin(t * 1.6)), accent, alpha=95, power=2.2)
        drawing.draw_art(dc, art, cx, cy, sz, accent, t, bg)

        self.orbit_dots(dc, cx, cy, sz * 1.28, sz * 0.92, t, accent, n=7, speed=1.0)
        self.rise_dots(dc, cx, cy, sz * 0.65, sz * 1.9, t, accent, n=6)

        tags = s.get("tags") or []
        if tags:
            anchors = [(-1, -0.52), (1, -0.52), (-1, 0.54), (1, 0.54)]
            f_tag = self.font(F_CN, int(H * 0.017))
            for i, tg in enumerate(tags[:4]):
                ax, ay = anchors[i]
                local = stagger(t, i, start=0.45, step=0.28, dur=0.55)
                if local <= 0.01:
                    continue
                tx = cx + ax * (sz * 1.9 + (1 - local) * S * 0.05)
                ty = cy + ay * (sz * 1.55 + (1 - local) * S * 0.04)
                ex = cx + ax * sz * 0.75
                ey = cy + ay * sz * 0.55
                dc.line([(ex, ey), (tx, ty)], fill=accent + (int(70 * local),), width=2)
                dc.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=accent + (int(160 * local),))
                self.pill(dc, tx, ty, tg, f_tag, style["text_main"], accent, int(235 * local))

        if s.get("label"):
            self.text_c(dc, (cx, cy + sz * 1.2), s["label"],
                        self.font(F_CN_B, int(H * 0.022)), style["text_main"])
        if s.get("labelsub"):
            self.text_c(dc, (cx, cy + sz * 1.2 + H * 0.034), s["labelsub"],
                        self.font(F_CN, int(H * 0.015)), style["text_note"])

    # ===== 双图对比：滑入 + 流动箭头 =====
    def sc_compare(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        aA = style["accents"][0]; aB = style["accents"][1 % len(style["accents"])]
        arts = s.get("arts", [None, None]); labels = s.get("labels", ["", ""])
        cy = H * 0.45; sz = S * 0.17
        bg = self.bg_color(style)
        for i, (cx, col, art, lab) in enumerate([(W * 0.30, aA, arts[0], labels[0]), (W * 0.70, aB, arts[1], labels[1])]):
            local = stagger(t, i, start=0.1, step=0.25, dur=0.55)
            slide = (1 - local) * W * 0.06 * (-1 if i == 0 else 1)
            x = cx + slide
            y = cy + math.sin(t * 1.1 + i) * S * 0.006
            if art:
                self.paste_glow(dc, (x, y), sz * 2.1, col, alpha=int(95 * local), power=2.2)
                self.sonar(dc, x, y, sz * 0.9, col, t, n=2, speed=0.28)
                drawing.draw_art(dc, art, x, y, sz, col, t, bg)
                self.orbit_dots(dc, x, y, sz * 1.2, sz * 0.85, t, col, n=5, speed=0.9)
            if lab:
                self.text_c(dc, (x, y + sz * 1.3), lab, self.font(F_CN_B, int(H * 0.020)),
                            style["text_main"] + (int(255 * local),))
        ax1, ax2 = W * 0.5 - sz * 0.45, W * 0.5 + sz * 0.45
        self.dashed(dc, (ax1, cy), (ax2, cy), style["text_note"] + (200,), dash=10, gap=8, offset=t * 40, width=4)
        dc.line([(ax2 - 12, cy - 8), (ax2, cy), (ax2 - 12, cy + 8)], fill=style["text_note"] + (220,), width=4, joint="curve")
        self.seg_dot(dc, (ax1, cy), (ax2, cy), t, aB, n=2, speed=0.55, r=3)

    # ===== 数据图：生长动画 =====
    def sc_chart(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        accent = style["accents"][0]; accent2 = style["accents"][1 % len(style["accents"])]
        data = s.get("data", [])
        n = max(1, len(data))
        base_y = H * 0.64; top_y = H * 0.30
        x0 = W * 0.16; x1 = W * 0.84; span = x1 - x0
        bw = span / (n * 1.7)
        maxv = max((d.get("value", 1) for d in data), default=1) or 1
        grow = ease_out((t - 0.35) / 1.15)
        for k in range(1, 5):
            yy = base_y - (base_y - top_y) * k / 4
            dc.line([(x0, yy), (x1, yy)], fill=style["text_dim"] + (18,), width=1)
        dc.line([(x0, base_y), (x0 + (x1 - x0) * grow, base_y)], fill=style["text_note"] + (200,), width=2)

        if s.get("kind") == "line":
            pts = []
            for i, d in enumerate(data):
                cx = x0 + span * (i + 0.5) / n
                yy = base_y - (base_y - top_y) * (d["value"] / maxv)
                pts.append((cx, yy))
            k = max(1, int(len(pts) * grow))
            seg = pts[:k]
            if len(seg) >= 2:
                dc.line(seg, fill=accent, width=5, joint="curve")
            for (cx, yy), d in zip(pts[:k], data[:k]):
                dc.ellipse([cx - 7, yy - 7, cx + 7, yy + 7], fill=accent + (255,))
                if d.get("label"):
                    self.text_c(dc, (cx, base_y + H * 0.03), d["label"],
                                self.font(F_CN, int(H * 0.016)), style["text_note"] + (int(255 * grow),))
                if d.get("value_label"):
                    self.text_c(dc, (cx, yy - H * 0.030), d["value_label"],
                                self.font(F_CN_B, int(H * 0.016)), style["text_main"] + (int(255 * grow),))
            if seg:
                self.seg_dot(dc, seg[0], seg[-1] if len(seg) > 1 else seg[0], t, accent, n=1, speed=0.4, r=4)
            return

        for i, d in enumerate(data):
            col = ACCENTS.get(d.get("accent", ""), accent if i == 0 else accent2)
            cx = x0 + span * (i + 0.5) / n
            bh = (base_y - top_y) * (d["value"] / maxv) * grow
            if bh < 1: bh = 1
            self.paste_glow(dc, (cx, base_y - bh / 2), bw * 1.25, col, alpha=70, power=2.0)
            dc.rounded_rectangle([cx - bw / 2, base_y - bh, cx + bw / 2, base_y],
                                 radius=6, fill=col + (185,), outline=col + (255,), width=2)
            for k in range(2):
                u = ((t * 0.5) + k / 2) % 1.0
                py = base_y - bh * u
                dc.ellipse([cx - 2.5, py - 2.5, cx + 2.5, py + 2.5], fill=col + (int(170 * (1 - u)),))
            lab_a = int(255 * clamp01(grow * 1.2))
            if d.get("label"):
                self.text_c(dc, (cx, base_y + H * 0.03), d["label"],
                            self.font(F_CN, int(H * 0.016)), style["text_note"] + (lab_a,))
            if d.get("value_label"):
                self.text_c(dc, (cx, base_y - bh - H * 0.024), d["value_label"],
                            self.font(F_CN_B, int(H * 0.016)), style["text_main"] + (lab_a,))

    def sc_hex(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        items = s.get("items", [])[:3]
        n = max(1, len(items))
        cy = H * 0.46; r = S * 0.10; gap = W * 0.30
        startx = W / 2 - gap * (n - 1) / 2
        bg = self.bg_color(style)
        for i, it in enumerate(items):
            local = stagger(t, i, start=0.12, step=0.24, dur=0.5)
            if local <= 0.01:
                continue
            cx = startx + gap * i
            yy = cy + math.sin(t * 1.1 + i * 1.4) * S * 0.007
            col = ACCENTS.get(it.get("accent", "amber"), style["accents"][0])
            rr = r * (0.6 + 0.4 * local)
            self.paste_glow(dc, (cx, yy), rr * 2.1, col, alpha=int(90 * local), power=2.2)
            self.sonar(dc, cx, yy, rr * 0.95, col, t, n=2, speed=0.3)
            self.hexagon(dc, cx, yy, rr, fill=col + (int(35 * local),), outline=col + (int(255 * local),), width=4)
            if it.get("art"):
                drawing.draw_art(dc, it["art"], cx, yy, rr * 0.6, col, t, bg)
            else:
                self.text_c(dc, (cx, yy), it.get("label", ""), self.font(F_CN_B, int(H * 0.030)),
                            style["text_main"] + (int(255 * local),))
            if it.get("note"):
                self.text_c(dc, (cx, yy + rr * 1.35), it["note"], self.font(F_CN, int(H * 0.016)),
                            style["text_note"] + (int(255 * local),))
            self.orbit_dots(dc, cx, yy, rr * 1.35, rr * 1.1, t, col, n=4, speed=0.8)

    def sc_battery(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        accent = style["accents"][0]
        cy = H * 0.46
        cx1 = W * 0.32; r1 = S * 0.115
        self.paste_glow(dc, (cx1, cy), r1 * 2.0, accent, alpha=110, power=2.1)
        self.sonar(dc, cx1, cy, r1 * 0.95, accent, t, n=2, speed=0.3)
        self.ring(dc, cx1, cy, r1, accent + (255,), w=4)
        self._glyph(dc, cx1, cy, r1, s.get("glyph", "饿"), accent)
        self.orbit_dots(dc, cx1, cy, r1 * 1.3, r1 * 1.0, t, accent, n=5, speed=0.9)
        self.text_c(dc, (cx1, cy + r1 * 1.45), s.get("glyph_note", ""), self.font(F_CN, int(H * 0.015)), style["text_note"])
        bx, by = W * 0.62, cy; bw, bh = S * 0.20, S * 0.30
        dc.rounded_rectangle([bx, by - bh / 2, bx + bw, by + bh / 2], radius=10,
                             outline=style["text_main"] + (240,), width=4)
        dc.rectangle([bx + bw + 2, by - bh * 0.14, bx + bw + 12, by + bh * 0.14], fill=style["text_main"] + (240,))
        bars = 3; inner_pad = 8; seg_h = (bh - inner_pad * 2) / bars
        for i in range(bars):
            yy = by - bh / 2 + inner_pad + i * seg_h
            fill = accent + (255,) if i < 1 else (255, 255, 255, 28)
            dc.rounded_rectangle([bx + inner_pad, yy, bx + bw - inner_pad, yy + seg_h - 6], radius=4, fill=fill)

    # ===== 流程：流动光点 + 节点呼吸 =====
    def sc_flow(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        items = s.get("items", [])[:5]
        n = max(1, len(items))
        cy = H * 0.45; margin = W * 0.145
        span = W - margin * 2
        step = span / max(1, n - 1) if n > 1 else 0
        r = min(S * 0.070, span / (n * 1.75)) if n > 1 else S * 0.10
        xs = [margin + step * i for i in range(n)] if n > 1 else [W / 2]
        bg = self.bg_color(style)

        for i in range(n - 1):
            p1 = (xs[i] + r + 8, cy); p2 = (xs[i + 1] - r - 14, cy)
            self.dashed(dc, p1, p2, (150, 165, 185, 120), dash=12, gap=9, offset=t * 45, width=4)
            dc.line([(p2[0] - 10, cy - 8), (p2[0], cy), (p2[0] - 10, cy + 8)], fill=(150, 165, 185, 200), width=4, joint="curve")
            self.seg_dot(dc, p1, p2, t, (150, 185, 205), n=2, speed=0.4, r=3)

        for i, it in enumerate(items):
            local = stagger(t, i, start=0.1, step=0.2, dur=0.5)
            if local <= 0.01:
                continue
            cx = xs[i]
            yy = cy + math.sin(t * 1.3 + i * 1.2) * S * 0.006
            col = ACCENTS.get(it.get("accent", "cyan"), style["accents"][0])
            rr = r * (0.75 + 0.25 * local)
            self.paste_glow(dc, (cx, yy), rr * 1.9, col, alpha=int(100 * local), power=2.1)
            self._node(dc, cx, yy, rr, col, it, t, bg)
            self.text_c(dc, (cx, yy + rr * 1.55), it.get("label", ""), self.font(F_CN, int(H * 0.016)),
                        style["text_note"] + (int(255 * local),))

    # ===== 网络：脉冲沿辐条传输 =====
    def sc_network(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        accent = style["accents"][0]; accent2 = style["accents"][1 % len(style["accents"])]
        items = s.get("items", [])[:6]; n = max(1, len(items))
        hx, hy = W * 0.30, H * 0.47
        Rh = S * 0.105
        cx_col = W * 0.73
        rc = S * (0.058 if n <= 3 else 0.046)
        step = min(H * 0.19, H * 0.44 / max(1, n - 1)) if n > 1 else 0.0
        ys = [hy + (i - (n - 1) / 2) * step for i in range(n)]
        bg = self.bg_color(style)

        for i, (it, y) in enumerate(zip(items, ys)):
            col = ACCENTS.get(it.get("accent", "cyan"), accent2)
            a = (hx + Rh * 0.92, hy); b = (cx_col - rc * 1.18, y)
            dc.line([a, b], fill=col + (95,), width=3)
            self.seg_dot(dc, a, b, t, col, n=2, speed=0.35, r=3.2, phase=i * 0.17)
            local = stagger(t, i, start=0.15, step=0.16, dur=0.45)
            self.paste_glow(dc, (cx_col, y), rc * 1.9, col, alpha=int(80 * local), power=2.0)
            self._node(dc, cx_col, y, rc, col, it, t, bg)
            dc.text((cx_col + rc * 1.35, y), it.get("label", ""),
                    font=self.font(F_CN, int(H * 0.021)), fill=style["text_main"] + (int(255 * local),), anchor="lm")

        self.sonar(dc, hx, hy, Rh * 1.05, accent, t, n=3, speed=0.25)
        self.paste_glow(dc, (hx, hy), Rh * (1.85 + 0.15 * math.sin(t * 1.8)), accent, alpha=120, power=2.0)
        self._node(dc, hx, hy, Rh, accent, {"art": s.get("art"), "glyph": s.get("glyph", "")}, t, bg)
        self.text_c(dc, (hx, hy + Rh * 1.32), s.get("label", ""), self.font(F_CN_B, int(H * 0.022)), style["text_main"])

    def sc_split(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        aA = style["accents"][0]; aB = style["accents"][1 % len(style["accents"])]
        panels = s.get("panels", [{}, {}])[:2]
        cy = H * 0.46; r = S * 0.12
        bg = self.bg_color(style)
        for i, (pp, col) in enumerate(zip(panels, [aA, aB])):
            local = stagger(t, i, start=0.1, step=0.25, dur=0.5)
            cx = (W * 0.28 if i == 0 else W * 0.72) + (1 - local) * (-1 if i == 0 else 1) * W * 0.05
            yy = cy + math.sin(t * 1.1 + i) * S * 0.006
            self.paste_glow(dc, (cx, yy), r * 2.0, col, alpha=int(110 * local), power=2.1)
            self.sonar(dc, cx, yy, r * 0.95, col, t, n=2, speed=0.3)
            self._node(dc, cx, yy, r, col, pp, t, bg)
            self.text_c(dc, (cx, yy + r * 1.5), pp.get("label", ""), self.font(F_CN_B, int(H * 0.022)),
                        style["text_main"] + (int(255 * local),))
            self.text_c(dc, (cx, yy + r * 1.5 + H * 0.034), pp.get("note", ""), self.font(F_CN, int(H * 0.014)),
                        style["text_note"] + (int(255 * local),))
        self.dashed(dc, (W * 0.5 - r * 0.5, cy), (W * 0.5 + r * 0.5, cy), style["text_note"] + (200,),
                    dash=10, gap=8, offset=t * 40, width=5)

    def sc_timeline(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        items = s.get("items", [])[:6]; n = max(1, len(items))
        y = H * 0.5; margin = W * 0.10; span = W - margin * 2
        step = span / max(1, n - 1) if n > 1 else 0
        accent = style["accents"][0]
        xs = [margin + step * i for i in range(n)] if n > 1 else [W / 2]
        bg = self.bg_color(style)
        draw_p = ease_out((t - 0.2) / 1.0)
        dc.line([(xs[0], y), (xs[0] + (xs[-1] - xs[0]) * draw_p, y)], fill=accent + (200,), width=4)
        self.seg_dot(dc, (xs[0], y), (xs[-1], y), t, accent, n=2, speed=0.3, r=3)
        for i, (x, it) in enumerate(zip(xs, items)):
            local = stagger(t, i, start=0.25, step=0.18, dur=0.45)
            col = ACCENTS.get(it.get("accent", "cyan"), style["accents"][0])
            self.paste_glow(dc, (x, y), S * 0.06, col, alpha=int(90 * local), power=2.0)
            self._node(dc, x, y, S * 0.045, col, it, t, bg)
            self.text_c(dc, (x, y + S * 0.085), it.get("label", ""), self.font(F_CN, int(H * 0.015)),
                        style["text_note"] + (int(255 * local),))
            if it.get("year"):
                self.text_c(dc, (x, y - S * 0.10), it["year"], self.font(F_EN, int(H * 0.013)),
                            style["text_dim"] + (int(255 * local),))

    def sc_icon(self, dc, s, t, dur, p, style):
        W, H = self.W, self.H; S = self.S
        accent = style["accents"][0]
        cy = H * 0.46 + math.sin(t * 0.9) * S * 0.007; r = S * 0.13
        bg = self.bg_color(style)
        self.sonar(dc, W / 2, cy, r * 1.0, accent, t, n=2, speed=0.28)
        if s.get("art"):
            self.paste_glow(dc, (W / 2, cy), r * 2.2, accent, alpha=110, power=2.1)
            drawing.draw_art(dc, s["art"], W / 2, cy, r * 0.92, accent, t, bg)
        else:
            self.paste_glow(dc, (W / 2, cy), r * 2.0, accent, alpha=110, power=2.0)
            self.ring(dc, W / 2, cy, r, accent + (255,), w=4)
            self._glyph(dc, W / 2, cy, r, s.get("glyph", ""), accent)
        self.orbit_dots(dc, W / 2, cy, r * 1.3, r * 1.0, t, accent, n=5, speed=0.9)
        if s.get("label"):
            self.text_c(dc, (W / 2, cy + r * 1.5), s["label"], self.font(F_CN, int(H * 0.017)), style["text_note"])

    # ---------- 叠加层 ----------
    def draw_chrome(self, dc, ch, style):
        W, H = self.W, self.H
        tcol = style["text_main"]; dcol = style["text_dim"]; ncol = style["text_note"]
        no = str(ch.get("no", "")).zfill(2) if ch.get("no") not in (None, "") else ""
        label_cn = ch.get("label_cn", ""); label_en = (ch.get("label_en", "") or "").upper()
        parts = [x for x in [no, label_cn, label_en] if x]
        line = "   ".join(parts)
        is_title = (ch.get("scene") or {}).get("type") == "title"
        if line and not is_title:
            self.tracked(dc, (W / 2, H * 0.105), line, self.font(F_EN, int(H * 0.0135)), dcol,
                         tracking=H * 0.004, center=True)
        sub = ch.get("sub", ""); note = ch.get("note", "")
        if note:
            self.text_c(dc, (W / 2, H * 0.70), note, self.font(F_CN, int(H * 0.0165)), ncol)
        if sub:
            f_sub = self.font(F_CN_B, int(H * 0.0245))
            lines = self.wrap(sub, f_sub, W * 0.84)
            base_y = H * 0.755 if note else H * 0.735
            for i, ln in enumerate(lines):
                self.text_c(dc, (W / 2, base_y + i * H * 0.036), ln, f_sub, tcol)

    # ---------- 单章渲染 ----------
    def render_clip(self, ch, idx, out_clip, style):
        dur = float(ch.get("duration", 4.5))
        scene = ch.get("scene", {})
        bg = self.make_bg(seed=1000 + idx * 7, style=style)
        self.make_ambient(seed=5000 + idx * 13)
        n = max(1, int(round(dur * self.fps)))
        proc = subprocess.Popen(
            [FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
             "-s", f"{self.W}x{self.H}", "-r", str(self.fps), "-i", "-",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
             out_clip], stdin=subprocess.PIPE)
        try:
            for i in range(n):
                t = i / self.fps
                frame = bg.copy()
                content = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
                self._content = content
                dc = ImageDraw.Draw(content)
                self.draw_ambient(dc, t, style)
                self.draw_scene(dc, scene, t, dur, i / max(1, n - 1), style)
                self.draw_chrome(dc, ch, style)
                alpha = ease_out(t / 0.6) * (1 - ease_out(max(0.0, (t - (dur - 0.45)) / 0.45)))
                if alpha < 0.999:
                    m = content.getchannel("A").point(lambda v: int(v * alpha))
                    content.putalpha(m)
                frame.alpha_composite(content)
                proc.stdin.write(frame.convert("RGB").tobytes())
        finally:
            proc.stdin.close()
            proc.wait()
        return n


def probe_dur(p):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def merge_xfade(clips, out, fade):
    if len(clips) == 1:
        shutil.copy(clips[0], out); return
    durs = [probe_dur(c) for c in clips]
    fc, cur = [], "[0:v]"
    off = 0.0
    for i in range(len(clips) - 1):
        off += durs[i]
        o = off - (i + 1) * fade
        nxt = f"[v{i}]"
        fc.append(f"{cur}[{i+1}:v]xfade=transition=fade:duration={fade}:offset={max(0.0, o):.3f}{nxt}")
        cur = nxt
    args = [FFMPEG, "-y", "-v", "error"]
    for c in clips:
        args += ["-i", c]
    args += ["-filter_complex", ";".join(fc), "-map", cur, "-c:v", "libx264",
             "-pix_fmt", "yuv420p", "-crf", "18", out]
    subprocess.run(args, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--w", type=int, default=1920)
    ap.add_argument("--h", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--fade", type=float, default=0.6)
    a = ap.parse_args()

    with open(a.script, "r", encoding="utf-8") as f:
        spec = json.load(f)
    chapters = spec.get("chapters", [])
    if not chapters:
        raise SystemExit("脚本里没有 chapters")
    style = resolve_style(spec)

    R = Renderer(a.w, a.h, a.fps)
    tmp = tempfile.mkdtemp(prefix="infov_")
    clips = []
    try:
        for i, ch in enumerate(chapters):
            clip = os.path.join(tmp, f"ch{i}.mp4")
            n = R.render_clip(ch, i, clip, style)
            clips.append(clip)
            print(f"[{i+1}/{len(chapters)}] {ch.get('label_cn','')} {n}f -> {os.path.basename(clip)}", flush=True)
        merge_xfade(clips, a.out, a.fade)
        print("OK:", a.out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

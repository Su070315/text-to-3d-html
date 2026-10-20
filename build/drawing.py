#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
drawing.py  —  具体化的矢量插画库（infographic-video-gen 视觉语言 v3）
================================================================
目的：打破「一个圆圈 + 一个字」的固化表达。
这里提供一批 *可识别的、与内容相关的* 矢量图形（月亮、大脑、书、水滴、
垃圾桶、齿轮、盾牌、闪电、苹果、心、床、太阳、星星、叶子、波、原子、
齿轮、山、眼睛、天平、对勾、云、火、电池、时钟 …）。
每个图形按 (cx, cy, size) 居中绘制，size 约等于「半径」，整体跨度约 2*size。
颜色由调用方传入（accent），背景色 bg 仅用于「挖月牙」等镂空操作。
"""
import math

def _rgba(c, a=255):
    return (c[0], c[1], c[2], a)

def _ellipse_poly(cx, cy, rx, ry, rot=0.0, seg=48):
    pts = []
    c = math.cos(rot); s = math.sin(rot)
    for i in range(seg):
        th = 2 * math.pi * i / seg
        x = rx * math.cos(th); y = ry * math.sin(th)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts

# ---------------- 具体图形 ----------------

def _moon(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    R = size * 0.85
    dc.ellipse([cx - R, cy - R, cx + R, cy + R], fill=_rgba(color, 60), outline=a, width=4)
    # 挖出月牙：偏移的同半径圆
    dc.ellipse([cx + 0.5 * R - 0.95 * R, cy - 0.1 * R - 0.95 * R,
                cx + 0.5 * R + 0.95 * R, cy - 0.1 * R + 0.95 * R], fill=_rgba(bg, 255))
    # 小星星
    for s in [(-1.05, -0.7), (1.05, -0.85), (1.15, 0.25), (-0.2, -1.0)]:
        sx = cx + s[0] * R; sy = cy + s[1] * R
        dc.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=_rgba((255, 255, 255), 210))

def _sun(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    dc.ellipse([cx - size * 0.5, cy - size * 0.5, cx + size * 0.5, cy + size * 0.5],
               fill=_rgba(color, 55), outline=a, width=4)
    for i in range(12):
        ang = math.pi * i / 6 + t * 0.2
        r1 = size * 0.62; r2 = size * 0.96
        dc.line([(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)),
                 (cx + r2 * math.cos(ang), cy + r2 * math.sin(ang))], fill=a, width=4)

def _star(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + math.pi * i / 5
        r = size if i % 2 == 0 else size * 0.45
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    dc.polygon(pts, fill=_rgba(color, 50), outline=a, width=4)

def _cloud(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    for off, r in [(-0.42, 0.5), (0.02, 0.72), (0.46, 0.55), (0.16, 0.62)]:
        x0 = cx + off * size - r * size; y0 = cy - 0.25 * size
        dc.ellipse([x0, y0, x0 + 2 * r * size, y0 + 2 * r * size],
                   fill=_rgba(color, 38), outline=a, width=3)

def _brain(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    # 脑轮廓：带 8 个叶状凸起的椭圆
    pts = []
    for i in range(56):
        ang = 2 * math.pi * i / 56
        bump = 1 + 0.13 * math.cos(8 * ang)
        r = size * bump
        pts.append((cx + r * math.cos(ang), cy + r * 0.86 * math.sin(ang)))
    dc.polygon(pts, fill=_rgba(color, 42), outline=a, width=4)
    # 中缝
    dc.line([(cx, cy - size * 0.85), (cx, cy + size * 0.85)], fill=a, width=3)
    # 脑回曲线
    for yy in (-0.35, 0.0, 0.35):
        p = []
        for i in range(0, 21):
            u = i / 20
            x = cx - size * 0.6 + 1.2 * size * u
            y = cy + yy * size + 0.12 * size * math.sin(u * math.pi * 4)
            p.append((x, y))
        dc.line(p, fill=_rgba(color, 150), width=2)
    # 轻微脉动高光
    br = 0.6 + 0.4 * math.sin(t * 2.0)
    dc.ellipse([cx - size * 0.18, cy - size * 0.2, cx + size * 0.18, cy + size * 0.18],
               fill=_rgba(color, int(40 + 50 * br)))

def _clock(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    R = size * 0.85
    dc.ellipse([cx - R, cy - R, cx + R, cy + R], fill=_rgba(color, 30), outline=a, width=4)
    for i in range(12):
        ang = math.pi * 2 * i / 12
        r1 = R * 0.82; r2 = R * 0.94
        dc.line([(cx + r1 * math.cos(ang), cy + r1 * math.sin(ang)),
                 (cx + r2 * math.cos(ang), cy + r2 * math.sin(ang))], fill=a, width=2)
    # 10:10 固定 + 秒针扫动
    hh = math.radians(-60); mh = math.radians(60)
    dc.line([(cx, cy), (cx + R * 0.45 * math.cos(hh), cy + R * 0.45 * math.sin(hh))], fill=a, width=5)
    dc.line([(cx, cy), (cx + R * 0.7 * math.cos(mh), cy + R * 0.7 * math.sin(mh))], fill=a, width=4)
    sec = math.radians((t * 90) % 360)
    dc.line([(cx, cy), (cx + R * 0.78 * math.cos(sec), cy + R * 0.78 * math.sin(sec))],
            fill=_rgba((255, 120, 120), 230), width=2)
    dc.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=a)

def _droplet(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    r = size * 0.82; oy = cy + size * 0.3
    pts = [(cx, cy - size)]
    for deg in range(200, 341, 8):
        ang = math.radians(deg)
        pts.append((cx + r * math.cos(ang), oy + r * math.sin(ang)))
    dc.polygon(pts, fill=_rgba(color, 50), outline=a, width=4)
    # 高光
    dc.ellipse([cx - size * 0.25, cy - size * 0.1, cx - size * 0.05, cy + size * 0.15],
               fill=_rgba((255, 255, 255), 120))

def _heart(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    pts = []
    for i in range(60):
        th = math.pi * 2 * i / 60
        x = 16 * math.sin(th) ** 3
        y = 13 * math.cos(th) - 5 * math.cos(2 * th) - 2 * math.cos(3 * th) - math.cos(4 * th)
        pts.append((cx + x / 16 * size, cy - y / 16 * size))
    dc.polygon(pts, fill=_rgba(color, 50), outline=a, width=4)
    br = 0.6 + 0.4 * math.sin(t * 2.5)
    dc.ellipse([cx - size * 0.3, cy - size * 0.35, cx - size * 0.05, cy - size * 0.1],
               fill=_rgba((255, 255, 255), int(70 + 60 * br)))

def _shield(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    pts = [(cx - size * 0.85, cy - size * 0.7), (cx + size * 0.85, cy - size * 0.7),
           (cx + size * 0.85, cy + size * 0.1), (cx, cy + size * 0.85),
           (cx - size * 0.85, cy + size * 0.1)]
    dc.polygon(pts, fill=_rgba(color, 45), outline=a, width=4)
    # 内部对勾
    dc.line([(cx - size * 0.4, cy), (cx - size * 0.08, cy + size * 0.35)], fill=a, width=6, joint="curve")
    dc.line([(cx - size * 0.08, cy + size * 0.35), (cx + size * 0.45, cy - size * 0.3)], fill=a, width=6, joint="curve")

def _flame(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    flick = 0.06 * math.sin(t * 6)
    pts = [(cx, cy - size),
           (cx + size * 0.5, cy - size * 0.2), (cx + size * 0.62, cy + size * 0.5),
           (cx + size * 0.2, cy + size * 0.9), (cx - size * 0.25, cy + size * 0.9),
           (cx - size * 0.6, cy + size * 0.4), (cx - size * 0.45, cy - size * 0.2)]
    pts = [(x + flick * size if i in (1, 2, 4, 5) else x, y) for i, (x, y) in enumerate(pts)]
    dc.polygon(pts, fill=_rgba(color, 55), outline=a, width=4)
    dc.ellipse([cx - size * 0.2, cy + size * 0.1, cx + size * 0.2, cy + size * 0.6],
               fill=_rgba((255, 220, 120), 120))

def _battery(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    w = size * 1.3; h = size * 2.0
    x0 = cx - w / 2; y0 = cy - h / 2
    dc.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=10, fill=_rgba(color, 35), outline=a, width=4)
    dc.rectangle([cx - size * 0.2, y0 - size * 0.18, cx + size * 0.2, y0], fill=a)
    bars = 4; pad = 10; seg = (h - pad * 2) / bars
    level = 1  # 满电；可由调用方传大小表现「低电量」
    for i in range(bars):
        yy = y0 + pad + i * seg
        fill = a if i < level else _rgba((255, 255, 255), 26)
        dc.rounded_rectangle([x0 + pad, yy, x0 + w - pad, yy + seg - 6], radius=4, fill=fill)

def _bed(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    w = size * 1.9; h = size * 0.6
    x0 = cx - w / 2; y0 = cy - h / 2
    dc.rounded_rectangle([x0, y0 + h * 0.32, x0 + w, y0 + h], radius=8,
                         fill=_rgba(color, 38), outline=a, width=4)
    dc.rectangle([x0, y0, x0 + w * 0.1, y0 + h * 0.7], fill=_rgba(color, 60), outline=a, width=4)
    dc.rounded_rectangle([x0 + w * 0.12, y0 + h * 0.28, x0 + w * 0.38, y0 + h * 0.6],
                         radius=10, fill=_rgba(color, 90), outline=a, width=3)
    dc.rounded_rectangle([x0 + w * 0.4, y0 + h * 0.4, x0 + w, y0 + h],
                         radius=8, fill=_rgba(color, 70), outline=a, width=3)

def _book(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    w = size * 1.5; h = size * 0.95
    dc.polygon([(cx, cy - h / 2), (cx - w / 2, cy - h / 2 + h * 0.08),
                (cx - w / 2, cy + h / 2 - h * 0.08), (cx, cy + h / 2)],
               fill=_rgba(color, 35), outline=a, width=4)
    dc.polygon([(cx, cy - h / 2), (cx + w / 2, cy - h / 2 + h * 0.08),
                (cx + w / 2, cy + h / 2 - h * 0.08), (cx, cy + h / 2)],
               fill=_rgba(color, 35), outline=a, width=4)
    dc.line([(cx, cy - h / 2), (cx, cy + h / 2)], fill=a, width=4)
    for k in range(1, 4):
        yy = cy - h / 2 + h * 0.1 * k
        dc.line([(cx - w / 2 * 0.82, yy), (cx - w * 0.1, yy)], fill=_rgba(color, 140), width=2)
        dc.line([(cx + w * 0.1, yy), (cx + w / 2 * 0.82, yy)], fill=_rgba(color, 140), width=2)

def _apple(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    r = size * 0.8
    dc.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 1.1], fill=_rgba(color, 55), outline=a, width=4)
    dc.line([(cx, cy - r * 0.7), (cx + r * 0.12, cy - r * 1.18)], fill=_rgba((150, 110, 70), 255), width=5)
    dc.ellipse([cx + r * 0.15, cy - r * 1.28, cx + r * 0.62, cy - r * 0.82],
               fill=_rgba((120, 200, 110), 235), outline=_rgba((120, 200, 110), 255), width=3)

def _leaf(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    ang = math.radians(35)
    c = math.cos(ang); s = math.sin(ang)
    pts = []
    for i in range(44):
        th = 2 * math.pi * i / 44
        x = size * 0.5 * math.cos(th); y = size * 1.05 * math.sin(th)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    dc.polygon(pts, fill=_rgba(color, 45), outline=a, width=4)
    tip1 = (cx + size * math.sin(ang), cy - size * math.cos(ang))
    tip2 = (cx - size * math.sin(ang), cy + size * math.cos(ang))
    dc.line([tip1, tip2], fill=_rgba(color, 150), width=3)

def _wave(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    pts = []
    for i in range(0, 61):
        x = cx - size + 2 * size * i / 60
        y = cy + size * 0.4 * math.sin((i / 60) * math.pi * 4 + t * 1.5)
        pts.append((x, y))
    dc.line(pts, fill=a, width=5, joint="curve")
    pts2 = [(x, y + size * 0.22) for (x, y) in pts]
    dc.line(pts2, fill=_rgba(color, 130), width=3, joint="curve")

def _atom(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    for k in range(3):
        rot = math.radians(60 * k + t * 12)
        dc.polygon(_ellipse_poly(cx, cy, size, size * 0.42, rot), outline=_rgba(color, 120), width=3)
    dc.ellipse([cx - size * 0.16, cy - size * 0.16, cx + size * 0.16, cy + size * 0.16],
               fill=_rgba(color, 70), outline=a, width=3)
    for k in range(3):
        ang = math.radians(120 * k + t * 60)
        ex = cx + size * 0.85 * math.cos(ang); ey = cy + size * 0.35 * math.sin(ang)
        dc.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=a)

def _gear(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    teeth = 10; outer = size; inner = size * 0.78
    pts = []
    for i in range(teeth * 2):
        ang = math.pi * i / teeth
        r = outer if i % 2 == 0 else inner
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    dc.polygon(pts, fill=_rgba(color, 40), outline=a, width=4)
    dc.ellipse([cx - size * 0.42, cy - size * 0.42, cx + size * 0.42, cy + size * 0.42],
               fill=_rgba(bg, 255), outline=a, width=4)
    dc.ellipse([cx - size * 0.18, cy - size * 0.18, cx + size * 0.18, cy + size * 0.18],
               fill=_rgba(color, 60), outline=a, width=3)

def _trash(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    w = size * 0.95; h = size * 1.15
    x0 = cx - w / 2; y0 = cy - h / 2 + h * 0.2
    dc.polygon([(x0, y0), (x0 + w, y0), (x0 + w * 0.85, y0 + h), (x0 + w * 0.15, y0 + h)],
               fill=_rgba(color, 40), outline=a, width=4)
    dc.rectangle([x0 - w * 0.12, y0 - h * 0.18, x0 + w + w * 0.12, y0], fill=_rgba(color, 60), outline=a, width=4)
    dc.line([(cx - w * 0.25, y0 - h * 0.32), (cx + w * 0.25, y0 - h * 0.32)], fill=a, width=5)
    for k in (0.3, 0.5, 0.7):
        dc.line([(x0 + w * k, y0 + h * 0.1), (x0 + w * k, y0 + h * 0.9)], fill=_rgba(color, 150), width=3)

def _bolt(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    pts = [(cx + size * 0.1, cy - size), (cx - size * 0.5, cy + size * 0.1),
           (cx - size * 0.05, cy + size * 0.1), (cx - size * 0.2, cy + size),
           (cx + size * 0.5, cy - size * 0.15), (cx + size * 0.05, cy - size * 0.15)]
    dc.polygon(pts, fill=_rgba(color, 55), outline=a, width=4)

def _eye(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    pts = []
    for i in range(0, 41):
        u = i / 40; x = cx - size + u * 2 * size
        y = cy - size * 0.5 * math.sin(math.pi * u)
        pts.append((x, y))
    dc.line(pts, fill=a, width=4, joint="curve")
    dc.ellipse([cx - size * 0.28, cy - size * 0.28, cx + size * 0.28, cy + size * 0.28],
               fill=_rgba(color, 60), outline=a, width=3)
    dc.ellipse([cx - size * 0.12, cy - size * 0.12, cx + size * 0.12, cy + size * 0.12],
               fill=_rgba((10, 12, 26), 255))

def _mountain(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    dc.polygon([(cx - size, cy + size * 0.6), (cx - size * 0.2, cy - size * 0.5),
                (cx + size * 0.3, cy + size * 0.2), (cx + size, cy + size * 0.6)],
               fill=_rgba(color, 30), outline=a, width=4)
    dc.polygon([(cx - size * 0.2, cy - size * 0.5), (cx - size * 0.38, cy - size * 0.1),
                (cx - size * 0.02, cy - size * 0.15)], fill=_rgba((240, 245, 255), 220))

def _scale(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    dc.line([(cx - size, cy - size * 0.4), (cx + size, cy - size * 0.4)], fill=a, width=4)
    dc.line([(cx, cy - size * 0.4), (cx, cy + size * 0.8)], fill=a, width=4)
    dc.line([(cx - size * 0.5, cy + size * 0.8), (cx + size * 0.5, cy + size * 0.8)], fill=a, width=4)
    for sgn in (-1, 1):
        px = cx + sgn * size
        dc.line([(px, cy - size * 0.4), (px, cy + size * 0.1)], fill=a, width=3)
        dc.pieslice([px - size * 0.28, cy + size * 0.1, px + size * 0.28, cy + size * 0.66],
                    180, 360, fill=_rgba(color, 40), outline=a, width=3)

def _check(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    dc.ellipse([cx - size, cy - size, cx + size, cy + size], fill=_rgba(color, 45), outline=a, width=4)
    dc.line([(cx - size * 0.5, cy), (cx - size * 0.1, cy + size * 0.45)], fill=a, width=6, joint="curve")
    dc.line([(cx - size * 0.1, cy + size * 0.45), (cx + size * 0.6, cy - size * 0.4)], fill=a, width=6, joint="curve")

# ---------------- 调度 ----------------

_ART = {
    "moon": _moon, "sun": _sun, "star": _star, "cloud": _cloud,
    "brain": _brain, "clock": _clock, "droplet": _droplet, "heart": _heart,
    "shield": _shield, "flame": _flame, "battery": _battery, "bed": _bed,
    "book": _book, "apple": _apple, "leaf": _leaf, "wave": _wave,
    "atom": _atom, "gear": _gear, "trash": _trash, "bolt": _bolt,
    "eye": _eye, "mountain": _mountain, "scale": _scale, "check": _check,
}

def draw_art(dc, name, cx, cy, size, color, t=0.0, bg=(8, 12, 26)):
    fn = _ART.get(name)
    if fn is None:
        # 未收录的图形：画一个小点兜底（不破坏整体）
        dc.ellipse([cx - size * 0.25, cy - size * 0.25, cx + size * 0.25, cy + size * 0.25],
                   fill=_rgba(color, 200))
        return
    fn(dc, cx, cy, size, color, t, bg)

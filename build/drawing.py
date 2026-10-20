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
    r = size * 0.72; oy = cy + size * 0.22
    pts = [(cx, cy - size)]
    for deg in range(20, 161, 8):
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

# ===== v5 新增：用于「多图编排」的组合素材 =====

def _file(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    w = size * 1.0; h = size * 1.3
    x0 = cx - w / 2; y0 = cy - h / 2
    fold = size * 0.34
    dc.polygon([(x0, y0), (x0 + w - fold, y0), (x0 + w, y0 + fold),
                (x0 + w, y0 + h), (x0, y0 + h)], fill=_rgba(color, 40), outline=a, width=3)
    dc.polygon([(x0 + w - fold, y0), (x0 + w - fold, y0 + fold), (x0 + w, y0 + fold)],
               fill=_rgba(color, 120), outline=a, width=2)
    for k in range(1, 4):
        yy = y0 + h * (0.30 + 0.17 * k)
        dc.line([(x0 + w * 0.16, yy), (x0 + w * 0.82, yy)], fill=_rgba(color, 150), width=2)

def _antibody(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    dc.line([(cx, cy + size * 0.85), (cx, cy - size * 0.1)], fill=a, width=7)
    dc.line([(cx, cy - size * 0.1), (cx - size * 0.62, cy - size * 0.8)], fill=a, width=7)
    dc.line([(cx, cy - size * 0.1), (cx + size * 0.62, cy - size * 0.8)], fill=a, width=7)
    dc.ellipse([cx - 4, cy + size * 0.84, cx + 4, cy + size * 0.9], fill=_rgba(color, 200))

def _germ(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    r = size * 0.52
    dc.ellipse([cx - r, cy - r, cx + r, cy + r], fill=_rgba(color, 45), outline=a, width=3)
    n = 10
    for i in range(n):
        ang = 2 * math.pi * i / n + t * 0.6
        x2 = cx + (r + size * 0.34) * math.cos(ang)
        y2 = cy + (r + size * 0.34) * math.sin(ang)
        dc.line([(cx + r * math.cos(ang), cy + r * math.sin(ang)), (x2, y2)], fill=a, width=3)
        dc.ellipse([x2 - 3, y2 - 3, x2 + 3, y2 + 3], fill=a)

def _arrow_up(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    dc.line([(cx, cy + size * 0.55), (cx, cy - size * 0.35)], fill=a, width=6)
    dc.polygon([(cx, cy - size), (cx - size * 0.42, cy - size * 0.3), (cx + size * 0.42, cy - size * 0.3)], fill=a)

def _arrow_down(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    dc.line([(cx, cy - size * 0.55), (cx, cy + size * 0.35)], fill=a, width=6)
    dc.polygon([(cx, cy + size), (cx - size * 0.42, cy + size * 0.3), (cx + size * 0.42, cy + size * 0.3)], fill=a)

def _stomach(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    pts = []
    for i in range(52):
        ang = 2 * math.pi * i / 52
        pinch = 1 - 0.48 * max(0.0, math.cos(ang)) ** 2
        pts.append((cx + size * 0.8 * math.cos(ang) * pinch, cy + size * 0.95 * math.sin(ang)))
    dc.polygon(pts, fill=_rgba(color, 42), outline=a, width=3)
    for k in range(2):
        yy = cy - size * 0.25 + k * size * 0.4
        dc.line([(cx - size * 0.25, yy), (cx + size * 0.2, yy)], fill=_rgba(color, 140), width=2)

def _muscle(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    dc.rounded_rectangle([cx - size * 0.42, cy - size * 0.10, cx + size * 0.42, cy + size * 0.10],
                         radius=6, fill=a)
    for sgn in (-1, 1):
        px = cx + sgn * size * 0.55
        dc.polygon([(px - sgn * size * 0.14, cy - size * 0.20),
                    (px + sgn * size * 0.14, cy - size * 0.36),
                    (px + sgn * size * 0.14, cy + size * 0.36),
                    (px - sgn * size * 0.14, cy + size * 0.20)],
                   fill=_rgba(color, 75), outline=a, width=3)

def _hourglass(dc, cx, cy, size, color, t, bg):
    a = _rgba(color, 255)
    w = size * 0.72; h = size * 1.5
    top = cy - h / 2; bot = cy + h / 2
    dc.rectangle([cx - w / 2, top, cx + w / 2, top + h * 0.08], fill=a)
    dc.rectangle([cx - w / 2, bot - h * 0.08, cx + w / 2, bot], fill=a)
    dc.polygon([(cx - w / 2, top + h * 0.08), (cx + w / 2, top + h * 0.08),
                (cx + size * 0.05, cy), (cx - size * 0.05, cy)],
               fill=_rgba(color, 28), outline=a, width=3)
    dc.polygon([(cx - w / 2, bot - h * 0.08), (cx + w / 2, bot - h * 0.08),
                (cx + size * 0.05, cy), (cx - size * 0.05, cy)],
               fill=_rgba(color, 28), outline=a, width=3)
    u = 0.5 + 0.5 * math.sin(t * 0.6)
    ft = h * 0.30 * (1 - u); fb = h * 0.30 * u
    if ft > 1:
        dc.polygon([(cx - w / 2 + 2, cy - ft), (cx + w / 2 - 2, cy - ft),
                    (cx + size * 0.04, cy - 2), (cx - size * 0.04, cy - 2)], fill=_rgba(color, 150))
    if fb > 1:
        dc.polygon([(cx - w / 2 + 2, bot - h * 0.09), (cx + w / 2 - 2, bot - h * 0.09),
                    (cx + size * 0.10, bot - h * 0.09 - fb), (cx - size * 0.10, bot - h * 0.09 - fb)],
                   fill=_rgba(color, 150))
    for i in range(3):
        ph = ((t * 0.9) + i / 3) % 1.0
        yy = cy + (bot - cy - h * 0.1) * ph
        dc.ellipse([cx - 2, yy - 2, cx + 2, yy + 2], fill=_rgba(color, 180))

# ---------------- 侏罗纪素材（v6） ----------------

def _bez(p0, p1, p2, n=16):
    out = []
    for i in range(n):
        u = i / (n - 1.0)
        k0 = (1 - u) ** 2; k1 = 2 * (1 - u) * u; k2 = u ** 2
        out.append((k0 * p0[0] + k1 * p1[0] + k2 * p2[0],
                    k0 * p0[1] + k1 * p1[1] + k2 * p2[1]))
    return out

def _taper(dc, pts, w0, w1, col, alpha=255):
    n = len(pts)
    if n < 2:
        return
    left = []; right = []
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        u = i / (n - 1.0)
        w = w0 + (w1 - w0) * u
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    dc.polygon(left + right[::-1], fill=_rgba(col, alpha))

def _limb(dc, p0, p1, w0, w1, col, alpha=255):
    _taper(dc, [p0, ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5), p1], w0, w1, col, alpha)

def _sauropod(dc, cx, cy, size, color, t, bg):
    """蜥脚类（腕龙式）：长颈 + 柱状四肢 + 长尾"""
    s = size; a = _rgba(color, 255)
    sway = math.sin(t * 0.7) * 0.035
    bob = math.sin(t * 0.9) * s * 0.012
    X = lambda u: cx + (u - 0.18) * s
    Y = lambda v: cy + v * s + bob
    for u, y1 in ((-0.16, 0.84), (0.20, 0.78)):                 # 远侧腿
        _limb(dc, (X(u), Y(0.26)), (X(u), Y(y1)), s * 0.045, s * 0.036, color, 90)
    _taper(dc, _bez((X(0.34), Y(0.12)), (X(0.68), Y(0.26)),
                    (X(0.98 + sway), Y(0.50)), 18), s * 0.105, s * 0.012, color, 200)
    dc.ellipse([X(-0.34), Y(-0.18), X(0.40), Y(0.46)], fill=_rgba(color, 58), outline=a, width=4)
    _taper(dc, _bez((X(-0.26), Y(-0.04)), (X(-0.44 - sway), Y(-0.48)),
                    (X(-0.18 + sway), Y(-0.78)), 18), s * 0.105, s * 0.055, color, 235)
    hx, hy = X(-0.18 + sway), Y(-0.80)
    dc.ellipse([hx - s * 0.10, hy - s * 0.075, hx + s * 0.10, hy + s * 0.075],
               fill=_rgba(color, 150), outline=a, width=3)
    dc.ellipse([hx - s * 0.032, hy - s * 0.035, hx - s * 0.004, hy - s * 0.005],
               fill=_rgba((255, 255, 255), 220))
    for u, y1 in ((-0.26, 0.86), (0.26, 0.80)):                 # 近侧腿
        _limb(dc, (X(u), Y(0.26)), (X(u), Y(y1)), s * 0.052, s * 0.044, color, 245)
        dc.ellipse([X(u) - s * 0.078, Y(y1) - s * 0.024, X(u) + s * 0.078, Y(y1) + s * 0.024],
                   fill=_rgba(color, 200))

def _theropod(dc, cx, cy, size, color, t, bg):
    """兽脚类（异特龙式）：双足 + 巨颌 + 平衡长尾"""
    s = size; a = _rgba(color, 255)
    bob = math.sin(t * 1.1) * s * 0.018
    X = lambda u: cx + (u - 0.08) * s
    Y = lambda v: cy + v * s + bob
    _limb(dc, (X(0.12), Y(0.10)), (X(0.22), Y(0.42)), s * 0.055, s * 0.045, color, 90)
    _limb(dc, (X(0.22), Y(0.42)), (X(0.10), Y(0.70)), s * 0.045, s * 0.028, color, 90)
    _taper(dc, _bez((X(0.30), Y(0.06)), (X(0.64), Y(0.00)), (X(0.98), Y(-0.20)), 18),
           s * 0.100, s * 0.012, color, 205)
    dc.polygon(_ellipse_poly(X(0.02), Y(0.02), s * 0.33, s * 0.20, rot=-0.30, seg=44),
               fill=_rgba(color, 58), outline=a, width=4)
    _taper(dc, _bez((X(-0.16), Y(-0.08)), (X(-0.36), Y(-0.24)), (X(-0.48), Y(-0.28)), 12),
           s * 0.085, s * 0.055, color, 240)
    dc.polygon([(X(-0.40), Y(-0.36)), (X(-0.78), Y(-0.29)), (X(-0.84), Y(-0.19)),
                (X(-0.44), Y(-0.13))], fill=_rgba(color, 180), outline=a, width=3)
    for k in range(4):                                          # 牙
        px = X(-0.48 - k * 0.078)
        dc.polygon([(px, Y(-0.16)), (px + s * 0.030, Y(-0.16)), (px + s * 0.015, Y(-0.10))],
                   fill=_rgba((255, 255, 255), 190))
    dc.ellipse([X(-0.50) - s * 0.024, Y(-0.30) - s * 0.024,
                X(-0.50) + s * 0.024, Y(-0.30) + s * 0.024], fill=_rgba((255, 255, 255), 225))
    _limb(dc, (X(-0.10), Y(0.06)), (X(-0.24), Y(0.20)), s * 0.034, s * 0.020, color, 200)
    _limb(dc, (X(0.04), Y(0.10)), (X(0.16), Y(0.44)), s * 0.062, s * 0.050, color, 245)
    _limb(dc, (X(0.16), Y(0.44)), (X(0.02), Y(0.72)), s * 0.050, s * 0.032, color, 245)
    dc.polygon([(X(-0.12), Y(0.72)), (X(0.18), Y(0.72)), (X(0.20), Y(0.80)), (X(-0.14), Y(0.80))],
               fill=a)

def _conifer(dc, cx, cy, size, color, t, bg):
    """高大针叶树（南洋杉式），树冠随风摆动"""
    s = size; a = _rgba(color, 255)
    sway = math.sin(t * 0.8) * s * 0.030
    def skirt(y0, y1, w):
        o0 = sway * (0.90 - y0) / 1.8
        o1 = sway * (0.90 - y1) / 1.8
        dc.polygon([(cx + o0, cy + y0 * s), (cx - w * s + o1, cy + y1 * s),
                    (cx + w * s + o1, cy + y1 * s)], fill=_rgba(color, 68), outline=a, width=3)
    dc.rectangle([cx - s * 0.055, cy + s * 0.58, cx + s * 0.055, cy + s * 0.90], fill=a)
    skirt(-0.88, -0.52, 0.15)
    skirt(-0.56, -0.14, 0.29)
    skirt(-0.20, 0.30, 0.43)
    skirt(0.24, 0.70, 0.55)

def _cycad(dc, cx, cy, size, color, t, bg):
    """苏铁：粗短树干 + 放射状羽状叶冠（侏罗纪标志植物）"""
    s = size; a = _rgba(color, 255)
    cy = cy - s * 0.16
    sway = math.sin(t * 0.9) * 0.055
    _taper(dc, [(cx, cy + s * 0.88), (cx, cy + s * 0.56), (cx, cy + s * 0.20)],
           s * 0.135, s * 0.105, color, 230)
    for k in range(4):
        y = cy + s * (0.30 + k * 0.145)
        dc.line([(cx - s * 0.105, y), (cx + s * 0.105, y)], fill=_rgba(color, 110), width=2)
    for i in range(9):
        u = i / 8.0
        ang = (-0.5 + u) * math.pi * 0.90 + sway * math.sin(i * 1.7)
        dx, dy = math.sin(ang), -math.cos(ang)
        L = s * 0.78
        p0 = (cx, cy + s * 0.16)
        pm = (cx + dx * L * 0.55, cy + s * 0.16 + dy * L * 0.62 - s * 0.06)
        p1 = (cx + dx * L, cy + s * 0.16 + dy * L * 0.92 + s * 0.24)
        _taper(dc, _bez(p0, pm, p1, 12), s * 0.048, s * 0.008, color, 195)

def _volcano(dc, cx, cy, size, color, t, bg):
    """火山：锥形山体 + 火口 + 流下熔岩 + 升腾烟柱"""
    s = size; a = _rgba(color, 255)
    dc.polygon([(cx - s * 0.92, cy + s * 0.88), (cx - s * 0.28, cy - s * 0.16),
                (cx + s * 0.28, cy - s * 0.16), (cx + s * 0.92, cy + s * 0.88)],
               fill=_rgba(color, 42), outline=a, width=4)
    dc.ellipse([cx - s * 0.30, cy - s * 0.32, cx + s * 0.30, cy - s * 0.06],
               fill=_rgba(color, 210))
    for k, sg in enumerate((-1, 0, 1)):
        ph = (t * 0.26 + k * 0.34) % 1.0
        if ph < 0.06:
            continue
        x0 = cx + sg * s * 0.20
        x1 = cx + sg * s * (0.20 + 0.58 * ph)
        _limb(dc, (x0, cy - s * 0.06), (x1, cy + s * (-0.02 + 0.90 * ph)),
              s * 0.030, s * 0.012, color, int(110 + 120 * (1 - ph)))
    for i in range(5):
        ph = ((t * 0.20) + i / 5.0) % 1.0
        r = s * (0.09 + 0.20 * ph)
        xx = cx + s * 0.16 * math.sin(ph * 3.0 + i)
        yy = cy - s * (0.24 + 0.74 * ph)
        dc.ellipse([xx - r, yy - r, xx + r, yy + r], fill=_rgba(color, int(115 * (1 - ph))))

def _landmass(dc, cx, cy, size, color, t, bg):
    """大陆块：不规则海岸线 + 中央发光的裂谷（泛古陆裂解）"""
    s = size; a = _rgba(color, 255)
    pts = []
    N = 56
    for i in range(N):
        u = 2 * math.pi * i / N
        r = s * (0.80 + 0.16 * math.sin(3 * u + 0.7) + 0.11 * math.sin(5 * u + 2.1)
                 + 0.07 * math.sin(8 * u + 1.2))
        pts.append((cx + r * math.cos(u) * 1.12, cy + r * math.sin(u) * 0.76))
    dc.polygon(pts, fill=_rgba(color, 44), outline=a, width=4)
    gap = s * (0.045 + 0.032 * (0.5 + 0.5 * math.sin(t * 0.7)))
    base = []
    for i in range(13):
        v = i / 12.0
        base.append((cx + s * 0.13 * math.sin(v * 7.0), cy + s * (-0.52 + 1.04 * v)))
    la = [(x - gap, y) for x, y in base]
    lb = [(x + gap, y) for x, y in base]
    dc.polygon(la + lb[::-1], fill=_rgba(color, 190))
    for sgn in (-1, 1):
        dc.line([(x + sgn * gap * 0.55, y) for x, y in base],
                fill=_rgba(color, 130), width=2, joint="curve")

def _ammonite(dc, cx, cy, size, color, t, bg):
    """菊石：对数螺线壳 + 隔壁 + 触手"""
    s = size; a = _rgba(color, 255)
    N = 130; TW = math.pi * 2 * 2.35
    rot = t * 0.14
    pts = []
    for i in range(N):
        th = TW * i / (N - 1.0)
        r = s * 0.13 * math.exp(0.127 * th)
        pts.append((cx + r * math.cos(th + rot), cy + r * math.sin(th + rot)))
    rE0 = s * 0.13 * math.exp(0.127 * TW)
    dc.ellipse([cx - rE0 * 0.97, cy - rE0 * 0.97, cx + rE0 * 0.97, cy + rE0 * 0.97],
               fill=_rgba(color, 38))
    for i in range(1, N):
        u = i / (N - 1.0)
        w = max(1, int(s * 0.010 + s * 0.078 * u))
        dc.line([pts[i - 1], pts[i]], fill=_rgba(color, int(110 + 140 * u)), width=w)
    for k in range(11):
        i = int(N * (k + 1) / 12.0)
        th = TW * i / (N - 1.0)
        r0 = s * 0.13 * math.exp(0.127 * th)
        x0 = cx + r0 * math.cos(th + rot); y0 = cy + r0 * math.sin(th + rot)
        r1 = r0 * 0.52
        x1 = cx + r1 * math.cos(th + rot); y1 = cy + r1 * math.sin(th + rot)
        dc.line([(x1, y1), (x0, y0)], fill=_rgba(color, 115), width=2)
    rE = s * 0.13 * math.exp(0.127 * TW)
    ex = cx + rE * math.cos(TW + rot); ey = cy + rE * math.sin(TW + rot)
    for k in range(5):
        ang = -0.32 + k * 0.155 + math.sin(t * 1.2 + k) * 0.08
        _limb(dc, (ex, ey), (ex + s * 0.24 * math.cos(ang), ey + s * 0.24 * math.sin(ang)),
              s * 0.024, s * 0.006, color, 165)

def _plesiosaur(dc, cx, cy, size, color, t, bg):
    """蛇颈龙：短身 + 超长颈 + 四鳍"""
    s = size; a = _rgba(color, 255)
    bob = math.sin(t * 0.9) * s * 0.020
    X = lambda u: cx + u * s
    Y = lambda v: cy + v * s + bob
    _taper(dc, _bez((X(0.34), Y(0.10)), (X(0.58), Y(0.18)), (X(0.82), Y(0.30)), 12),
           s * 0.060, s * 0.010, color, 200)
    dc.ellipse([X(-0.34), Y(-0.14), X(0.36), Y(0.38)], fill=_rgba(color, 58), outline=a, width=4)
    for sg in (-1, 1):
        for u in (-0.20, 0.14):
            px, py = X(u), Y(0.20)
            ex = px + sg * s * 0.30
            ey = py + s * 0.22 + math.sin(t * 1.4 + u * 3) * s * 0.05
            _taper(dc, [(px, py), (px + sg * s * 0.16, py + s * 0.10), (ex, ey)],
                   s * 0.085, s * 0.028, color, 185)
    sw = math.sin(t * 0.8) * 0.05
    _taper(dc, _bez((X(-0.28), Y(0.02)), (X(-0.62), Y(-0.30)), (X(-0.72 + sw), Y(-0.62)), 16),
           s * 0.070, s * 0.035, color, 235)
    hx, hy = X(-0.72 + sw * 0.6), Y(-0.66)
    dc.ellipse([hx - s * 0.09, hy - s * 0.060, hx + s * 0.09, hy + s * 0.060],
               fill=_rgba(color, 170), outline=a, width=3)
    dc.ellipse([hx - s * 0.026, hy - s * 0.026, hx + s * 0.006, hy + s * 0.006],
               fill=_rgba((255, 255, 255), 215))

def _ichthyosaur(dc, cx, cy, size, color, t, bg):
    """鱼龙：流线型身体 + 长吻 + 背鳍 + 摆动的尾鳍"""
    s = size; a = _rgba(color, 255)
    bob = math.sin(t * 1.0) * s * 0.022
    fln = math.sin(t * 1.6) * 0.105
    fl = fln * s
    X = lambda u: cx + u * s
    Y = lambda v: cy + v * s + bob
    dc.polygon([(X(0.68), Y(0.00)), (X(0.98), Y(-0.42 + fln)),
                (X(0.84), Y(0.02)), (X(0.98), Y(0.42 + fln))],
               fill=_rgba(color, 165), outline=a, width=3)
    up = _bez((X(-0.62), Y(-0.04)), (X(-0.05), Y(-0.34)), (X(0.70), Y(0.00)), 20)
    dn = _bez((X(-0.62), Y(-0.04)), (X(-0.05), Y(0.34)), (X(0.70), Y(0.00)), 20)
    dc.polygon(up + dn[::-1], fill=_rgba(color, 58), outline=a, width=4)
    _taper(dc, _bez((X(-0.56), Y(-0.06)), (X(-0.80), Y(-0.06)), (X(-0.96), Y(-0.04)), 10),
           s * 0.058, s * 0.018, color, 220)
    dc.polygon([(X(0.00), Y(-0.26)), (X(0.15), Y(-0.63)), (X(0.21), Y(-0.21))],
               fill=_rgba(color, 150), outline=a, width=3)
    for u in (-0.14, 0.22):
        px, py = X(u), Y(0.18)
        _taper(dc, _bez((px, py), (px + s * 0.18, py + s * 0.18),
                        (px + s * 0.34, py + s * 0.30 + fl * 0.12), 10),
               s * 0.078, s * 0.016, color, 190)
    dc.ellipse([X(-0.52) - s * 0.030, Y(-0.10) - s * 0.030,
                X(-0.52) + s * 0.030, Y(-0.10) + s * 0.030], fill=_rgba((255, 255, 255), 220))

def _pterosaur(dc, cx, cy, size, color, t, bg):
    """翼龙（俯视）：宽翼膜 + 长喙 + 头冠，振翅"""
    s = size; a = _rgba(color, 255)
    flap = math.sin(t * 1.5)
    X = lambda u: cx + u * s
    Y = lambda v: cy + v * s + flap * s * 0.03

    def lp(p0, p1, u):
        return (p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u)

    for sg in (-1, 1):
        root = (X(sg * 0.04), Y(-0.12))
        mid = (X(sg * 0.72), Y(-0.40 - flap * 0.15))
        tip = (X(sg * 1.02), Y(0.06 + flap * 0.20))
        back = (X(sg * 0.26), Y(0.32))
        dc.polygon([root, mid, tip, back], fill=_rgba(color, 50), outline=a, width=3)
        for k in range(3):                                  # 翼膜张力线
            u = 0.28 + 0.26 * k
            dc.line([lp(root, tip, u), lp(back, tip, u)], fill=_rgba(color, 85), width=2)
        dc.line([root, mid, tip], fill=_rgba(color, 200), width=4, joint="curve")
    dc.polygon(_ellipse_poly(X(0.00), Y(0.04), s * 0.15, s * 0.31, seg=36),
               fill=_rgba(color, 130), outline=a, width=3)
    _taper(dc, [(X(-0.10), Y(-0.10)), (X(-0.42), Y(-0.15)), (X(-0.76), Y(-0.13))],
           s * 0.085, s * 0.018, color, 230)
    dc.polygon([(X(-0.10), Y(-0.18)), (X(-0.34), Y(-0.52)), (X(0.04), Y(-0.22))],
               fill=_rgba(color, 165), outline=a, width=2)
    dc.ellipse([X(-0.20) - s * 0.030, Y(-0.21) - s * 0.030,
                X(-0.20) + s * 0.030, Y(-0.21) + s * 0.030], fill=_rgba((255, 255, 255), 220))
    _taper(dc, [(X(0.12), Y(0.26)), (X(0.24), Y(0.42)), (X(0.30), Y(0.58))],
           s * 0.050, s * 0.012, color, 195)

def _bird(dc, cx, cy, size, color, t, bg):
    """始祖鸟（侧视）：具齿的喙 + 抬起的长羽翼 + 长尾羽扇"""
    s = size; a = _rgba(color, 255)
    flap = math.sin(t * 1.3)
    X = lambda u: cx + (u + 0.06) * s
    Y = lambda v: cy + v * s + flap * s * 0.025
    for k in range(5):                                          # 尾羽扇
        ang = 0.28 + k * 0.095
        L = s * 0.82
        _limb(dc, (X(0.16), Y(0.06)),
              (X(0.16) + L * math.cos(ang), Y(0.06) + L * math.sin(ang)),
              s * 0.032, s * 0.009, color, 165)
    SX, SY = X(-0.02), Y(-0.10)                                 # 抬起的翼：羽片扇出
    for k in range(7):
        ang = -1.62 + k * 0.205 + flap * 0.05
        L = s * (0.86 - 0.055 * abs(k - 3))
        ex = SX + L * math.cos(ang); ey = SY + L * math.sin(ang)
        _taper(dc, _bez((SX, SY), (SX + L * 0.55 * math.cos(ang),
                                   SY + L * 0.55 * math.sin(ang) - s * 0.05), (ex, ey), 10),
               s * 0.050, s * 0.011, color, 175)
    dc.ellipse([SX - s * 0.075, SY - s * 0.065, SX + s * 0.075, SY + s * 0.065],
               fill=_rgba(color, 120))
    dc.polygon(_ellipse_poly(X(0.00), Y(0.02), s * 0.25, s * 0.15, rot=-0.10, seg=40),
               fill=_rgba(color, 85), outline=a, width=4)
    _taper(dc, _bez((X(-0.20), Y(-0.04)), (X(-0.32), Y(-0.20)), (X(-0.40), Y(-0.28)), 10),
           s * 0.080, s * 0.058, color, 240)
    hx, hy = X(-0.44), Y(-0.30)
    dc.ellipse([hx - s * 0.105, hy - s * 0.095, hx + s * 0.105, hy + s * 0.095],
               fill=_rgba(color, 165), outline=a, width=3)
    dc.polygon([(hx - s * 0.050, hy - s * 0.025), (hx - s * 0.30, hy + s * 0.020),
                (hx - s * 0.050, hy + s * 0.080)], fill=a)
    dc.ellipse([hx - s * 0.048, hy - s * 0.058, hx + s * 0.002, hy - s * 0.008],
               fill=_rgba((255, 255, 255), 225))

def _mammal(dc, cx, cy, size, color, t, bg):
    """小型哺乳动物（鼩鼱式）：夜行、穴居、侏罗纪的角落幸存者"""
    s = size; a = _rgba(color, 255)
    bob = math.sin(t * 1.6) * s * 0.020
    X = lambda u: cx + u * s
    Y = lambda v: cy + v * s + bob
    for u in (-0.20, 0.10, 0.26):
        _limb(dc, (X(u), Y(0.06)), (X(u + 0.02), Y(0.44)), s * 0.030, s * 0.024, color, 140)
    dc.ellipse([X(-0.36), Y(-0.16), X(0.34), Y(0.22)], fill=_rgba(color, 58), outline=a, width=4)
    _taper(dc, _bez((X(-0.34), Y(-0.06)), (X(-0.56), Y(-0.10)), (X(-0.74), Y(-0.06)), 8),
           s * 0.090, s * 0.030, color, 230)
    dc.ellipse([X(-0.20) - s * 0.060, Y(-0.24) - s * 0.070,
                X(-0.20) + s * 0.060, Y(-0.24) + s * 0.070],
               fill=_rgba(color, 185), outline=a, width=2)
    dc.ellipse([X(-0.40) - s * 0.022, Y(-0.10) - s * 0.022,
                X(-0.40) + s * 0.022, Y(-0.10) + s * 0.022], fill=_rgba((255, 255, 255), 220))
    _taper(dc, _bez((X(0.32), Y(0.00)), (X(0.60), Y(0.10)), (X(0.80), Y(-0.10)), 10),
           s * 0.026, s * 0.008, color, 175)

def _nest(dc, cx, cy, size, color, t, bg):
    """巢穴与蛋"""
    s = size; a = _rgba(color, 255)
    dc.ellipse([cx - s * 0.80, cy - s * 0.10, cx + s * 0.80, cy + s * 0.60],
               fill=_rgba(color, 50), outline=a, width=4)
    for k in range(9):
        u = k / 8.0
        x0 = cx + s * (-0.72 + 1.44 * u)
        y0 = cy + s * 0.26 + s * 0.24 * math.sin(u * 3.0)
        _limb(dc, (x0, y0), (x0 + s * 0.10, y0 + s * 0.30), s * 0.020, s * 0.010, color, 145)
    for i, u in enumerate((-0.38, 0.02, 0.40)):
        wob = math.sin((t * 0.5 + i * 0.33) * 6.28) * s * 0.028
        ex, ey = cx + s * u + wob, cy + s * 0.02
        dc.ellipse([ex - s * 0.20, ey - s * 0.28, ex + s * 0.20, ey + s * 0.28],
                   fill=_rgba(color, 185), outline=a, width=3)
        dc.ellipse([ex - s * 0.10, ey - s * 0.20, ex - s * 0.02, ey - s * 0.10],
                   fill=_rgba((255, 255, 255), 85))

def _footprint(dc, cx, cy, size, color, t, bg):
    """三趾型恐龙足迹化石"""
    s = size; a = _rgba(color, 255)
    dc.ellipse([cx - s * 0.38, cy + s * 0.04, cx + s * 0.38, cy + s * 0.50],
               fill=_rgba(color, 45), outline=a, width=4)
    for ang, wd in ((-0.74, 0.17), (0.0, 0.18), (0.74, 0.17)):
        L = s * 0.74
        p0 = (cx + math.sin(ang) * s * 0.07, cy + s * 0.12)
        p1 = (cx + math.sin(ang) * L, cy + s * 0.12 - math.cos(ang) * L)
        _taper(dc, _bez(p0, ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5), p1, 10),
               s * wd, s * 0.062, color, 210)
        tipx = p1[0] + math.sin(ang) * s * 0.14
        tipy = p1[1] - math.cos(ang) * s * 0.14
        dc.polygon([(p1[0] - s * 0.055, p1[1] + s * 0.030),
                    (p1[0] + s * 0.055, p1[1] + s * 0.030),
                    (tipx, tipy)], fill=a)
    for k in range(3):                                          # 地层纹
        y = cy + s * (0.56 + k * 0.12)
        dc.line([(cx - s * 0.66, y), (cx + s * 0.66, y)], fill=_rgba(color, 70), width=2)


# ---------------- 调度 ----------------

_ART = {
    "moon": _moon, "sun": _sun, "star": _star, "cloud": _cloud,
    "brain": _brain, "clock": _clock, "droplet": _droplet, "heart": _heart,
    "shield": _shield, "flame": _flame, "battery": _battery, "bed": _bed,
    "book": _book, "apple": _apple, "leaf": _leaf, "wave": _wave,
    "atom": _atom, "gear": _gear, "trash": _trash, "bolt": _bolt,
    "eye": _eye, "mountain": _mountain, "scale": _scale, "check": _check,
    # v5 组合素材
    "file": _file, "antibody": _antibody, "germ": _germ,
    "arrow_up": _arrow_up, "arrow_down": _arrow_down,
    "stomach": _stomach, "muscle": _muscle, "hourglass": _hourglass,
    # v6 侏罗纪素材
    "sauropod": _sauropod, "theropod": _theropod,
    "conifer": _conifer, "cycad": _cycad, "volcano": _volcano,
    "landmass": _landmass, "ammonite": _ammonite,
    "plesiosaur": _plesiosaur, "ichthyosaur": _ichthyosaur,
    "pterosaur": _pterosaur, "bird": _bird, "mammal": _mammal,
    "nest": _nest, "footprint": _footprint,
}

def draw_art(dc, name, cx, cy, size, color, t=0.0, bg=(8, 12, 26)):
    fn = _ART.get(name)
    if fn is None:
        # 未收录的图形：画一个小点兜底（不破坏整体）
        dc.ellipse([cx - size * 0.25, cy - size * 0.25, cx + size * 0.25, cy + size * 0.25],
                   fill=_rgba(color, 200))
        return
    fn(dc, cx, cy, size, color, t, bg)

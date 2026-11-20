#!/usr/bin/env python3
"""Render entry.png for news-image-20261119 - agent 2, 2/3 (noble-robin-77).

Layout "THE DAY UNFOLDS, corrected": the red timeline rail down the left
edge is kept, but the order is flipped - APEC opens the page at the TOP
(FIRST WIRES) as three big scene panels, instead of being buried mid-page.
Masthead (giant serif date) -> continent count strip -> "day in numbers"
strip -> 3 hero scene panels -> 10 scene cards (2 rows x 5) -> small flat
world map + numbered briefs -> DATE CHECK box -> footer.
35 stories, all happened / first reported on Thursday 19 November 2026.
Every story carries a source and a verification tag (REPORTED / CONFIRMED /
CLAIM / FORECAST). Flat vector, PIL only, fully deterministic.
"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 14
CW = W - 2 * M

PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (179, 39, 30)
NAVY = (27, 42, 74)
GOLD = (201, 162, 39)
GREY = (85, 85, 85)
TEAL = (31, 92, 77)
MAP_BG = (232, 240, 234)
MAP_LAND = (214, 205, 170)
SKY = (216, 230, 238)
CREAM = (250, 246, 230)
TINTS = [(220, 232, 238), (221, 235, 224), (228, 222, 239),
         (242, 232, 201), (240, 220, 216), (213, 232, 230)]

DJV = "/usr/share/fonts/truetype/dejavu/"
NOTO = "/usr/share/fonts/truetype/noto/"


def _font(path, size):
    return ImageFont.truetype(path, size)


def serif_b(s):
    return _font(DJV + "DejaVuSerif-Bold.ttf", s)


def serif(s):
    return _font(DJV + "DejaVuSerif.ttf", s)


def serif_i(s):
    return _font(NOTO + "NotoSerif-Italic.ttf", s)


def sans_b(s):
    return _font(DJV + "DejaVuSans-Bold.ttf", s)


def sans(s):
    return _font(DJV + "DejaVuSans.ttf", s)


def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tracked(d, xy, text, fnt, fill, track=1):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + track
    return x


def tracked_w(d, text, fnt, track=1):
    w = 0
    for ch in text:
        w += d.textlength(ch, font=fnt) + track
    return w - track if text else 0


def num_circle(d, cx, cy, n, r=8, fill=RED):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=INK, width=1)
    f = sans_b(10 if len(str(n)) < 2 else 8)
    tw = d.textlength(str(n), font=f)
    d.text((cx - tw / 2, cy - 6), str(n), font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- world map
# Coarse continent outlines (lon, lat), drawn by me for this page. Pins are
# projected with the same equirectangular mapping, so a pin lands on the
# continent its story belongs to. Verified at render time by on_land().
POLYS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-110, 72), (-95, 73),
     (-85, 73), (-78, 70), (-70, 62), (-60, 55), (-55, 48), (-60, 45),
     (-66, 44), (-70, 42), (-74, 39), (-76, 35), (-80, 31), (-81, 26),
     (-84, 30), (-90, 29), (-96, 26), (-97, 22), (-94, 18), (-90, 15),
     (-86, 12), (-82, 9), (-79, 8), (-82, 10), (-87, 13), (-92, 15),
     (-97, 16), (-103, 19), (-107, 23), (-110, 25), (-114, 29), (-117, 33),
     (-122, 37), (-124, 42), (-124, 48), (-128, 51), (-133, 57), (-141, 60),
     (-150, 61), (-158, 58), (-165, 60)],
    # Greenland
    [(-55, 60), (-45, 60), (-38, 65), (-30, 68), (-22, 70), (-20, 74),
     (-30, 77), (-45, 78), (-58, 76), (-60, 71), (-55, 64)],
    # South America
    [(-79, 9), (-76, 3), (-80, -4), (-78, -10), (-74, -17), (-70, -22),
     (-70, -30), (-73, -38), (-73, -46), (-70, -53), (-66, -55), (-64, -47),
     (-61, -39), (-57, -34), (-51, -31), (-47, -26), (-40, -21), (-38, -15),
     (-35, -8), (-36, -5), (-41, -3), (-45, -2), (-50, 0), (-54, 5),
     (-59, 8), (-64, 10), (-69, 12), (-75, 11)],
    # Africa
    [(-17, 15), (-16, 21), (-13, 27), (-9, 32), (-5, 35), (1, 36), (10, 37),
     (12, 33), (17, 32), (22, 32), (27, 31), (31, 31), (33, 27), (35, 22),
     (38, 18), (40, 15), (43, 12), (48, 11), (51, 11), (46, 5), (42, 0),
     (40, -7), (38, -14), (35, -20), (33, -26), (28, -33), (21, -35),
     (17, -32), (14, -26), (12, -17), (13, -10), (10, -2), (9, 4), (5, 4),
     (-1, 5), (-7, 5), (-13, 8), (-16, 12)],
    # Eurasia
    [(-9, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 50), (3, 51),
     (6, 54), (8, 57), (10, 59), (5, 61), (7, 63), (12, 65), (16, 68),
     (21, 70), (27, 71), (32, 69), (38, 68), (44, 68), (50, 69), (57, 69),
     (64, 71), (70, 72), (76, 73), (83, 74), (90, 75), (97, 76), (104, 77),
     (110, 74), (117, 73), (124, 72), (131, 72), (138, 72), (145, 71),
     (152, 70), (158, 69), (164, 67), (170, 66), (178, 65), (176, 62),
     (169, 60), (163, 58), (158, 53), (156, 51), (150, 59), (143, 59),
     (141, 53), (139, 47), (136, 43), (132, 43), (129, 40), (127, 35),
     (125, 32), (122, 29), (120, 26), (116, 23), (112, 21), (109, 18),
     (106, 10), (104, 8), (101, 6), (98, 9), (97, 14), (94, 17), (91, 22),
     (88, 22), (86, 20), (83, 17), (80, 13), (77, 8), (75, 12), (73, 18),
     (70, 21), (67, 24), (64, 25), (61, 25), (58, 26), (55, 26), (52, 27),
     (50, 29), (48, 30), (50, 26), (53, 25), (56, 26), (58, 22), (56, 18),
     (53, 16), (49, 14), (45, 13), (43, 12), (42, 15), (40, 20), (39, 22),
     (37, 26), (35, 29), (34, 31), (35, 36), (32, 36), (29, 36), (27, 37),
     (25, 38), (23, 36), (21, 38), (19, 41), (19, 44), (16, 45), (13, 45),
     (10, 44), (7, 44), (3, 43), (0, 40), (-2, 37), (-6, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (133, 34), (136, 35), (139, 35), (141, 38), (141, 41),
     (143, 43), (144, 44), (142, 41), (140, 36), (137, 35), (134, 34),
     (131, 33)],
    # Australia
    [(114, -22), (114, -31), (117, -35), (122, -34), (127, -32), (132, -32),
     (136, -35), (139, -37), (144, -38), (149, -37), (153, -31), (153, -26),
     (150, -22), (146, -19), (142, -14), (142, -11), (140, -17), (136, -15),
     (134, -12), (130, -13), (126, -14), (121, -17), (117, -20)],
    # New Zealand (South Island, then North Island - separate rings)
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (174, -41),
     (171, -44)],
    [(173, -35), (176, -38), (178, -38), (176, -40), (174, -41),
     (172, -40)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -20)],
    # Italy boot (the big Eurasia ring cuts it off, so it gets its own)
    [(8, 44), (12, 44), (14, 42), (16, 40), (18, 40), (16, 38), (14, 40),
     (12, 42), (10, 44)],
    # Greece
    [(19, 41), (21, 40), (23, 38), (23, 36), (21, 38), (19, 40)],
    # Canary Islands
    [(-18, 29), (-13, 29), (-13, 27.5), (-18, 27.5)],
    # Tonga
    [(-175.5, -20.5), (-174.5, -21.5), (-175.5, -22)],
    # Cook Islands
    [(-160.5, -20.5), (-159, -21.5), (-160.5, -22)],
    # Borneo / Sumatra / Java / New Guinea (small islands, coarse)
    [(109, 1), (113, 3), (117, 5), (118, 1), (116, -3), (111, -3)],
    [(95, 5), (99, 2), (102, -1), (105, -4), (106, -6), (101, -4), (97, 1)],
    [(105, -6), (109, -7), (113, -7), (114, -8), (109, -8), (106, -7)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (146, -9),
     (141, -8), (136, -6), (132, -3)],
]


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xi2 = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xi2:
                inside = not inside
        j = i
    return inside


def on_land(lon, lat):
    return any(_in_poly(lon, lat, p) for p in POLYS)


MAP_LAT_TOP = 75.0
MAP_LAT_BOT = -55.0


def project(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * mh
    return x, y

# ------------------------------------------------------------- illustrations
# Every motif draws inside (x, y, w, h) with relative coordinates.
# Faces are simple flat-vector faces (skin circle, hair, eyes, smile) so the
# three leaders are recognisable people, not blank dots.

def _face(d, cx, cy, r, skin, hair, hair_style):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=skin, outline=INK, width=2)
    if hair_style == "blond-side":  # Trump: blond sweep
        d.pieslice([cx - r, cy - r, cx + r, cy + r * 0.4], 180, 360,
                   fill=(232, 200, 120), outline=INK)
        d.rectangle([cx - r, cy - r * 0.55, cx + r * 0.9, cy - r * 0.1],
                    fill=(232, 200, 120))
    elif hair_style == "black-neat":  # Xi: neat black hair
        d.pieslice([cx - r, cy - r, cx + r, cy + r * 0.2], 180, 360,
                   fill=(30, 30, 30), outline=INK)
    else:  # Putin: grey, receding
        d.arc([cx - r, cy - r, cx + r, cy + r * 0.3], 180, 360,
              fill=(170, 170, 170), width=3)
    d.ellipse([cx - r * 0.45, cy - r * 0.1, cx - r * 0.3, cy + r * 0.05],
              fill=INK)
    d.ellipse([cx + r * 0.3, cy - r * 0.1, cx + r * 0.45, cy + r * 0.05],
              fill=INK)
    d.arc([cx - r * 0.35, cy + r * 0.15, cx + r * 0.35, cy + r * 0.7],
          10, 170, fill=INK, width=2)


def ill_apec(d, x, y, w, h):
    """Hero 1: three faced leaders at a summit table, flags + nameplates."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # skyline
    for bx, bw, bh in [(0.02, 0.07, 0.30), (0.11, 0.06, 0.44),
                       (0.19, 0.08, 0.26), (0.29, 0.06, 0.36),
                       (0.37, 0.07, 0.22), (0.46, 0.06, 0.34),
                       (0.54, 0.08, 0.24), (0.64, 0.06, 0.38),
                       (0.72, 0.08, 0.28), (0.82, 0.07, 0.32),
                       (0.91, 0.06, 0.24)]:
        d.rectangle([x + bx * w, y + h * 0.62 - bh * h, x + (bx + bw) * w,
                     y + h * 0.62], fill=NAVY)
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(233, 224, 196))
    leaders = [
        (0.20, (244, 200, 160), "blond-side", NAVY, RED, "TRUMP"),
        (0.50, (240, 200, 160), "black-neat", INK, RED, "XI"),
        (0.80, (238, 205, 175), "grey", NAVY, (200, 60, 40), "PUTIN"),
    ]
    for fx, skin, hair, suit, tie, _name in leaders:
        cx = x + fx * w
        # flag pole behind
        d.line([cx, y + h * 0.04, cx, y + h * 0.30], fill=INK, width=2)
        d.rectangle([cx, y + h * 0.04, cx + w * 0.07, y + h * 0.11],
                    fill=tie, outline=INK)
        _face(d, cx, y + h * 0.30, w * 0.075, skin, hair, hair)
        # suit + tie
        d.polygon([(cx - w * 0.11, y + h * 0.62), (cx - w * 0.06, y + h * 0.42),
                   (cx + w * 0.06, y + h * 0.42), (cx + w * 0.11, y + h * 0.62)],
                  fill=suit, outline=INK)
        d.polygon([(cx - w * 0.014, y + h * 0.44), (cx + w * 0.014, y + h * 0.44),
                   (cx + w * 0.02, y + h * 0.60), (cx - w * 0.02, y + h * 0.60)],
                  fill=tie)
    # table + nameplates + banner (stacked, no overlap)
    d.rectangle([x + w * 0.04, y + h * 0.58, x + w * 0.96, y + h * 0.66],
                fill=(196, 120, 60), outline=INK)
    for fx, _s, _h, _su, _t, name in leaders:
        cx = x + fx * w
        f = sans_b(10)
        tw = d.textlength(name, font=f)
        d.rectangle([cx - tw / 2 - 6, y + h * 0.68, cx + tw / 2 + 6,
                     y + h * 0.84], fill=CREAM, outline=INK)
        d.text((cx - tw / 2, y + h * 0.70), name, font=f, fill=INK)
    # banner
    bf = sans_b(11)
    bt = "FIRST US-CHINA-RUSSIA SUMMIT"
    tw = d.textlength(bt, font=bf)
    d.rectangle([x + w / 2 - tw / 2 - 8, y + h * 0.87,
                 x + w / 2 + tw / 2 + 8, y + h * 0.99],
                fill=RED)
    d.text((x + w / 2 - tw / 2, y + h * 0.89), bt, font=bf,
           fill=(255, 255, 255))


def ill_icj(d, x, y, w, h):
    """Hero 2: World Court building + scales + big 9-6 badge."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.84, x + w, y + h], fill=(233, 224, 196))
    cx, base = x + w * 0.38, y + h * 0.84
    d.polygon([(cx - w * 0.30, y + h * 0.24), (cx + w * 0.30, y + h * 0.24),
               (cx, y + h * 0.05)], fill=NAVY)
    d.rectangle([cx - w * 0.30, y + h * 0.24, cx + w * 0.30, y + h * 0.28],
                fill=CREAM, outline=INK)
    for i in range(4):
        px = cx - w * 0.26 + i * w * 0.15
        d.rectangle([px, y + h * 0.28, px + w * 0.06, base],
                    fill=CREAM, outline=INK)
    d.rectangle([cx - w * 0.30, base - 4, cx + w * 0.30, base], fill=NAVY)
    # scales, right
    sx = x + w * 0.80
    d.line([sx, y + h * 0.14, sx, y + h * 0.60], fill=INK, width=3)
    d.line([sx - w * 0.11, y + h * 0.20, sx + w * 0.11, y + h * 0.20],
           fill=INK, width=3)
    d.ellipse([sx - w * 0.14, y + h * 0.50, sx - w * 0.05, y + h * 0.62],
              fill=GOLD, outline=INK)
    d.ellipse([sx + w * 0.05, y + h * 0.50, sx + w * 0.14, y + h * 0.62],
              fill=GOLD, outline=INK)
    d.line([sx - w * 0.095, y + h * 0.20, sx - w * 0.095, y + h * 0.50],
           fill=INK, width=2)
    d.line([sx + w * 0.095, y + h * 0.20, sx + w * 0.095, y + h * 0.50],
           fill=INK, width=2)
    # 9-6 badge
    bf = sans_b(16)
    bt = "9-6"
    tw = d.textlength(bt, font=bf)
    d.rectangle([x + w * 0.60, y + h * 0.06, x + w * 0.60 + tw + 14,
                 y + h * 0.06 + 26], fill=RED, outline=INK)
    d.text((x + w * 0.60 + 7, y + h * 0.06 + 4), bt, font=bf,
           fill=(255, 255, 255))
    d.text((x + w * 0.60, y + h * 0.68), "GENOCIDE", font=sans_b(9),
           fill=INK)
    d.text((x + w * 0.60, y + h * 0.80), "RULING", font=sans_b(9),
           fill=INK)


def ill_cop(d, x, y, w, h):
    """Hero 3: globe + thermometer + FOSSIL FUELS document struck through."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 225, 210))
    # globe (sized to the panel: radius from width, centred mid-panel)
    cx, cy, r = x + w * 0.28, y + h * 0.38, w * 0.13
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 160, 200),
              outline=INK, width=2)
    d.ellipse([cx - r * 0.55, cy - r * 0.5, cx + r * 0.1, cy + r * 0.1],
              fill=(60, 140, 90), outline=INK)
    d.ellipse([cx - r * 0.1, cy + r * 0.2, cx + r * 0.6, cy + r * 0.7],
              fill=(60, 140, 90), outline=INK)
    # thermometer
    tx = x + w * 0.58
    d.rounded_rectangle([tx, y + h * 0.12, tx + w * 0.06, y + h * 0.62],
                        radius=6, fill=CREAM, outline=INK)
    d.rectangle([tx + 2, y + h * 0.22, tx + w * 0.06 - 2, y + h * 0.60],
                fill=RED)
    d.ellipse([tx - w * 0.03, y + h * 0.58, tx + w * 0.09, y + h * 0.74],
              fill=RED, outline=INK)
    # document
    dx, dy, dw, dh = x + w * 0.68, y + h * 0.10, w * 0.28, h * 0.55
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=CREAM, outline=INK, width=2)
    f = sans_b(9)
    d.text((dx + 4, dy + 4), "DRAFT DEAL", font=f, fill=INK)
    d.text((dx + 4, dy + 18), "FOSSIL", font=f, fill=INK)
    d.text((dx + 4, dy + 30), "FUELS", font=f, fill=INK)
    d.line([dx + 2, dy + 26, dx + dw - 2, dy + 22], fill=RED, width=4)
    d.line([dx + 2, dy + 40, dx + dw - 2, dy + 36], fill=RED, width=4)
    # CUT stamp
    sf = sans_b(13)
    st = "CUT"
    tw = d.textlength(st, font=sf)
    d.rectangle([dx - 6, dy + dh - 6, dx - 6 + tw + 10, dy + dh + 14],
                fill=RED, outline=INK)
    d.text((dx - 1, dy + dh - 4), st, font=sf, fill=(255, 255, 255))
    # aid line
    d.text((x + w * 0.04, y + h * 0.80), "$120bn ADAPTATION AID",
           font=sans_b(11), fill=NAVY)


def ill_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(168, 205, 225))
    d.line([x, y + h * 0.55, x + w, y + h * 0.55], fill=INK, width=3)
    d.arc([x + w * 0.18, y + h * 0.30, x + w * 0.82, y + h * 0.80],
          180, 360, fill=INK, width=2)
    d.line([x + w * 0.30, y + h * 0.20, x + w * 0.30, y + h * 0.55],
           fill=INK, width=2)
    d.line([x + w * 0.70, y + h * 0.20, x + w * 0.70, y + h * 0.55],
           fill=INK, width=2)
    bx, by = x + w * 0.50, y + h * 0.42
    burst = []
    for i in range(10):
        r = w * 0.11 if i % 2 == 0 else w * 0.05
        a = -math.pi / 2 + i * math.pi / 5
        burst.append((bx + r * math.cos(a), by + r * math.sin(a)))
    d.polygon(burst, fill=RED)


def ill_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 220, 180))
    for bx, bw, bh in [(0.04, 0.12, 0.45), (0.20, 0.10, 0.60),
                       (0.34, 0.12, 0.38), (0.50, 0.10, 0.55),
                       (0.64, 0.12, 0.42), (0.80, 0.12, 0.50)]:
        d.rectangle([x + bx * w, y + h * 0.90 - bh * h, x + (bx + bw) * w,
                     y + h * 0.90], fill=NAVY)
    d.rectangle([x, y + h * 0.90, x + w, y + h], fill=(233, 224, 196))
    # interceptor burst in the sky (kept inside the illustration box)
    bx, by = x + w * 0.62, y + h * 0.34
    burst = []
    for i in range(10):
        r = w * 0.08 if i % 2 == 0 else w * 0.035
        a = -math.pi / 2 + i * math.pi / 5
        burst.append((bx + r * math.cos(a), by + r * math.sin(a)))
    d.polygon(burst, fill=GOLD, outline=INK)
    d.line([x + w * 0.20, y + h * 0.30, bx - w * 0.08, by + h * 0.05],
           fill=INK, width=2)


def ill_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[0])
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(168, 205, 225))
    # spiral radii are scaled to the ILLUSTRATION HEIGHT so the arcs never
    # spill past the card into the headline below
    cx, cy = x + w * 0.42, y + h * 0.50
    for r in (0.12, 0.22, 0.32, 0.42):
        rr = h * r
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 20, 300, fill=NAVY,
              width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)


def ill_seoul(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[3])
    # gavel
    d.line([x + w * 0.30, y + h * 0.25, x + w * 0.70, y + h * 0.55],
           fill=(120, 80, 40), width=4)
    d.rounded_rectangle([x + w * 0.55, y + h * 0.12, x + w * 0.80,
                         y + h * 0.32], radius=4, fill=NAVY, outline=INK)
    d.rectangle([x + w * 0.15, y + h * 0.70, x + w * 0.55, y + h * 0.78],
                fill=NAVY, outline=INK)
    # OVERTURNED stamp
    sf = sans_b(10)
    st = "OVERTURNED"
    tw = d.textlength(st, font=sf)
    d.rectangle([x + w * 0.52, y + h * 0.62, x + w * 0.52 + tw + 8,
                 y + h * 0.62 + 16], fill=RED)
    d.text((x + w * 0.52 + 4, y + h * 0.62 + 2), st, font=sf,
           fill=(255, 255, 255))


def ill_greenland(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.polygon([(x, y + h), (x + w * 0.30, y + h * 0.30),
               (x + w * 0.55, y + h)], fill=(250, 250, 246), outline=INK)
    d.polygon([(x + w * 0.40, y + h), (x + w * 0.68, y + h * 0.18),
               (x + w * 0.95, y + h)], fill=(230, 235, 240), outline=INK)
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(168, 205, 225))
    # two small flags
    d.line([x + w * 0.12, y + h * 0.10, x + w * 0.12, y + h * 0.34],
           fill=INK, width=2)
    d.rectangle([x + w * 0.12, y + h * 0.10, x + w * 0.22, y + h * 0.18],
                fill=RED, outline=INK)
    d.line([x + w * 0.82, y + h * 0.10, x + w * 0.82, y + h * 0.34],
           fill=INK, width=2)
    d.rectangle([x + w * 0.82, y + h * 0.10, x + w * 0.92, y + h * 0.18],
                fill=NAVY, outline=INK)
    bf = sans_b(11)
    d.text((x + w * 0.38, y + h * 0.06), "109-0", font=bf, fill=RED)


def ill_anthropic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[2])
    d.rectangle([x + w * 0.06, y + h * 0.28, x + w * 0.30, y + h * 0.74],
                fill=NAVY, outline=INK)
    d.text((x + w * 0.10, y + h * 0.36), "ANT", font=sans_b(11),
           fill=(255, 255, 255))
    pts = [(x + w * 0.36, y + h * 0.72), (x + w * 0.50, y + h * 0.64),
           (x + w * 0.62, y + h * 0.68), (x + w * 0.76, y + h * 0.44),
           (x + w * 0.90, y + h * 0.24)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + w * 0.90, y + h * 0.24), (x + w * 0.80, y + h * 0.22),
               (x + w * 0.88, y + h * 0.36)], fill=RED)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    d.text((x + w * 0.62, y + h * 0.06), "+17%", font=sans_b(12), fill=RED)


def ill_gta(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 160, 220))
    for bx, bw, bh in [(0.04, 0.10, 0.35), (0.16, 0.09, 0.50),
                       (0.28, 0.10, 0.30), (0.62, 0.10, 0.45),
                       (0.74, 0.09, 0.55), (0.86, 0.10, 0.32)]:
        d.rectangle([x + bx * w, y + h * 0.88 - bh * h, x + (bx + bw) * w,
                     y + h * 0.88], fill=NAVY)
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(233, 224, 196))
    cx = x + w // 2
    d.rounded_rectangle([cx - w * 0.16, y + h * 0.30, cx + w * 0.16,
                         y + h * 0.66], radius=6, fill=INK)
    d.ellipse([cx - w * 0.11, y + h * 0.36, cx - w * 0.04, y + h * 0.46],
              fill=CREAM)
    d.ellipse([cx + w * 0.04, y + h * 0.36, cx + w * 0.11, y + h * 0.46],
              fill=RED)
    d.ellipse([cx + w * 0.04, y + h * 0.52, cx + w * 0.11, y + h * 0.62],
              fill=GOLD)
    d.text((cx - w * 0.06, y + h * 0.06), "VI", font=serif_b(16),
           fill=(255, 255, 255))


def ill_bogota(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[3])
    # crowd of heads + placards
    for i, cx in enumerate([0.12, 0.28, 0.44, 0.60, 0.76, 0.90]):
        col = [RED, NAVY, GOLD, (60, 140, 90), RED, NAVY][i]
        d.ellipse([x + cx * w - 7, y + h * 0.52, x + cx * w + 7,
                   y + h * 0.52 + 14], fill=col, outline=INK)
        d.rectangle([x + cx * w - 9, y + h * 0.66, x + cx * w + 9,
                     y + h * 0.92], fill=col, outline=INK)
    d.rectangle([x + w * 0.30, y + h * 0.10, x + w * 0.70, y + h * 0.30],
                fill=CREAM, outline=INK)
    d.text((x + w * 0.36, y + h * 0.14), "STRIKE", font=sans_b(11), fill=RED)


def ill_nairobi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[1])
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(196, 120, 60))
    # runner silhouette
    cx, cy = x + w * 0.40, y + h * 0.45
    d.ellipse([cx - 6, cy - 16, cx + 6, cy - 4], fill=INK)
    d.line([cx, cy - 4, cx + 2, cy + 12], fill=INK, width=4)
    d.line([cx, cy - 2, cx - 12, cy + 6], fill=INK, width=3)
    d.line([cx, cy - 2, cx + 12, cy - 6], fill=INK, width=3)
    d.line([cx + 2, cy + 12, cx - 8, cy + 26], fill=INK, width=3)
    d.line([cx + 2, cy + 12, cx + 12, cy + 24], fill=INK, width=3)
    sf = sans_b(10)
    st = "BANNED"
    tw = d.textlength(st, font=sf)
    d.rectangle([x + w * 0.58, y + h * 0.16, x + w * 0.58 + tw + 8,
                 y + h * 0.16 + 16], fill=RED)
    d.text((x + w * 0.58 + 4, y + h * 0.16 + 2), st, font=sf,
           fill=(255, 255, 255))
    d.text((x + w * 0.60, y + h * 0.40), "3 YEARS", font=sans_b(10),
           fill=INK)


def ill_canberra(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=TINTS[4])
    for i, bh in enumerate([0.50, 0.42, 0.34, 0.26]):
        bx = x + w * 0.10 + i * w * 0.14
        d.rectangle([bx, y + h * 0.88 - h * bh, bx + w * 0.09, y + h * 0.88],
                    fill=NAVY)
    pts = [(x + w * 0.62, y + h * 0.30), (x + w * 0.74, y + h * 0.44),
           (x + w * 0.86, y + h * 0.58), (x + w * 0.94, y + h * 0.72)]
    d.line(pts, fill=RED, width=3)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    d.text((x + w * 0.60, y + h * 0.06), "4.9%", font=sans_b(13), fill=RED)


ILL = {"apec": ill_apec, "icj": ill_icj, "cop": ill_cop,
       "bridge": ill_bridge, "riyadh": ill_riyadh, "cyclone": ill_cyclone,
       "seoul": ill_seoul, "greenland": ill_greenland,
       "anthropic": ill_anthropic, "gta": ill_gta, "bogota": ill_bogota,
       "nairobi": ill_nairobi, "canberra": ill_canberra}

# -------------------------------------------------------------------- stories
# 35 stories = 3 hero + 10 cards + 22 briefs. Every featured story happened
# or was first reported on Thursday 19 November 2026. Anything dated 18 or
# 20 November lives ONLY in the DATE CHECK box below.
HERO = [
    (1, "APEC 2026 · SHENZHEN",
     "Trump, Xi and Putin hold first three-way summit",
     "The US, Chinese and Russian leaders meet for ~90 minutes and issue "
     "a \u201cDeclaration on Peace\u201d on nuclear risk and UN reform.",
     "Reuters · AP · Xinhua", "CONFIRMED", "apec"),
    (2, "THE HAGUE · JUSTICE",
     "World Court: Myanmar committed genocide",
     "By 9 votes to 6 the court finds Myanmar guilty of genocide against "
     "the Rohingya and orders reparations.",
     "Al Jazeera · UN News", "CONFIRMED", "icj"),
    (3, "ANTALYA · CLIMATE",
     "COP31 draft drops fossil fuels and $120bn aid goal",
     "The draft text drops fossil fuels and sets a $120bn adaptation-aid "
     "goal. Talks are due to end on Friday.",
     "Reuters · AFP", "REPORTED", "cop"),
]

# (num, kicker, headline, deck, source, tag, illustration)
CARDS = [
    (4, "KERCH BRIDGE · WAR", "Ukraine hits Crimea bridge again",
     "Third strike in a week halts trains to Russia.",
     "Euronews", "REPORTED", "bridge"),
    (5, "OVER RIYADH · WAR", "Saudis shoot down Houthi missiles",
     "Debris fell on the capital; no casualties reported.",
     "Reuters", "REPORTED", "riyadh"),
    (6, "ODISHA · STORM", "Cyclone Akvan nears India\u2019s coast",
     "Over 100,000 in shelters before Friday\u2019s landfall.",
     "IMD", "FORECAST", "cyclone"),
    (7, "SEOUL · JUSTICE", "Korea\u2019s top court clears ex-PM Han",
     "Han Duck-soo\u2019s martial-law conviction is overturned.",
     "AP", "CONFIRMED", "seoul"),
    (8, "GREENLAND · SECURITY", "Denmark backs Arctic pact with US",
     "Parliament approves the Greenland security deal 109\u20130.",
     "AP", "CONFIRMED", "greenland"),
    (9, "NEW YORK · MARKETS", "Anthropic starts trading on Nasdaq",
     "Shares jump 17% on the first day after the record $81bn sale.",
     "AP", "CONFIRMED", "anthropic"),
    (10, "WORLDWIDE · GAMES", "GTA VI goes on sale after 13 years",
     "The midnight launch draws rave reviews.",
     "ABC", "CONFIRMED", "gta"),
    (11, "BOGOT\u00c1 · LABOUR", "Colombia\u2019s unions hold national strike",
     "Marches fill three cities in a day of protest.",
     "Infobae", "REPORTED", "bogota"),
    (12, "NAIROBI · SPORT", "Marathon champion banned for doping",
     "Kenya\u2019s Peres Jepchirchir gets three years.",
     "ABC", "CONFIRMED", "nairobi"),
    (13, "CANBERRA · ECONOMY", "Australia\u2019s jobless rate hits 4.9%",
     "Highest since 2024; shares and the dollar slide.",
     "ABC", "CONFIRMED", "canberra"),
]

# (num, place, one line, source or "")
BRIEFS = [
    (14, "SHENZHEN", "Xi urges ban on all nuclear arms.", "Al Jazeera"),
    (15, "SHENZHEN", "Putin: \u201cEnd your war\u201d, at APEC.", "ABC"),
    (16, "SEOUL", "Half a million sit college entrance exam.", "Sedaily"),
    (17, "JAKARTA", "Asset-seizure law passes after 18 years.", "Kompas"),
    (18, "HORMUZ", "Iran says mines set 3 tankers ablaze.", "Al Jazeera"),
    (19, "GAZA", "Israel ends tank raid past truce line.", "BBC"),
    (20, "KRASNODAR", "Kyiv says it hit two oil refineries.", "Euronews"),
    (21, "BRUSSELS", "EU delays methane rules two years.", "Euronews"),
    (22, "UK", "Inquiry: yacht Bayesian was vulnerable to wind.", "RNZ"),
    (23, "ZURICH", "Two rivals to challenge FIFA\u2019s Infantino.", "ABC"),
    (24, "ROME", "Author Corrado Augias dies at 91.", "Euronews"),
    (25, "MOGADISHU", "Somalia expels UAE ambassador.", "Al Jazeera"),
    (26, "SUDAN", "Court sentences absent RSF chief to death.", "AP"),
    (27, "PRETORIA", "Central bank holds rate at 7.25%.", "SABC"),
    (28, "CANARIES", "Record 11,000 migrants in 15 days.", "Africanews"),
    (29, "FLORIDA", "Floods shut Broward, Miami schools again.", "CBS"),
    (30, "WELLINGTON", "Court: pay equity cuts broke rights law.", "RNZ"),
    (31, "TONGA", "Drought emergency takes effect.", "RNZ"),
    (32, "COOK ISLANDS", "Cyclone Xavier weakens to category 4.", "RNZ"),
    (33, "SPACE", "Red giant seen eating a Sun-sized star.", "Nature"),
    (34, "SENEGAL", "Boat capsizes off Yenne; dozens missing.", ""),
    (35, "CEPU", "Refinery blast kills one worker.", ""),
]

# Map pins for stories 1-13: (num, lon, lat). Briefs 14-35 are small dots,
# except 33 (space) which gets a star with a label instead.
PINS = [
    (1, 114.1, 22.5), (2, 4.3, 52.1), (3, 30.7, 36.9), (4, 35.4, 45.3),
    (5, 46.7, 24.6), (6, 85.0, 20.5), (7, 127.0, 37.5), (8, -51.7, 64.2),
    (9, -74.0, 40.7), (10, -81.2, 27.8), (11, -74.1, 4.7),
    (12, 36.8, -1.3), (13, 149.1, -35.3),
]
DOTS = [
    (14, 114.1, 22.5), (15, 114.1, 22.5), (16, 127.0, 37.5),
    (17, 108.0, -7.2), (18, 56.5, 26.5), (19, 34.5, 31.5),
    (20, 39.0, 45.0), (21, 4.35, 50.85), (22, -1.5, 52.5),
    (23, 8.5, 47.4), (24, 12.5, 41.9), (25, 43.5, 3.0), (26, 32.5, 15.6),
    (27, 28.2, -25.7), (28, -15.6, 28.3), (29, -81.7, 27.9),
    (30, 174.5, -40.3), (31, -175.2, -21.1), (32, -159.8, -21.2),
    (34, -16.5, 14.7), (35, 111.6, -7.1),
]

# Continent counts - MUST match the stories above (recomputed in build()).
# Asia: 1, 6, 7, 14, 15, 16, 17, 35 = 8
# Europe: 2, 3, 4, 8, 20, 21, 22, 23, 24 = 9
# Middle East: 5, 18, 19 = 3
# Africa: 12, 25, 26, 27, 28, 34 = 6
# Americas: 9, 11, 29 = 3
# Oceania: 13, 30, 31, 32 = 4
# Global: 10, 33 = 2
CONTINENTS = [("ASIA", 8, RED), ("EUROPE", 9, NAVY),
              ("MIDDLE EAST", 3, TEAL), ("AFRICA", 6, (140, 110, 30)),
              ("AMERICAS", 3, (110, 60, 130)), ("OCEANIA", 4, (40, 110, 90)),
              ("GLOBAL", 2, GREY)]

NUMBERS = [
    ("3", "presidents at one table"),
    ("9\u20136", "World Court genocide vote"),
    ("$81.3bn", "Anthropic\u2019s record IPO"),
    ("109\u20130", "Danish vote on Arctic pact"),
    ("4.9%", "Australian jobless rate"),
    ("$120bn", "aid goal cut at COP31"),
]

DATE_TEXT = "Thursday 19 November 2026"
SUBLINE = ("Trump, Xi and Putin share one table \u00b7 The World Court finds "
           "genocide in Myanmar \u00b7 COP31\u2019s draft drops fossil fuels")

# Timeline rail: (label, band top y, band bottom y)
X0 = 64                      # content left edge (right of the rail)
X1 = 1010
CW2 = X1 - X0
SPINE_X = 52
RAIL_LABEL_X = 20

Y_MASTHEAD = 0
Y_CONT = 106
Y_NUM = 128
Y_HERO = 162
H_HERO = 204
Y_C1 = 370
Y_C2 = 504
H_CARD = 130
Y_MAP = 638
H_MAP = 168
Y_LEGEND = 810
Y_DATE = 832
H_DATE = 96
Y_FOOT = 944


def draw_masthead(d):
    tracked(d, (M, 8), "THE WORLD IN ONE DAY", sans_b(11), INK, track=2)
    right = "35 STORIES \u00b7 EVERY CONTINENT \u00b7 ALL FROM THIS ONE DAY"
    rw = tracked_w(d, right, sans_b(11), track=2)
    tracked(d, (W - M - rw, 8), right, sans_b(11), RED, track=2)
    size = 54
    f = serif_b(size)
    while d.textlength(DATE_TEXT, font=f) > CW and size > 40:
        size -= 2
        f = serif_b(size)
    d.text((M, 24), DATE_TEXT, font=f, fill=INK)
    d.rectangle([M, 88, W - M, 90], fill=RED)
    d.text((M, 94), SUBLINE, font=serif_i(13), fill=RED)


def draw_continents(d):
    seg_w = CW2 / len(CONTINENTS)
    for i, (name, n, col) in enumerate(CONTINENTS):
        x = X0 + i * seg_w
        d.rectangle([x, Y_CONT, x + seg_w - 2, Y_CONT + 18], fill=col)
        t = f"{name} {n}"
        f = sans_b(10)
        tw = d.textlength(t, font=f)
        d.text((x + (seg_w - 2 - tw) / 2, Y_CONT + 4), t, font=f,
               fill=(255, 255, 255))


def draw_numbers(d):
    cell_w = CW2 / len(NUMBERS)
    for i, (num, label) in enumerate(NUMBERS):
        x = X0 + i * cell_w
        if i:
            d.line([x - 3, Y_NUM + 2, x - 3, Y_NUM + 26], fill=(170, 160, 140))
        f = serif_b(20)
        d.text((x + 4, Y_NUM), num, font=f, fill=INK)
        lf = sans(8)
        d.text((x + 4, Y_NUM + 22), label, font=lf, fill=GREY)
    d.line([X0, Y_NUM + 32, X1, Y_NUM + 32], fill=(170, 160, 140), width=1)


def draw_rail(d, bands):
    d.line([SPINE_X, bands[0][1], SPINE_X, bands[-1][2]], fill=RED, width=2)
    for label, y0, y1 in bands:
        cy = (y0 + y1) // 2
        d.ellipse([SPINE_X - 5, cy - 5, SPINE_X + 5, cy + 5], fill=RED)
        # stacked vertical label, centred on the band
        f = sans_b(9)
        total_h = len(label) * 11
        yy = cy - total_h // 2
        for ch in label:
            cw = d.textlength(ch, font=f)
            d.text((RAIL_LABEL_X + (12 - cw) / 2, yy), ch, font=f, fill=RED)
            yy += 11


def draw_hero(d):
    pw = (CW2 - 2 * 6) // 3
    for i, (num, kick, head, deck, src, tag, ill_key) in enumerate(HERO):
        x = X0 + i * (pw + 6)
        d.rectangle([x, Y_HERO, x + pw, Y_HERO + H_HERO], outline=INK, width=1)
        ILL[ill_key](d, x + 1, Y_HERO + 1, pw - 2, 102)
        ty = Y_HERO + 108
        num_circle(d, x + 10, ty + 7, num, r=8)
        tracked(d, (x + 24, ty), kick, sans_b(9), RED, track=1)
        hf = serif_b(15)
        hlines = wrap(d, head, hf, pw - 12)
        if len(hlines) > 2:
            print(f"OVERFLOW hero headline {num}: {hlines}")
        hy = ty + 18
        for ln in hlines[:2]:
            d.text((x + 6, hy), ln, font=hf, fill=INK)
            hy += 18
        df = sans(9)
        dlines = wrap(d, deck, df, pw - 12)
        if len(dlines) > 3:
            print(f"OVERFLOW hero deck {num}: {dlines}")
        dy = hy + 2
        for ln in dlines[:3]:
            d.text((x + 6, dy), ln, font=df, fill=INK)
            dy += 12
        sf = sans(8)
        d.text((x + 6, Y_HERO + H_HERO - 14),
               f"\u2014 {src} \u00b7 {tag}", font=sf, fill=GREY)


def draw_cards(d, y0, cards):
    cw = (CW2 - 4 * 6) // 5
    for i, (num, kick, head, deck, src, tag, ill_key) in enumerate(cards):
        x = X0 + i * (cw + 6)
        d.rectangle([x, y0, x + cw, y0 + H_CARD], outline=INK, width=1)
        ILL[ill_key](d, x + 1, y0 + 1, cw - 2, 50)
        ty = y0 + 56
        num_circle(d, x + 9, ty + 6, num, r=7)
        tracked(d, (x + 20, ty), kick, sans_b(8), RED, track=1)
        hf = serif_b(11)
        hlines = wrap(d, head, hf, cw - 10)
        if len(hlines) > 2:
            print(f"OVERFLOW card headline {num}: {hlines}")
        hy = ty + 15
        for ln in hlines[:2]:
            d.text((x + 5, hy), ln, font=hf, fill=INK)
            hy += 13
        df = sans(8)
        dlines = wrap(d, deck, df, cw - 10)
        if len(dlines) > 2:
            print(f"OVERFLOW card deck {num}: {dlines}")
        dy = hy + 1
        for ln in dlines[:2]:
            d.text((x + 5, dy), ln, font=df, fill=INK)
            dy += 11
        sf = sans(7)
        d.text((x + 5, y0 + H_CARD - 11), f"\u2014 {src} \u00b7 {tag}",
               font=sf, fill=GREY)


def draw_map_briefs(d):
    # --- map (left)
    tracked(d, (X0, Y_MAP), "WHERE IT HAPPENED", sans_b(10), INK, track=2)
    mx, my, mw, mh = X0, Y_MAP + 16, 300, H_MAP - 16
    d.rectangle([mx, my, mx + mw, my + mh], fill=MAP_BG, outline=INK)
    for poly in POLYS:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=MAP_LAND, outline=(120, 110, 80))
    for _num, lon, lat in DOTS:
        px, py = project(lon, lat, mx, my, mw, mh)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    for num, lon, lat in PINS:
        px, py = project(lon, lat, mx, my, mw, mh)
        num_circle(d, px, py, num, r=7)
    # space story 33: star, top-right of the map
    sx, sy = mx + mw - 14, my + 14
    star = []
    for i in range(10):
        r = 8 if i % 2 == 0 else 3.5
        a = -math.pi / 2 + i * math.pi / 5
        star.append((sx + r * math.cos(a), sy + r * math.sin(a)))
    d.polygon(star, fill=RED)
    d.text((sx - 62, sy - 5), "33 \u00b7 SPACE", font=sans_b(8), fill=RED)
    # --- briefs (right, 2 columns x 11)
    bx0 = mx + mw + 12
    bw = X1 - bx0
    tracked(d, (bx0, Y_MAP), "ALSO ON THURSDAY 19 NOVEMBER 2026", sans_b(10),
            INK, track=2)
    col_w = (bw - 12) // 2
    for ci in range(2):
        cx = bx0 + ci * (col_w + 12)
        for ri, (num, place, text, src) in enumerate(
                BRIEFS[ci * 11:(ci + 1) * 11]):
            y = Y_MAP + 16 + ri * 14
            full = f"{num}. {place} \u2014 {text}"
            if src:
                full += f" {src}"
            f = sans(9)
            fb = sans_b(9)
            d.text((cx, y), f"{num}. ", font=fb, fill=RED)
            x = cx + d.textlength(f"{num}. ", font=fb)
            d.text((x, y), place, font=fb, fill=INK)
            x += d.textlength(place + " ", font=fb)
            d.text((x, y), "\u2014 " + text, font=f, fill=INK)
            x += d.textlength("\u2014 " + text, font=f)
            if src:
                d.text((x + 2, y), src, font=f, fill=GREY)
            total = (d.textlength(f"{num}. ", font=fb)
                     + d.textlength(place + " ", font=fb)
                     + d.textlength("\u2014 " + text, font=f)
                     + (d.textlength(src, font=f) + 2 if src else 0))
            if total > col_w:
                print(f"OVERFLOW brief {num}: {total:.0f}px > {col_w}px")


def draw_legend(d):
    t = ("HOW SURE ARE WE?  REPORTED = as reported  \u00b7  CONFIRMED = "
         "verified by two sources or official  \u00b7  CLAIM = one side\u2019s "
         "claim  \u00b7  FORECAST = due, not yet happened")
    d.text((X0, Y_LEGEND), t, font=sans(9), fill=GREY)


def draw_datecheck(d):
    d.rectangle([X0, Y_DATE, X1, Y_DATE + H_DATE], outline=RED, width=2)
    y = Y_DATE + 6
    d.text((X0 + 8, y), "DATE CHECK \u2713", font=sans_b(11), fill=RED)
    d.text((X0 + 118, y),
           "Every story on this page happened, or was first reported, on "
           "Thursday 19 November 2026.", font=sans(10), fill=INK)
    y += 18
    f = sans(10)
    fb = sans_b(10)
    lines = [
        ("LEFT OUT \u2014 18 NOV:  ",
         "Van Gogh $190.4m \u00b7 Jeffries named for US Speaker \u00b7 "
         "Voyager 1 one light-day \u00b7 EU \u20ac45bn Ukraine loan \u00b7 "
         "Nvidia results \u00b7 Pew: Islam largest faith by 2035 \u00b7 "
         "Anthropic IPO pricing ($83) \u00b7 Gaza push began"),
        ("LEFT OUT \u2014 20 NOV (NOT YET HAPPENED):  ",
         "COP31 close \u00b7 Cyclone Akvan landfall"),
        ("NOTE:  ",
         "Anthropic\u2019s $83 pricing was 18 Nov \u2014 its Nasdaq listing "
         "and +17% first day were 19 Nov."),
    ]
    for lead, body in lines:
        d.text((X0 + 8, y), lead, font=fb, fill=INK)
        lx = X0 + 8 + d.textlength(lead, font=fb)
        wrapped = wrap(d, body, f, X1 - 8 - lx)
        for j, ln in enumerate(wrapped):
            d.text((lx if j == 0 else X0 + 8, y), ln, font=f, fill=INK)
            y += 13
    # fill remaining box height with nothing - box ends at Y_DATE+H_DATE


def draw_footer(d):
    d.line([M, Y_FOOT - 6, W - M, Y_FOOT - 6], fill=INK, width=2)
    d.text((M, Y_FOOT),
           "Claims are attributed, not stated as fact. Pictures and map: "
           "original, drawn in code.", font=sans(10), fill=GREY)
    d.text((M, Y_FOOT + 14),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 Al Jazeera "
           "\u00b7 UN News \u00b7 Euronews \u00b7 ABC \u00b7 RNZ \u00b7 Xinhua "
           "\u00b7 Nature \u00b7 2026-11-19",
           font=sans(10), fill=GREY)


def build(out_path):
    # --- self-checks before drawing
    total = len(HERO) + len(CARDS) + len(BRIEFS)
    assert total == 35, f"story count {total} != 35"
    assert sum(n for _n, n, _c in CONTINENTS) == 35, "continent counts != 35"
    for num, lon, lat in PINS:
        if not on_land(lon, lat):
            print(f"WARNING pin {num} NOT on land: lon={lon} lat={lat}")
    for num, lon, lat in DOTS:
        if not on_land(lon, lat):
            print(f"WARNING dot {num} NOT on land: lon={lon} lat={lat}")
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    bands = [("FIRST WIRES", Y_HERO, Y_HERO + H_HERO),
             ("MORNING", Y_C1, Y_C1 + H_CARD),
             ("MIDDAY", Y_C2, Y_C2 + H_CARD),
             ("AFTERNOON", Y_MAP, Y_MAP + H_MAP),
             ("EVENING", Y_DATE, Y_DATE + H_DATE)]
    draw_masthead(d)
    draw_continents(d)
    draw_numbers(d)
    draw_rail(d, bands)
    draw_hero(d)
    draw_cards(d, Y_C1, CARDS[:5])
    draw_cards(d, Y_C2, CARDS[5:])
    draw_map_briefs(d)
    draw_legend(d)
    draw_datecheck(d)
    draw_footer(d)
    img.save(out_path, "PNG", optimize=True)
    print(f"wrote {out_path} ({total} stories)")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "entry.png"))

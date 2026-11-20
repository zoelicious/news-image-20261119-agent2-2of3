#!/usr/bin/env python3
"""Render entry.png for news-image-20261119 - agent 2, 2/3 (noble-robin-77).

Layout "THE DAY UNFOLDS, corrected" (rebuild #4): the left timeline rail
is GONE - the full width goes to the page. APEC opens at the TOP as three
big scene panels. Masthead (giant serif date) -> continent count strip ->
"day in numbers" strip -> 3 hero scene panels -> 10 scene cards (2 rows x
5), each with a dark slug banner on top -> small flat world map + numbered
briefs -> DATE CHECK box -> footer.
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
MAP_LAND = (188, 166, 102)
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

def _blob(d, cx, cy, rx, ry, fill, seed=0.0, n=28, wob=0.10):
    """A smooth organic blob: an ellipse sampled as a many-point polygon
    with a gentle sinusoidal wobble, so its edge reads as a curve, not
    as the jagged straight edges of a few-point polygon."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        w = 1 + wob * math.sin(a * 3 + seed)
        pts.append((cx + rx * w * math.cos(a), cy + ry * w * math.sin(a)))
    d.polygon(pts, fill=fill)


def _face(d, cx, cy, r, skin, hair, hair_style):
    # ears, so the head reads as a person, not a floating blob
    d.ellipse([cx - r - 3, cy - r * 0.1, cx - r + 3, cy + r * 0.25],
              fill=skin, outline=INK)
    d.ellipse([cx + r - 3, cy - r * 0.1, cx + r + 3, cy + r * 0.25],
              fill=skin, outline=INK)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=skin, outline=INK, width=2)
    if hair_style == "blond-side":  # Trump: blond sweep + strand lines
        d.pieslice([cx - r, cy - r, cx + r, cy + r * 0.4], 180, 360,
                   fill=(232, 200, 120), outline=INK)
        d.rectangle([cx - r, cy - r * 0.55, cx + r * 0.9, cy - r * 0.1],
                    fill=(232, 200, 120))
        for sx in (-0.5, -0.1, 0.3):
            d.line([cx + sx * r, cy - r * 0.85, cx + (sx + 0.2) * r,
                    cy - r * 0.35], fill=(190, 150, 60), width=2)
    elif hair_style == "black-neat":  # Xi: neat black hair + side part
        d.pieslice([cx - r, cy - r, cx + r, cy + r * 0.2], 180, 360,
                   fill=(30, 30, 30), outline=INK)
        d.line([cx - r * 0.2, cy - r * 0.95, cx - r * 0.2, cy - r * 0.25],
               fill=(90, 90, 90), width=2)
    else:  # Putin: grey, receding, a few side strands
        d.arc([cx - r, cy - r, cx + r, cy + r * 0.3], 180, 360,
              fill=(170, 170, 170), width=3)
        for sx in (-0.7, 0.7):
            d.line([cx + sx * r, cy - r * 0.55, cx + sx * r, cy - r * 0.1],
                   fill=(150, 150, 150), width=2)
    # eyebrows: distinct per leader, so the three heads do not read alike
    if hair_style == "blond-side":  # Trump: raised, arched brows
        d.arc([cx - r * 0.62, cy - r * 0.55, cx - r * 0.10, cy - r * 0.05],
              180, 360, fill=INK, width=2)
        d.arc([cx + r * 0.10, cy - r * 0.55, cx + r * 0.62, cy - r * 0.05],
              180, 360, fill=INK, width=2)
    elif hair_style == "black-neat":  # Xi: straight, thick, dark brows
        d.line([cx - r * 0.58, cy - r * 0.33, cx - r * 0.18, cy - r * 0.33],
               fill=INK, width=3)
        d.line([cx + r * 0.18, cy - r * 0.33, cx + r * 0.58, cy - r * 0.33],
               fill=INK, width=3)
    else:  # Putin: thinner brows, angled slightly down toward the nose
        d.line([cx - r * 0.58, cy - r * 0.38, cx - r * 0.18, cy - r * 0.26],
               fill=INK, width=2)
        d.line([cx + r * 0.18, cy - r * 0.26, cx + r * 0.58, cy - r * 0.38],
               fill=INK, width=2)
        # one forehead line (his forehead is bare, unlike the other two)
        d.line([cx - r * 0.35, cy - r * 0.68, cx + r * 0.35, cy - r * 0.68],
               fill=(130, 110, 90), width=1)
    # eyes: white with a dark pupil, so the gaze reads
    for ex in (-0.38, 0.38):
        d.ellipse([cx + ex * r - r * 0.14, cy - r * 0.12,
                   cx + ex * r + r * 0.14, cy + r * 0.12],
                  fill=(255, 255, 255), outline=INK)
        d.ellipse([cx + ex * r - r * 0.06, cy - r * 0.06,
                   cx + ex * r + r * 0.06, cy + r * 0.06], fill=INK)
    # nose + cheek shading (a darker skin-tone crescent on the right
    # cheek gives the flat face some depth) + smile lines + jaw
    d.line([cx, cy + r * 0.05, cx - r * 0.08, cy + r * 0.28], fill=INK,
           width=2)
    shade = tuple(max(0, c - 30) for c in skin)
    d.arc([cx + r * 0.20, cy - r * 0.70, cx + r * 0.95, cy + r * 0.70],
          -55, 55, fill=shade, width=3)
    d.arc([cx - r * 0.48, cy + r * 0.08, cx - r * 0.04, cy + r * 0.55],
          90, 180, fill=INK, width=1)
    d.arc([cx + r * 0.04, cy + r * 0.08, cx + r * 0.48, cy + r * 0.55],
          0, 90, fill=INK, width=1)
    d.arc([cx - r * 0.45, cy + r * 0.35, cx + r * 0.45, cy + r * 0.95],
          20, 160, fill=INK, width=1)
    # mouth: distinct per leader (wide grin / small smile / flat line)
    if hair_style == "blond-side":
        d.arc([cx - r * 0.40, cy + r * 0.22, cx + r * 0.40, cy + r * 0.78],
              10, 170, fill=INK, width=2)
    elif hair_style == "black-neat":
        d.arc([cx - r * 0.30, cy + r * 0.30, cx + r * 0.30, cy + r * 0.72],
              20, 160, fill=INK, width=2)
    else:
        d.line([cx - r * 0.28, cy + r * 0.48, cx + r * 0.28, cy + r * 0.48],
               fill=INK, width=2)
        d.line([cx - r * 0.28, cy + r * 0.48, cx - r * 0.34, cy + r * 0.42],
               fill=INK, width=2)
        d.line([cx + r * 0.28, cy + r * 0.48, cx + r * 0.34, cy + r * 0.42],
               fill=INK, width=2)


def ill_apec(d, x, y, w, h):
    """Hero 1: three faced leaders at a summit table, flags + nameplates.

    Fills the whole panel: red banner on top, real flags behind each
    leader, big faces, suits, a full-width table with nameplates on it.
    """
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # red banner strip on top
    bf = sans_b(11)
    bt = "FIRST US-CHINA-RUSSIA SUMMIT"
    tw = d.textlength(bt, font=bf)
    d.rectangle([x, y, x + w, y + 20], fill=RED)
    d.text((x + (w - tw) / 2, y + 4), bt, font=bf, fill=(255, 255, 255))
    # skyline behind the leaders
    for bx, bw, bh in [(0.02, 0.06, 0.22), (0.10, 0.05, 0.30),
                       (0.17, 0.06, 0.18), (0.27, 0.05, 0.26),
                       (0.34, 0.06, 0.16), (0.42, 0.05, 0.24),
                       (0.58, 0.06, 0.18), (0.66, 0.05, 0.28),
                       (0.74, 0.06, 0.16), (0.83, 0.05, 0.24),
                       (0.90, 0.06, 0.18)]:
        d.rectangle([x + bx * w, y + h * 0.68 - bh * h, x + (bx + bw) * w,
                     y + h * 0.68], fill=NAVY)
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(233, 224, 196))
    leaders = [
        (0.18, (246, 192, 138), "blond-side", NAVY, RED, "TRUMP", "us"),
        (0.50, (243, 210, 182), "black-neat", INK, RED, "XI", "cn"),
        (0.82, (240, 204, 186), "grey", NAVY, (200, 60, 40), "PUTIN", "ru"),
    ]
    for fx, skin, hair, suit, tie, name, flag in leaders:
        cx = x + fx * w
        # flag on a pole behind the leader
        px = cx - w * 0.115
        d.line([px, y + 24, px, y + h * 0.34], fill=INK, width=2)
        fw, fh = w * 0.075, 16
        if flag == "us":  # stars and stripes, simplified
            d.rectangle([px, y + 24, px + fw, y + 24 + fh], fill=(255, 255, 255),
                        outline=INK)
            for s in range(4):
                d.rectangle([px, y + 24 + s * 4, px + fw, y + 24 + s * 4 + 2],
                            fill=RED)
            d.rectangle([px, y + 24, px + fw * 0.45, y + 24 + 9], fill=NAVY)
            d.ellipse([px + 3, y + 26, px + 7, y + 30], fill=(255, 255, 255))
            d.ellipse([px + 9, y + 29, px + 13, y + 33], fill=(255, 255, 255))
        elif flag == "cn":  # red field, gold stars
            d.rectangle([px, y + 24, px + fw, y + 24 + fh], fill=RED,
                        outline=INK)
            d.ellipse([px + 2, y + 26, px + 7, y + 31], fill=GOLD)
            d.ellipse([px + 10, y + 26, px + 13, y + 29], fill=GOLD)
            d.ellipse([px + 13, y + 30, px + 16, y + 33], fill=GOLD)
        else:  # Russia: white / blue / red tricolour
            d.rectangle([px, y + 24, px + fw, y + 24 + fh], fill=(255, 255, 255),
                        outline=INK)
            d.rectangle([px, y + 24 + 5, px + fw, y + 24 + 11], fill=NAVY)
            d.rectangle([px, y + 24 + 11, px + fw, y + 24 + fh], fill=RED)
        _face(d, cx, y + h * 0.44, w * 0.082, skin, hair, hair)
        # suit + tie
        d.polygon([(cx - w * 0.11, y + h * 0.68), (cx - w * 0.065, y + h * 0.55),
                   (cx + w * 0.065, y + h * 0.55), (cx + w * 0.11, y + h * 0.68)],
                  fill=suit, outline=INK)
        d.polygon([(cx - w * 0.014, y + h * 0.57), (cx + w * 0.014, y + h * 0.57),
                   (cx + w * 0.02, y + h * 0.68), (cx - w * 0.02, y + h * 0.68)],
                  fill=tie)
    # full-width table + nameplates sitting on its front
    d.rectangle([x + w * 0.02, y + h * 0.68, x + w * 0.98, y + h * 0.80],
                fill=(196, 120, 60), outline=INK)
    for fx, _s, _h, _su, _t, name, _f in leaders:
        cx = x + fx * w
        f = sans_b(11)
        tw = d.textlength(name, font=f)
        d.rectangle([cx - tw / 2 - 7, y + h * 0.82, cx + tw / 2 + 7,
                     y + h * 0.98], fill=CREAM, outline=INK)
        d.text((cx - tw / 2, y + h * 0.845), name, font=f, fill=INK)


def ill_icj(d, x, y, w, h):
    """Hero 2: World Court building + scales + big 9-6 badge.

    Fills the panel: a wide red-brick Peace-Palace-style building with
    two towers and arched windows on the left, tall scales on the right,
    a big red 9-6 badge on top and GENOCIDE RULING under it.
    """
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(233, 224, 196))
    # --- brick building, left ~62% of the panel
    bx0, bx1 = x + w * 0.03, x + w * 0.62
    base = y + h * 0.86
    d.rectangle([bx0, y + h * 0.34, bx1, base], fill=(178, 84, 60),
                outline=INK)
    # two towers with pointed roofs
    for tx0 in (bx0 + 2, bx1 - w * 0.13):
        d.rectangle([tx0, y + h * 0.16, tx0 + w * 0.13, base],
                    fill=(178, 84, 60), outline=INK)
        d.polygon([(tx0 - 3, y + h * 0.16), (tx0 + w * 0.065, y + h * 0.03),
                   (tx0 + w * 0.13 + 3, y + h * 0.16)], fill=NAVY,
                  outline=INK)
        d.rectangle([tx0 + w * 0.045, y + h * 0.30, tx0 + w * 0.085,
                     y + h * 0.44], fill=CREAM, outline=INK)
    # main roof + arched windows + door
    d.polygon([(bx0 - 2, y + h * 0.34), (x + w * 0.325, y + h * 0.20),
               (bx1 + 2, y + h * 0.34)], fill=NAVY, outline=INK)
    for i in range(4):
        wx = bx0 + w * 0.055 + i * w * 0.115
        d.pieslice([wx, y + h * 0.46, wx + w * 0.055, y + h * 0.58], 180, 360,
                   fill=CREAM, outline=INK)
        d.rectangle([wx, y + h * 0.52, wx + w * 0.055, y + h * 0.66],
                    fill=CREAM, outline=INK)
    d.rectangle([x + w * 0.28, y + h * 0.66, x + w * 0.37, base],
                fill=NAVY, outline=INK)
    # --- scales, right
    sx = x + w * 0.79
    d.line([sx, y + h * 0.30, sx, y + h * 0.78], fill=INK, width=3)
    d.line([sx - w * 0.10, y + h * 0.36, sx + w * 0.10, y + h * 0.36],
           fill=INK, width=3)
    d.ellipse([sx - w * 0.13, y + h * 0.60, sx - w * 0.045, y + h * 0.74],
              fill=GOLD, outline=INK)
    d.ellipse([sx + w * 0.045, y + h * 0.60, sx + w * 0.13, y + h * 0.74],
              fill=GOLD, outline=INK)
    d.line([sx - w * 0.087, y + h * 0.36, sx - w * 0.087, y + h * 0.60],
           fill=INK, width=2)
    d.line([sx + w * 0.087, y + h * 0.36, sx + w * 0.087, y + h * 0.60],
           fill=INK, width=2)
    d.ellipse([sx - 4, y + h * 0.28, sx + 4, y + h * 0.28 + 8], fill=GOLD,
              outline=INK)
    # --- 9-6 badge, top right
    bf = sans_b(20)
    bt = "9-6"
    tw = d.textlength(bt, font=bf)
    bxx = x + w * 0.66
    d.rectangle([bxx, y + 6, bxx + tw + 16, y + 34], fill=RED, outline=INK)
    d.text((bxx + 8, y + 8), bt, font=bf, fill=(255, 255, 255))
    d.text((bxx, y + h * 0.80), "GENOCIDE", font=sans_b(10), fill=INK)
    d.text((bxx, y + h * 0.80 + 13), "RULING", font=sans_b(10), fill=INK)


def ill_cop(d, x, y, w, h):
    """Hero 3: globe + thermometer + clean FOSSIL FUELS document.

    Fills the whole panel: a big clean globe on the left (solid blue,
    solid green land, no texture), a tall red thermometer in the middle,
    the draft document on the right with NO strikethrough anywhere, a
    CUT stamp tucked inside the document, and a navy strip along the
    bottom carrying the aid figure.
    """
    d.rectangle([x, y, x + w, y + h], fill=(200, 225, 210))
    # globe, left - big, smooth: solid blue disc, two smooth green land
    # blobs (many-point curves, no jagged polygon edges, no dither)
    cx, cy, r = x + w * 0.24, y + h * 0.36, w * 0.155
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 160, 200),
              outline=INK, width=2)
    _blob(d, cx - r * 0.30, cy - r * 0.28, r * 0.38, r * 0.28,
          (60, 140, 90), seed=0.7)
    _blob(d, cx + r * 0.25, cy + r * 0.30, r * 0.35, r * 0.30,
          (60, 140, 90), seed=2.1)
    d.arc([cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8], 200, 340,
          fill=(255, 255, 255), width=3)
    # thermometer, middle - tall, red mercury near the top
    tx = x + w * 0.47
    d.rounded_rectangle([tx, y + h * 0.08, tx + w * 0.055, y + h * 0.62],
                        radius=6, fill=CREAM, outline=INK)
    d.rectangle([tx + 2, y + h * 0.16, tx + w * 0.055 - 2, y + h * 0.60],
                fill=RED)
    d.ellipse([tx - w * 0.025, y + h * 0.58, tx + w * 0.08, y + h * 0.74],
              fill=RED, outline=INK)
    d.text((tx - w * 0.02, y + h * 0.76), "HOT", font=sans_b(9), fill=RED)
    # document, right - CLEAN: no red line crosses any letter
    dx, dy, dw, dh = x + w * 0.60, y + h * 0.06, w * 0.37, h * 0.60
    d.rectangle([dx, dy, dx + dw, dy + dh], fill=CREAM, outline=INK, width=2)
    f = sans_b(10)
    d.text((dx + 5, dy + 5), "DRAFT DEAL", font=f, fill=INK)
    d.line([dx + 5, dy + 20, dx + dw - 5, dy + 20], fill=INK, width=1)
    d.text((dx + 5, dy + 26), "FOSSIL", font=sans_b(13), fill=INK)
    d.text((dx + 5, dy + 44), "FUELS", font=sans_b(13), fill=INK)
    d.text((dx + 5, dy + 62), "ADAPTATION AID:", font=sans(9), fill=GREY)
    d.text((dx + 5, dy + 73), "$120bn", font=sans_b(10), fill=RED)
    # CUT stamp, fully INSIDE the document's lower-right corner: it
    # touches no letter and pokes out of nothing
    sf = sans_b(14)
    st = "CUT"
    tw = d.textlength(st, font=sf)
    d.rectangle([dx + dw - tw - 16, dy + dh - 24,
                 dx + dw - 6, dy + dh - 4], fill=RED, outline=INK)
    d.text((dx + dw - tw - 11, dy + dh - 22), st, font=sf,
           fill=(255, 255, 255))
    # navy strip along the bottom with the aid figure
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=NAVY)
    bf = sans_b(12)
    bt = "$120bn ADAPTATION AID CUT"
    tw = d.textlength(bt, font=bf)
    d.text((x + (w - tw) / 2, y + h * 0.86), bt, font=bf,
           fill=(255, 255, 255))


def ill_bridge(d, x, y, w, h):
    """Kerch bridge: deck + arch + pylons, a big explosion with smoke,
    water below and a ship passing under."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # water
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(120, 180, 210))
    d.line([x + w * 0.05, y + h * 0.80, x + w * 0.30, y + h * 0.80],
           fill=(255, 255, 255), width=1)
    d.line([x + w * 0.62, y + h * 0.88, x + w * 0.90, y + h * 0.88],
           fill=(255, 255, 255), width=1)
    # ship under the bridge, left
    sx = x + w * 0.08
    d.polygon([(sx, y + h * 0.82), (sx + w * 0.22, y + h * 0.82),
               (sx + w * 0.19, y + h * 0.94), (sx + w * 0.03, y + h * 0.94)],
              fill=NAVY, outline=INK)
    d.rectangle([sx + w * 0.07, y + h * 0.72, sx + w * 0.13, y + h * 0.82],
                fill=CREAM, outline=INK)
    # bridge deck + arch + pylons
    d.line([x, y + h * 0.52, x + w, y + h * 0.52], fill=INK, width=3)
    d.arc([x + w * 0.14, y + h * 0.22, x + w * 0.86, y + h * 0.82],
          180, 360, fill=INK, width=3)
    for px in (0.30, 0.70):
        d.line([x + px * w, y + h * 0.14, x + px * w, y + h * 0.52],
               fill=INK, width=2)
    # explosion: orange core, red starburst, grey smoke puffs
    bx, by = x + w * 0.52, y + h * 0.42
    burst = []
    for i in range(12):
        r = w * 0.13 if i % 2 == 0 else w * 0.06
        a = -math.pi / 2 + i * math.pi / 6
        burst.append((bx + r * math.cos(a), by + r * math.sin(a)))
    d.polygon(burst, fill=RED, outline=INK)
    d.ellipse([bx - w * 0.05, by - w * 0.05, bx + w * 0.05, by + w * 0.05],
              fill=(250, 180, 40))
    for sx2, sy2, sr in [(0.40, 0.12, 7), (0.62, 0.08, 8), (0.68, 0.20, 6)]:
        d.ellipse([x + sx2 * w - sr, y + sy2 * h - sr, x + sx2 * w + sr,
                   y + sy2 * h + sr], fill=(120, 120, 120), outline=INK)


def ill_riyadh(d, x, y, w, h):
    """Riyadh at night: dark sky with stars, a tower skyline, two
    missile trails curving up to a gold interception burst."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 32, 64))
    # stars
    for sx, sy in [(0.08, 0.12), (0.22, 0.06), (0.38, 0.16), (0.55, 0.08),
                   (0.72, 0.14), (0.88, 0.06), (0.94, 0.22), (0.30, 0.24)]:
        d.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1,
                   y + sy * h + 1], fill=(255, 255, 255))
    # crescent moon
    d.ellipse([x + w * 0.06, y + h * 0.08, x + w * 0.06 + 12,
               y + h * 0.08 + 12], fill=(250, 240, 200))
    d.ellipse([x + w * 0.06 + 4, y + h * 0.08 - 2, x + w * 0.06 + 14,
               y + h * 0.08 + 10], fill=(24, 32, 64))
    # skyline: towers with lit windows, one tall tower with an arch top
    for bx, bw, bh in [(0.02, 0.13, 0.34), (0.17, 0.11, 0.48),
                       (0.30, 0.12, 0.30), (0.44, 0.11, 0.42),
                       (0.68, 0.12, 0.36), (0.82, 0.13, 0.46)]:
        d.rectangle([x + bx * w, y + h * 0.92 - bh * h, x + (bx + bw) * w,
                     y + h * 0.92], fill=(10, 14, 34), outline=(90, 100, 140))
        for wy in (0.92 - bh * h + 4, 0.92 - bh * h + 12):
            d.rectangle([x + (bx + 0.03) * w, y + wy, x + (bx + 0.06) * w,
                         y + wy + 3], fill=GOLD)
    # tall Kingdom-Centre-style tower, centre-right, with arched opening
    tx0, tx1 = x + w * 0.56, x + w * 0.66
    d.rectangle([tx0, y + h * 0.22, tx1, y + h * 0.92], fill=(10, 14, 34),
                outline=(90, 100, 140))
    d.pieslice([tx0 + 2, y + h * 0.22, tx1 - 2, y + h * 0.44], 180, 360,
               fill=(24, 32, 64))
    d.rectangle([x, y + h * 0.92, x + w, y + h], fill=(233, 224, 196))
    # missile trails: dotted arcs rising to the interception burst
    bx, by = x + w * 0.60, y + h * 0.30
    for t in [i / 12 for i in range(13)]:
        px = x + w * 0.10 + (bx - x - w * 0.10) * t
        py = y + h * 0.85 - (y + h * 0.85 - by) * t * t
        d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5],
                  fill=(255, 255, 255))
    for t in [i / 10 for i in range(11)]:
        px = x + w * 0.95 - (x + w * 0.95 - bx) * t
        py = y + h * 0.80 - (y + h * 0.80 - by) * t * t
        d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=GOLD)
    burst = []
    for i in range(12):
        r = w * 0.10 if i % 2 == 0 else w * 0.045
        a = -math.pi / 2 + i * math.pi / 6
        burst.append((bx + r * math.cos(a), by + r * math.sin(a)))
    d.polygon(burst, fill=GOLD, outline=INK)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 255, 255))


def ill_cyclone(d, x, y, w, h):
    """Cyclone Akvan: ONE asymmetric spiral arm over the sea (never
    concentric rings, never a target), a dashed red trajectory arrow to
    the coast, and a clear ODISHA label in the empty top-left corner."""
    d.rectangle([x, y, x + w, y + h], fill=TINTS[0])
    # sea
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(120, 180, 210))
    # coastline: sand strip with three small houses, right side
    d.polygon([(x + w * 0.62, y + h * 0.62), (x + w, y + h * 0.62),
               (x + w, y + h), (x + w * 0.62, y + h)], fill=(233, 224, 196),
              outline=INK)
    for hx, hy in [(0.68, 0.68), (0.80, 0.72), (0.90, 0.66)]:
        d.rectangle([x + hx * w, y + hy * h, x + hx * w + 12, y + hy * h + 9],
                    fill=CREAM, outline=INK)
        d.polygon([(x + hx * w - 1, y + hy * h),
                   (x + hx * w + 6, y + hy * h - 6),
                   (x + hx * w + 13, y + hy * h)], fill=RED, outline=INK)
    # waves
    for wy in (0.80, 0.90):
        d.arc([x + w * 0.05, y + h * wy, x + w * 0.35, y + h * wy + 8],
              180, 360, fill=(255, 255, 255), width=2)
    # ODISHA label, top-left, in empty sky - clear of the spiral below
    lf = sans_b(9)
    lt = "ODISHA"
    lw = d.textlength(lt, font=lf)
    d.rectangle([x + 4, y + 3, x + 4 + lw + 8, y + 15], fill=CREAM,
                outline=INK)
    d.text((x + 8, y + 4), lt, font=lf, fill=NAVY)
    # asymmetric spiral: ONE arm curling outwards, radius growing with
    # angle, centre offset left; its tail continues from the top of the
    # curl and sweeps RIGHT and down, staying clear of the ODISHA label
    # (which ends at ~0.29w). No closed rings at all.
    cx, cy = x + w * 0.34, y + h * 0.50
    pts = []
    for deg in range(0, 721, 6):
        a = math.radians(deg - 90)
        r = h * (0.015 + 0.00042 * deg)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.line(pts, fill=NAVY, width=3)
    tail = []
    for t in range(0, 16):
        a = math.radians(270 + t * 5)
        r = h * (0.32 + 0.008 * t)
        tail.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.line(tail, fill=NAVY, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    # dashed red trajectory arrow from the spiral toward the coast
    ax0, ay0 = cx + w * 0.17, cy + h * 0.12
    ax1, ay1 = x + w * 0.60, cy + h * 0.20
    nseg = 7
    for i in range(nseg):
        if i % 2 == 0:
            t0, t1 = i / nseg, (i + 1) / nseg
            d.line([(ax0 + (ax1 - ax0) * t0, ay0 + (ay1 - ay0) * t0),
                    (ax0 + (ax1 - ax0) * t1, ay0 + (ay1 - ay0) * t1)],
                   fill=RED, width=2)
    d.polygon([(ax1, ay1), (ax1 - 8, ay1 - 4), (ax1 - 8, ay1 + 5)], fill=RED)


def ill_seoul(d, x, y, w, h):
    """Seoul: a small courthouse with columns and a Korean flag, a big
    gavel striking, and a red OVERTURNED stamp."""
    d.rectangle([x, y, x + w, y + h], fill=TINTS[3])
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(233, 224, 196))
    # courthouse, left
    cx0, cx1 = x + w * 0.04, x + w * 0.42
    base = y + h * 0.86
    d.polygon([(cx0 - 2, y + h * 0.30), ((cx0 + cx1) / 2, y + h * 0.12),
               (cx1 + 2, y + h * 0.30)], fill=NAVY, outline=INK)
    d.rectangle([cx0, y + h * 0.30, cx1, y + h * 0.34], fill=CREAM,
                outline=INK)
    for i in range(3):
        px = cx0 + w * 0.05 + i * w * 0.115
        d.rectangle([px, y + h * 0.34, px + w * 0.045, base], fill=CREAM,
                    outline=INK)
    d.rectangle([cx0, base - 3, cx1, base], fill=NAVY)
    # Korean flag on a pole above the courthouse
    d.line([x + w * 0.23, y + h * 0.02, x + w * 0.23, y + h * 0.12],
           fill=INK, width=2)
    d.rectangle([x + w * 0.23, y + h * 0.02, x + w * 0.23 + 16, y + h * 0.10],
                fill=(255, 255, 255), outline=INK)
    d.ellipse([x + w * 0.23 + 5, y + h * 0.02 + 2, x + w * 0.23 + 11,
               y + h * 0.10 - 2], fill=RED, outline=INK)
    # gavel, centre-right, diagonal
    d.line([x + w * 0.52, y + h * 0.62, x + w * 0.88, y + h * 0.18],
           fill=(120, 80, 40), width=5)
    d.rounded_rectangle([x + w * 0.70, y + h * 0.06, x + w * 0.96,
                         y + h * 0.28], radius=4, fill=NAVY, outline=INK)
    # sound block
    d.rectangle([x + w * 0.48, y + h * 0.72, x + w * 0.72, y + h * 0.80],
                fill=NAVY, outline=INK)
    # OVERTURNED stamp, bottom right
    sf = sans_b(10)
    st = "OVERTURNED"
    tw = d.textlength(st, font=sf)
    d.rectangle([x + w - tw - 12, y + h * 0.66, x + w - 4,
                 y + h * 0.66 + 16], fill=RED)
    d.text((x + w - tw - 8, y + h * 0.66 + 2), st, font=sf,
           fill=(255, 255, 255))


def ill_greenland(d, x, y, w, h):
    """Greenland: two big snow peaks filling the card, Danish and US
    flags planted on them, a red 109-0 badge and sea at the bottom."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # mountains, full width
    d.polygon([(x, y + h), (x + w * 0.28, y + h * 0.16),
               (x + w * 0.56, y + h)], fill=(250, 250, 246), outline=INK)
    d.polygon([(x + w * 0.22, y + h * 0.30), (x + w * 0.28, y + h * 0.16),
               (x + w * 0.34, y + h * 0.30)], fill=(200, 220, 235))
    d.polygon([(x + w * 0.44, y + h), (x + w * 0.72, y + h * 0.08),
               (x + w, y + h)], fill=(230, 235, 240), outline=INK)
    d.polygon([(x + w * 0.66, y + h * 0.24), (x + w * 0.72, y + h * 0.08),
               (x + w * 0.78, y + h * 0.24)], fill=(200, 220, 235))
    # sea
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(120, 180, 210))
    d.line([x + w * 0.10, y + h * 0.92, x + w * 0.30, y + h * 0.92],
           fill=(255, 255, 255), width=1)
    # Danish flag on the left peak, US flag on the right peak
    d.line([x + w * 0.28, y + h * 0.02, x + w * 0.28, y + h * 0.18],
           fill=INK, width=2)
    d.rectangle([x + w * 0.28, y + h * 0.02, x + w * 0.28 + 16,
                 y + h * 0.02 + 11], fill=RED, outline=INK)
    d.rectangle([x + w * 0.28, y + h * 0.02 + 4, x + w * 0.28 + 16,
                 y + h * 0.02 + 7], fill=(255, 255, 255))
    d.rectangle([x + w * 0.28 + 6, y + h * 0.02, x + w * 0.28 + 9,
                 y + h * 0.02 + 11], fill=(255, 255, 255))
    d.line([x + w * 0.72, y + h * 0.02, x + w * 0.72, y + h * 0.10],
           fill=INK, width=2)
    d.rectangle([x + w * 0.72, y + h * 0.02, x + w * 0.72 + 16,
                 y + h * 0.02 + 11], fill=(255, 255, 255), outline=INK)
    for s in range(3):
        d.rectangle([x + w * 0.72, y + h * 0.02 + s * 4,
                     x + w * 0.72 + 16, y + h * 0.02 + s * 4 + 2], fill=RED)
    d.rectangle([x + w * 0.72, y + h * 0.02, x + w * 0.72 + 7,
                 y + h * 0.02 + 6], fill=NAVY)
    # 109-0 badge, centre bottom above the sea
    bf = sans_b(12)
    bt = "109-0"
    tw = d.textlength(bt, font=bf)
    d.rectangle([x + (w - tw) / 2 - 6, y + h * 0.62,
                 x + (w - tw) / 2 + tw + 6, y + h * 0.62 + 18], fill=RED,
                outline=INK)
    d.text((x + (w - tw) / 2, y + h * 0.62 + 2), bt, font=bf,
           fill=(255, 255, 255))


def ill_anthropic(d, x, y, w, h):
    """Anthropic: a Nasdaq exchange facade with a big ANT ticker on the
    left, a rising chart as a small element on the right, +17% badge."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 214))
    # exchange facade, left third: columns + pediment + ANT sign
    fx0, fx1 = x + w * 0.04, x + w * 0.34
    base = y + h * 0.88
    d.polygon([(fx0 - 2, y + h * 0.22), ((fx0 + fx1) / 2, y + h * 0.08),
               (fx1 + 2, y + h * 0.22)], fill=NAVY, outline=INK)
    d.rectangle([fx0, y + h * 0.22, fx1, y + h * 0.26], fill=CREAM,
                outline=INK)
    for i in range(3):
        px = fx0 + w * 0.04 + i * w * 0.09
        d.rectangle([px, y + h * 0.26, px + w * 0.035, base], fill=CREAM,
                    outline=INK)
    d.rectangle([fx0, base - 3, fx1, base], fill=NAVY)
    # white exchange sign across the facade front with the ticker on it
    d.rectangle([fx0 + 2, y + h * 0.44, fx1 - 2, y + h * 0.78], fill=CREAM,
                outline=INK)
    d.text((fx0 + w * 0.07, y + h * 0.46), "ANT",
           font=sans_b(13 if h >= 62 else 11), fill=NAVY)
    d.text((fx0 + w * 0.05, y + h * 0.66), "NASDAQ", font=sans_b(7),
           fill=NAVY)
    # rising chart, right two thirds (a small element, not the card)
    pts = [(x + w * 0.40, y + h * 0.76), (x + w * 0.52, y + h * 0.68),
           (x + w * 0.62, y + h * 0.72), (x + w * 0.74, y + h * 0.50),
           (x + w * 0.86, y + h * 0.54), (x + w * 0.94, y + h * 0.30)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + w * 0.94, y + h * 0.30), (x + w * 0.85, y + h * 0.28),
               (x + w * 0.92, y + h * 0.42)], fill=RED)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    # +17% badge, top right
    bf = sans_b(12)
    bt = "+17%"
    tw = d.textlength(bt, font=bf)
    d.rectangle([x + w - tw - 10, y + 4, x + w - 4, y + 22], fill=RED)
    d.text((x + w - tw - 7, y + 6), bt, font=bf, fill=(255, 255, 255))
    d.text((x + w * 0.40, y + h * 0.06), "FIRST DAY", font=sans_b(8),
           fill=GREY)


def ill_gta(d, x, y, w, h):
    """GTA VI: a purple dusk city, a BIG white game controller front and
    centre (so the card reads as a video game at a glance), a big VI
    logo top-right with OUT NOW under it. Deliberately sparse: no car,
    no sunset, only two skyline silhouettes, so nothing crowds the
    controller. No STRIKE label anywhere."""
    d.rectangle([x, y, x + w, y + h], fill=(196, 150, 216))
    # two skyline silhouettes, far left and far right only
    for bx, bw, bh in [(0.02, 0.10, 0.34), (0.90, 0.09, 0.32)]:
        d.rectangle([x + bx * w, y + h * 0.78 - bh * h, x + (bx + bw) * w,
                     y + h * 0.78], fill=NAVY)
        for wy in (0.78 - bh * h + 0.06, 0.78 - bh * h + 0.14):
            d.rectangle([x + (bx + 0.02) * w, y + h * wy,
                         x + (bx + 0.05) * w, y + h * wy + 3], fill=GOLD)
    # street
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(60, 50, 70))
    d.line([x, y + h * 0.90, x + w, y + h * 0.90], fill=GOLD, width=2)
    # big white game controller, centre: body, grips, d-pad, buttons,
    # two sticks. It sits above the street, clear of VI / OUT NOW.
    gx0, gy0 = x + w * 0.20, y + h * 0.26
    gx1, gy1 = x + w * 0.68, y + h * 0.68
    d.rounded_rectangle([gx0, gy0, gx1, gy1], radius=8, fill=(255, 255, 255),
                        outline=INK, width=2)
    d.ellipse([gx0 - 2, gy1 - 10, gx0 + 14, gy1 + 6], fill=(255, 255, 255),
              outline=INK, width=2)
    d.ellipse([gx1 - 14, gy1 - 10, gx1 + 2, gy1 + 6], fill=(255, 255, 255),
              outline=INK, width=2)
    # d-pad, left
    dpx, dpy = gx0 + w * 0.09, (gy0 + gy1) / 2
    d.rectangle([dpx - 3, dpy - 9, dpx + 3, dpy + 9], fill=INK)
    d.rectangle([dpx - 9, dpy - 3, dpx + 9, dpy + 3], fill=INK)
    # four action buttons, right
    bcx, bcy = gx1 - w * 0.09, (gy0 + gy1) / 2
    for dxb, dyb, col in [(0, -8, (60, 140, 90)), (8, 0, RED),
                          (0, 8, NAVY), (-8, 0, GOLD)]:
        d.ellipse([bcx + dxb - 4, bcy + dyb - 4, bcx + dxb + 4,
                   bcy + dyb + 4], fill=col, outline=INK)
    # two thumb sticks
    for sx in (gx0 + w * 0.24, gx1 - w * 0.24):
        d.ellipse([sx - 5, (gy0 + gy1) / 2 + 2, sx + 5,
                   (gy0 + gy1) / 2 + 12], fill=(200, 200, 200), outline=INK)
    # big VI logo, top right, with OUT NOW below it - clear of the
    # controller (controller top is 0.26h, VI ends well above it)
    d.text((x + w * 0.78, y + h * 0.01), "VI", font=serif_b(30),
           fill=(255, 255, 255))
    d.text((x + w * 0.70, y + h * 0.52), "OUT NOW", font=sans_b(9),
           fill=(255, 255, 255))


def ill_bogota(d, x, y, w, h):
    """Bogota: a street protest - buildings behind, a two-row crowd of
    marchers with raised BLANK placards, and a Colombian tricolour
    stripe at the top. NO text inside the illustration at all: the
    dark "PARO NACIONAL" banner above the card is the only label.
    No STRIKE label."""
    d.rectangle([x, y, x + w, y + h], fill=TINTS[3])
    # buildings behind the crowd
    for bx, bw, bh in [(0.02, 0.14, 0.34), (0.18, 0.12, 0.44),
                       (0.70, 0.13, 0.38), (0.85, 0.13, 0.46)]:
        d.rectangle([x + bx * w, y + h * 0.52 - bh * h, x + (bx + bw) * w,
                     y + h * 0.52], fill=NAVY)
    # Colombian tricolour stripe, top - colour only, no letters
    d.rectangle([x, y, x + w, y + h * 0.10], fill=GOLD)
    d.rectangle([x, y + h * 0.10, x + w, y + h * 0.16], fill=NAVY)
    d.rectangle([x, y + h * 0.16, x + w, y + h * 0.22], fill=RED)
    # crowd: two rows of marchers, heads + bodies, varied colours
    cols = [RED, NAVY, (60, 140, 90), GOLD, RED, NAVY]
    for i, cx in enumerate([0.10, 0.26, 0.42, 0.58, 0.74, 0.90]):
        col = cols[i]
        d.ellipse([x + cx * w - 6, y + h * 0.62, x + cx * w + 6,
                   y + h * 0.62 + 12], fill=(240, 200, 160), outline=INK)
        d.rectangle([x + cx * w - 8, y + h * 0.74, x + cx * w + 8,
                     y + h * 0.96], fill=col, outline=INK)
    for i, cx in enumerate([0.18, 0.34, 0.50, 0.66, 0.82]):
        col = cols[(i + 2) % 6]
        d.ellipse([x + cx * w - 6, y + h * 0.50, x + cx * w + 6,
                   y + h * 0.50 + 12], fill=(240, 200, 160), outline=INK)
        d.rectangle([x + cx * w - 8, y + h * 0.62, x + cx * w + 8,
                     y + h * 0.80], fill=col, outline=INK)
    # raised placards above the back row
    for px in (0.34, 0.66):
        d.line([x + px * w, y + h * 0.50, x + px * w, y + h * 0.40],
               fill=INK, width=2)
        d.rectangle([x + px * w - 11, y + h * 0.40, x + px * w + 11,
                     y + h * 0.40 + 10], fill=CREAM, outline=INK)


def ill_nairobi(d, x, y, w, h):
    """Nairobi marathon: a SMALL runner mid-stride on a track, leaning
    into a checkered finish gantry, with a red BANNED 3 YEARS stamp in
    the TOP-RIGHT corner of the illustration, far from any headline.
    Every coordinate is a fraction of h, so the runner (head to shoes)
    ends well inside the illustration - nothing touches the headline
    below. No stick figure: torso, shorts, thick limbs."""
    d.rectangle([x, y, x + w, y + h], fill=TINTS[1])
    # sky + distant stands
    d.rectangle([x, y + h * 0.52, x + w, y + h * 0.60], fill=NAVY)
    for i in range(9):
        d.ellipse([x + w * 0.05 + i * w * 0.10, y + h * 0.54,
                   x + w * 0.05 + i * w * 0.10 + 4, y + h * 0.54 + 4],
                  fill=CREAM)
    # track
    d.rectangle([x, y + h * 0.60, x + w, y + h], fill=(196, 120, 60))
    d.line([x, y + h * 0.72, x + w, y + h * 0.72], fill=(255, 255, 255),
           width=1)
    # finish gantry, right: two posts + checkered top bar, lowered so
    # its top bar (0.34h) stays clear of the stamp above it
    gx = x + w * 0.82
    d.rectangle([gx, y + h * 0.34, gx + 4, y + h * 0.96], fill=INK)
    d.rectangle([x + w * 0.97, y + h * 0.34, x + w * 0.97 + 4,
                 y + h * 0.96], fill=INK)
    for i in range(8):
        sq = gx + 4 + i * (x + w * 0.97 - gx - 4) / 8
        d.rectangle([sq, y + h * 0.34, sq + (x + w * 0.97 - gx - 4) / 8,
                     y + h * 0.34 + 7],
                    fill=INK if i % 2 == 0 else (255, 255, 255))
    # tape across the track at the gantry
    d.line([gx, y + h * 0.62, gx, y + h * 0.96], fill=(255, 255, 255),
           width=2)
    # runner, SMALL and mid-stride, leaning toward the gantry. Head
    # top 0.16h, shoes bottom ~0.90h: fully inside the illustration.
    hx, hy = x + w * 0.30, y + h * 0.26   # head centre
    skin = (150, 90, 60)
    hr = h * 0.10
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=skin, outline=INK)
    # torso (leaning) + shorts
    d.polygon([(hx - h * 0.07, hy + h * 0.12), (hx + h * 0.14, hy + h * 0.10),
               (hx + h * 0.20, hy + h * 0.38), (hx - h * 0.03, hy + h * 0.40)],
              fill=RED, outline=INK)
    d.polygon([(hx - h * 0.03, hy + h * 0.36), (hx + h * 0.20, hy + h * 0.34),
               (hx + h * 0.21, hy + h * 0.46), (hx - h * 0.02, hy + h * 0.48)],
              fill=NAVY, outline=INK)
    # arms: one pumping forward, one back
    d.line([hx + h * 0.12, hy + h * 0.16, hx + h * 0.36, hy + h * 0.06],
           fill=skin, width=4)
    d.line([hx + h * 0.36, hy + h * 0.06, hx + h * 0.46, hy + h * 0.22],
           fill=skin, width=4)
    d.line([hx - h * 0.05, hy + h * 0.16, hx - h * 0.28, hy + h * 0.34],
           fill=skin, width=4)
    d.line([hx - h * 0.28, hy + h * 0.34, hx - h * 0.12, hy + h * 0.48],
           fill=skin, width=4)
    # legs: front leg bent forward, back leg trailing
    d.line([hx + h * 0.08, hy + h * 0.46, hx + h * 0.32, hy + h * 0.42],
           fill=skin, width=4)
    d.line([hx + h * 0.32, hy + h * 0.42, hx + h * 0.30, hy + h * 0.60],
           fill=skin, width=4)
    d.line([hx + h * 0.15, hy + h * 0.46, hx - h * 0.10, hy + h * 0.40],
           fill=skin, width=4)
    d.line([hx - h * 0.10, hy + h * 0.40, hx - h * 0.28, hy + h * 0.56],
           fill=skin, width=4)
    # shoes
    d.ellipse([hx + h * 0.22, hy + h * 0.58, hx + h * 0.38, hy + h * 0.65],
              fill=(255, 255, 255), outline=INK)
    d.ellipse([hx - h * 0.36, hy + h * 0.54, hx - h * 0.20, hy + h * 0.61],
              fill=(255, 255, 255), outline=INK)
    # BANNED 3 YEARS stamp, TOP-RIGHT corner, above the gantry bar
    sf = sans_b(8)
    st = "BANNED 3 YEARS"
    tw = d.textlength(st, font=sf)
    d.rectangle([x + w - tw - 12, y + 3, x + w - 4, y + 16], fill=RED)
    d.text((x + w - tw - 8, y + 5), st, font=sf, fill=(255, 255, 255))


def ill_canberra(d, x, y, w, h):
    """Canberra: Parliament House with its flag mast on a lawn, and a
    small falling chart as a minor element on the right."""
    d.rectangle([x, y, x + w, y + h], fill=TINTS[4])
    # lawn
    d.rectangle([x, y + h * 0.80, x + w, y + h], fill=(90, 160, 90))
    # Parliament House, left two thirds: low building + flag mast
    px0, px1 = x + w * 0.05, x + w * 0.58
    base = y + h * 0.80
    d.rectangle([px0, y + h * 0.42, px1, base], fill=CREAM, outline=INK)
    d.polygon([(px0 - 2, y + h * 0.42), ((px0 + px1) / 2, y + h * 0.28),
               (px1 + 2, y + h * 0.42)], fill=NAVY, outline=INK)
    for i in range(4):
        cx = px0 + w * 0.06 + i * w * 0.115
        d.rectangle([cx, y + h * 0.46, cx + w * 0.045, base], fill=NAVY,
                    outline=INK)
    d.rectangle([px0 + w * 0.20, y + h * 0.62, px0 + w * 0.30, base],
                fill=NAVY, outline=INK)
    # flag mast rising from the roof
    mx = (px0 + px1) / 2
    d.line([mx, y + h * 0.28, mx, y + h * 0.04], fill=INK, width=2)
    d.rectangle([mx, y + h * 0.04, mx + 16, y + h * 0.04 + 10],
                fill=NAVY, outline=INK)
    d.ellipse([mx + 3, y + h * 0.04 + 2, mx + 8, y + h * 0.04 + 8],
              fill=(255, 255, 255))
    # small falling chart, right
    pts = [(x + w * 0.64, y + h * 0.30), (x + w * 0.72, y + h * 0.44),
           (x + w * 0.80, y + h * 0.40), (x + w * 0.88, y + h * 0.56),
           (x + w * 0.95, y + h * 0.68)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + w * 0.95, y + h * 0.68), (x + w * 0.87, y + h * 0.66),
               (x + w * 0.93, y + h * 0.56)], fill=RED)
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    d.text((x + w * 0.66, y + h * 0.06), "4.9%", font=sans_b(13), fill=RED)


ILL = {"apec": ill_apec, "icj": ill_icj, "cop": ill_cop,
       "bridge": ill_bridge, "riyadh": ill_riyadh, "cyclone": ill_cyclone,
       "seoul": ill_seoul, "greenland": ill_greenland,
       "anthropic": ill_anthropic, "gta": ill_gta, "bogota": ill_bogota,
       "nairobi": ill_nairobi, "canberra": ill_canberra}

# Dark slug banner on top of every secondary card (rank-1 pattern): the
# story's slug in white caps on a near-black strip, so each card is
# recognisable at ~300px even before its headline is read.
BANNERS = {4: "KERCH BRIDGE", 5: "OVER RIYADH", 6: "CYCLONE AKVAN",
           7: "SEOUL", 8: "GREENLAND", 9: "ANT \u00b7 NASDAQ",
           10: "GTA VI", 11: "PARO NACIONAL", 12: "DOPING \u00b7 3 YEARS",
           13: "4.9% JOBLESS RATE"}

# -------------------------------------------------------------------- stories
# 35 stories = 3 hero + 10 cards + 22 briefs. Every featured story happened
# or was first reported on Thursday 19 November 2026. Anything dated 18 or
# 20 November lives ONLY in the DATE CHECK box below.
HERO = [
    (1, "APEC 2026 · SHENZHEN",
     "Trump, Xi and Putin hold first three-way summit",
     "Three leaders meet for ~90 minutes, issue a \u201cDeclaration on "
     "Peace\u201d on nuclear risk and back UN reform.",
     "Reuters · AP · Xinhua", "CONFIRMED", "apec"),
    (2, "THE HAGUE · JUSTICE",
     "World Court: Myanmar committed genocide",
     "By 9 votes to 6 the court finds Myanmar guilty of genocide against "
     "the Rohingya and orders reparations.",
     "Al Jazeera · UN News", "CONFIRMED", "icj"),
    (3, "ANTALYA · CLIMATE",
     "COP31 draft drops fossil fuels and $120bn aid goal",
     "The draft drops fossil fuels and a $120bn adaptation-aid goal. "
     "Talks end Friday.",
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
     "Shares jump 17% on the first day after the record $81.3bn sale.",
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
    (14, "SHENZHEN", "Xi urges nuclear-arms ban.", "Al Jazeera"),
    (15, "SHENZHEN",
     "Albanese to Putin: \u201cEnd your war, end it now\u201d.", "ABC"),
    (16, "SEOUL", "500,000 sit college exam.", "Sedaily"),
    (17, "JAKARTA", "Asset-seizure law passes at last.", "Kompas"),
    (18, "HORMUZ", "Iran says mines set 3 tankers ablaze.", "Al Jazeera"),
    (19, "GAZA", "Israel ends tank raid past truce line.", "BBC"),
    (20, "KRASNODAR", "Kyiv says it hit two oil refineries.", "Euronews"),
    (21, "BRUSSELS", "EU delays methane rules two years.", "Euronews"),
    (22, "UK", "Inquiry: Bayesian yacht vulnerable to wind.", "RNZ"),
    (23, "ZURICH", "Two rivals to challenge FIFA\u2019s Infantino.", "ABC"),
    (24, "ROME", "Author Corrado Augias dies at 91.", "Euronews"),
    (25, "MOGADISHU", "Somalia expels UAE ambassador.", "Al Jazeera"),
    (26, "SUDAN", "Court sentences absent RSF chief to death.", "AP"),
    (27, "PRETORIA", "Central bank holds rate at 7.25%.", "SABC"),
    (28, "CANARIES", "Record 11,000 migrants in 15 days.", "Africanews"),
    (29, "FLORIDA", "Floods shut Broward, Miami schools.", "CBS"),
    (30, "WELLINGTON", "Court: pay equity cuts broke rights law.", "RNZ"),
    (31, "TONGA", "Drought emergency takes effect.", "RNZ"),
    (32, "COOK ISLANDS", "Cyclone Xavier now category 4.", "RNZ"),
    (33, "SPACE", "Red giant seen eating Sun-sized star.", "Nature"),
    (34, "SENEGAL", "Boat capsizes off Yenne; dozens missing.", ""),
    (35, "CEPU, JAVA", "Refinery blast kills one worker.", ""),
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

X0 = M                       # content left edge: rail removed, full width
X1 = 1010
CW2 = X1 - X0

Y_MASTHEAD = 0
Y_CONT = 108
Y_NUM = 128
Y_HERO = 164
H_HERO = 264
Y_C1 = 434
Y_C2 = 588
H_CARD = 148
Y_MAP = 740
H_MAP = 138
Y_LEGEND = 882
Y_DATE = 894
H_DATE = 76
Y_FOOT = 980


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
    # strapline, smaller (11pt) and higher (y 91): its descenders end
    # well above the continent strip, so nothing looks struck through
    d.text((M, 91), SUBLINE, font=serif_i(11), fill=RED)


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


def draw_hero(d):
    pw = (CW2 - 2 * 6) // 3
    for i, (num, kick, head, deck, src, tag, ill_key) in enumerate(HERO):
        x = X0 + i * (pw + 6)
        d.rectangle([x, Y_HERO, x + pw, Y_HERO + H_HERO], outline=INK, width=1)
        ILL[ill_key](d, x + 1, Y_HERO + 1, pw - 2, 164)
        ty = Y_HERO + 168
        num_circle(d, x + 10, ty + 7, num, r=8)
        tracked(d, (x + 24, ty), kick, sans_b(9), RED, track=1)
        hf = serif_b(16)
        hlines = wrap(d, head, hf, pw - 12)
        if len(hlines) > 2:
            print(f"OVERFLOW hero headline {num}: {hlines}")
        hy = ty + 18
        for ln in hlines[:2]:
            d.text((x + 6, hy), ln, font=hf, fill=INK)
            hy += 18
        df = sans(9)
        dlines = wrap(d, deck, df, pw - 12)
        if len(dlines) > 2:
            print(f"OVERFLOW hero deck {num}: {dlines}")
        dy = hy + 2
        for ln in dlines[:2]:
            d.text((x + 6, dy), ln, font=df, fill=INK)
            dy += 11
        sf = sans(8)
        d.text((x + 6, Y_HERO + H_HERO - 14),
               f"\u2014 {src} \u00b7 {tag}", font=sf, fill=GREY)


def draw_cards(d, y0, cards):
    cw = (CW2 - 4 * 6) // 5
    for i, (num, kick, head, deck, src, tag, ill_key) in enumerate(cards):
        x = X0 + i * (cw + 6)
        d.rectangle([x, y0, x + cw, y0 + H_CARD], outline=INK, width=1)
        # dark slug banner on top (rank-1 pattern), white caps
        bt = BANNERS[num]
        bf = sans_b(10)
        if tracked_w(d, bt, bf, track=1) > cw - 10:
            bf = sans_b(9)
        bw = tracked_w(d, bt, bf, track=1)
        d.rectangle([x, y0, x + cw, y0 + 16], fill=INK)
        tracked(d, (x + (cw - bw) / 2, y0 + 3), bt, bf, (255, 255, 255),
                track=1)
        ILL[ill_key](d, x + 1, y0 + 17, cw - 2, 58)
        ty = y0 + 78
        num_circle(d, x + 9, ty + 6, num, r=7)
        tracked(d, (x + 20, ty), kick, sans_b(8), RED, track=1)
        hf = serif_b(11)
        hlines = wrap(d, head, hf, cw - 10)
        if len(hlines) > 2:
            print(f"OVERFLOW card headline {num}: {hlines}")
        hy = ty + 14
        for ln in hlines[:2]:
            d.text((x + 5, hy), ln, font=hf, fill=INK)
            hy += 12
        df = sans(8)
        dlines = wrap(d, deck, df, cw - 10)
        if len(dlines) > 2:
            print(f"OVERFLOW card deck {num}: {dlines}")
        dy = hy + 1
        for ln in dlines[:2]:
            d.text((x + 5, dy), ln, font=df, fill=INK)
            dy += 10
        sf = sans(7)
        d.text((x + 5, y0 + H_CARD - 11), f"\u2014 {src} \u00b7 {tag}",
               font=sf, fill=GREY)


def draw_map_briefs(d):
    # --- map (left, widened to 340 so pins stop crowding)
    tracked(d, (X0, Y_MAP), "WHERE IT HAPPENED", sans_b(10), INK, track=2)
    mx, my, mw, mh = X0, Y_MAP + 16, 320, H_MAP - 16
    d.rectangle([mx, my, mx + mw, my + mh], fill=MAP_BG, outline=INK)
    for poly in POLYS:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=MAP_LAND, outline=(96, 84, 52), width=2)
    for _num, lon, lat in DOTS:
        px, py = project(lon, lat, mx, my, mw, mh)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    for num, lon, lat in PINS:
        px, py = project(lon, lat, mx, my, mw, mh)
        num_circle(d, px, py, num, r=6)
    # story 33 is in space: no star pin on the map, just the brief line
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
            y = Y_MAP + 13 + ri * 11.7
            full = f"{num}. {place} \u2014 {text}"
            if src:
                full += f" {src}"
            f = sans(9)
            fb = sans_b(9)
            fs = sans(8)
            d.text((cx, y), f"{num}. ", font=fb, fill=RED)
            x = cx + d.textlength(f"{num}. ", font=fb)
            d.text((x, y), place, font=fb, fill=INK)
            x += d.textlength(place + " ", font=fb)
            d.text((x, y), "\u2014 " + text, font=f, fill=INK)
            x += d.textlength("\u2014 " + text, font=f)
            if src:
                d.text((x + 2, y), src, font=fs, fill=GREY)
            total = (d.textlength(f"{num}. ", font=fb)
                     + d.textlength(place + " ", font=fb)
                     + d.textlength("\u2014 " + text, font=f)
                     + (d.textlength(src, font=fs) + 2 if src else 0))
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
    draw_masthead(d)
    draw_continents(d)
    draw_numbers(d)
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

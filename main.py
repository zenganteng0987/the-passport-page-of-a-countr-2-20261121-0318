#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Pure-stdlib Python: draws an open passport spread for the invented
atoll republic of Taluna and writes /output/entry.png (and ./entry.png
when run locally). No third-party imports, no network, no fonts read
from disk: all lettering comes from a 5x7 bitmap font embedded below,
and the PNG is encoded by hand (zlib + struct).
"""
import math
import os
import struct
import zlib

W, H = 1024, 724

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font. '#' = ink, '.' = blank. 7 rows of 5 columns each.
FONT = {
    'A': ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "'": ("..#..", "..#..", ".....", ".....", ".....", ".....", "....."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
}

# ------------------------------------------------------------- config -----
# CONFIG START
CFG = {
    "country": "REPUBLIC OF TALUNA",
    "doc_title": "PASSPORT",
    "emblem": "sun",
    "photo_left": True,
    "navy": (16, 38, 74),        # deep sea blue
    "gold": (176, 141, 63),
    "paper": (246, 239, 220),    # cream paper
    "ink": (22, 34, 56),
    "label": (96, 104, 122),
    "holder": {
        "code": "TLA",
        "short": "TALUNA",
        "surname": "MARAEA",
        "given": "LIORA SELENE",
        "nationality": "TALUNAN",
        "dob": "12 JUN 1994",
        "dob_mrz": "940612",
        "pob": "PORT LIORA",
        "sex": "F",
        "issue": "14 MAR 2019",
        "expiry": "14 MAR 2029",
        "expiry_mrz": "290314",
        "number": "TLA 041982",   # doc number in MRZ: TLA041982 (9 chars)
        "authority": "MINISTRY OF THE INTERIOR",
        "authority2": "PORT LIORA",
        "skin": (219, 168, 120),
        "skin_dark": (198, 145, 100),
        "hair": (36, 26, 22),
        "hair_style": "long",
        "lips": (163, 74, 74),
        "jacket": (49, 64, 90),
        "necklace": True,
        "beard": False,
    },
    # stamps: kind oval/rect, ink colour, country, action, date, centre, size, rotation
    "stamps": [
        {"kind": "oval", "color": (28, 84, 160), "country": "KESTREL ISLANDS",
         "action": "ENTRY", "date": "02 JUN 2021", "cx": 648, "cy": 196,
         "w": 208, "h": 118, "rot": -8},
        {"kind": "rect", "color": (110, 58, 140), "country": "KESTREL ISLANDS",
         "action": "EXIT", "date": "18 JUN 2021", "cx": 848, "cy": 192,
         "w": 196, "h": 112, "rot": 6},
        {"kind": "oval", "color": (168, 62, 44), "country": "REPUBLIC OF VARDOS",
         "action": "ENTRY", "date": "09 NOV 2023", "cx": 652, "cy": 340,
         "w": 208, "h": 118, "rot": -5},
        {"kind": "rect", "color": (24, 120, 110), "country": "SANTARA",
         "action": "ENTRY", "date": "04 FEB 2025", "cx": 848, "cy": 336,
         "w": 196, "h": 112, "rot": 7},
    ],
    "visa": {
        "title": "VISA - REPUBLIC OF VARDOS",
        "fields": [
            ("TYPE", "TOURIST"),
            ("ENTRIES", "MULTIPLE"),
            ("ISSUED", "12 OCT 2023"),
            ("VALID UNTIL", "11 OCT 2024"),
            ("No.", "V-2204117"),
        ],
    },
    "permit": [
        "CORAL ROUTE PERMIT REQUIRED - HOLDER MAY LAND",
        "ONLY AT PORT LIORA AND NORTH REEF",
        "REEF LEVY PAID  12 TALA",
    ],
}
# CONFIG END

# ------------------------------------------------------------ canvas ------
class Canvas:
    def __init__(self, w, h, bg=(255, 255, 255), alpha=255):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        self.alp = bytearray([alpha]) * (w * h)
        r, g, b = bg
        for i in range(w * h):
            self.buf[i * 3] = r
            self.buf[i * 3 + 1] = g
            self.buf[i * 3 + 2] = b

    def set_px(self, x, y, color, alpha=1.0):
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        i = y * self.w + x
        j = i * 3
        if alpha >= 1.0:
            self.buf[j], self.buf[j + 1], self.buf[j + 2] = color
            self.alp[i] = 255
        else:
            a = alpha
            self.buf[j] = int(self.buf[j] * (1 - a) + color[0] * a)
            self.buf[j + 1] = int(self.buf[j + 1] * (1 - a) + color[1] * a)
            self.buf[j + 2] = int(self.buf[j + 2] * (1 - a) + color[2] * a)
            self.alp[i] = max(self.alp[i], int(255 * a))

    def rect(self, x, y, w, h, color, alpha=1.0):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                self.set_px(xx, yy, color, alpha)

    def rect_outline(self, x, y, w, h, color, t=1, alpha=1.0):
        self.rect(x, y, w, t, color, alpha)
        self.rect(x, y + h - t, w, t, color, alpha)
        self.rect(x, y, t, h, color, alpha)
        self.rect(x + w - t, y, t, h, color, alpha)

    def line(self, x0, y0, x1, y1, color, width=1, alpha=1.0):
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = max(1, width // 2)
        for s in range(steps + 1):
            cx = x0 + dx * s // steps
            cy = y0 + dy * s // steps
            for yy in range(cy - r, cy + r + 1):
                for xx in range(cx - r, cx + r + 1):
                    if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r + 1:
                        self.set_px(xx, yy, color, alpha)

    def poly(self, pts, color, alpha=1.0):
        # scanline fill, works for convex and simple polygons
        ys = [p[1] for p in pts]
        for y in range(max(0, int(min(ys))), min(self.h, int(max(ys)) + 1)):
            xs = []
            n = len(pts)
            for k in range(n):
                x0, y0 = pts[k]
                x1, y1 = pts[(k + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            if len(xs) >= 2:
                xs.sort()
                for xx in range(int(math.ceil(xs[0])), int(math.floor(xs[-1])) + 1):
                    self.set_px(xx, y, color, alpha)

    def ellipse(self, cx, cy, rx, ry, color, alpha=1.0, fill=True, t=1):
        cx, cy, rx, ry = int(cx), int(cy), int(rx), int(ry)
        for y in range(cy - ry - 1, cy + ry + 2):
            dy = (y - cy) / ry if ry else 0
            if abs(dy) > 1:
                continue
            dx = rx * math.sqrt(max(0.0, 1 - dy * dy))
            x0, x1 = int(cx - dx), int(cx + dx)
            if fill:
                for xx in range(x0, x1 + 1):
                    self.set_px(xx, y, color, alpha)
            else:
                for xx in range(x0, x0 + t):
                    self.set_px(xx, y, color, alpha)
                for xx in range(x1 - t + 1, x1 + 1):
                    self.set_px(xx, y, color, alpha)

    def ellipse_outline(self, cx, cy, rx, ry, color, t=2, alpha=1.0):
        for k in range(t):
            self.ellipse(cx, cy, rx - k, ry - k, color, alpha, fill=False, t=1)

    def arc(self, cx, cy, r, a0, a1, color, width=2, alpha=1.0):
        steps = max(8, int(abs(a1 - a0) * r / 3))
        prev = None
        for s in range(steps + 1):
            a = a0 + (a1 - a0) * s / steps
            x = int(cx + r * math.cos(a))
            y = int(cy + r * math.sin(a))
            if prev is not None:
                self.line(prev[0], prev[1], x, y, color, width, alpha)
            prev = (x, y)

    def text(self, x, y, s, scale, color, spacing=1, alpha=1.0):
        cx = int(x)
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for r in range(7):
                row = g[r]
                for c in range(5):
                    if row[c] == '#':
                        self.rect(cx + c * scale, int(y) + r * scale,
                                  scale, scale, color, alpha)
            cx += (5 + spacing) * scale
        return cx

    def text_w(self, s, scale, spacing=1):
        if not s:
            return 0
        return (len(s) * (5 + spacing) - spacing) * scale

    def text_c(self, cx, y, s, scale, color, spacing=1, alpha=1.0):
        x = int(cx - self.text_w(s, scale, spacing) / 2)
        return self.text(x, y, s, scale, color, spacing, alpha)


def blit_rotated(dst, src, cx, cy, angle_deg, alpha=1.0):
    """Paste src canvas centred at (cx, cy), rotated by angle_deg."""
    ang = math.radians(angle_deg)
    ca, sa = math.cos(ang), math.sin(ang)
    w, h = src.w, src.h
    corners = []
    for px, py in ((0, 0), (w, 0), (0, h), (w, h)):
        rx = (px - w / 2) * ca - (py - h / 2) * sa
        ry = (px - w / 2) * sa + (py - h / 2) * ca
        corners.append((rx, ry))
    minx = int(cx + min(c[0] for c in corners)) - 1
    maxx = int(cx + max(c[0] for c in corners)) + 1
    miny = int(cy + min(c[1] for c in corners)) - 1
    maxy = int(cy + max(c[1] for c in corners)) + 1
    for dy in range(miny, maxy + 1):
        for dx in range(minx, maxx + 1):
            relx, rely = dx - cx, dy - cy
            sx = ca * relx + sa * rely + w / 2
            sy = -sa * relx + ca * rely + h / 2
            ix, iy = int(sx), int(sy)
            if 0 <= ix < w and 0 <= iy < h:
                sa_ = src.alp[iy * w + ix] / 255.0 * alpha
                if sa_ > 0.02:
                    j = (iy * w + ix) * 3
                    dst.set_px(dx, dy,
                               (src.buf[j], src.buf[j + 1], src.buf[j + 2]),
                               sa_)


# -------------------------------------------------------------- MRZ --------
def mrz_check(s):
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[ch] = 10 + i
    vals['<'] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def build_mrz(holder):
    doc = holder["number"].replace(" ", "")          # e.g. TLA041982
    code = holder["code"]
    line1 = "P<" + code + holder["surname"] + "<<" + \
        holder["given"].replace(" ", "<")
    line1 = line1 + "<" * (44 - len(line1))
    personal = "<" * 14
    line2 = (doc + mrz_check(doc) + code + holder["dob_mrz"] +
             mrz_check(holder["dob_mrz"]) + holder["sex"] +
             holder["expiry_mrz"] + mrz_check(holder["expiry_mrz"]) +
             personal + mrz_check(personal))
    composite_src = (doc + mrz_check(doc) + holder["dob_mrz"] +
                     mrz_check(holder["dob_mrz"]) + holder["expiry_mrz"] +
                     mrz_check(holder["expiry_mrz"]) + personal +
                     mrz_check(personal))
    line2 = line2 + mrz_check(composite_src)
    assert len(line1) == 44, len(line1)
    assert len(line2) == 44, len(line2)
    return line1, line2


# --------------------------------------------------------- drawing ---------
def draw_emblem(cv, cx, cy, r, navy, gold):
    cv.ellipse_outline(cx, cy, r, r, gold, t=3)
    cv.ellipse_outline(cx, cy, r - 6, r - 6, gold, t=1)
    if CFG.get("emblem", "sun") == "peaks":
        # mountain peaks with snow caps inside the seal
        cv.poly([(cx - 24, cy + 18), (cx - 6, cy - 16), (cx + 8, cy + 18)],
                navy)
        cv.poly([(cx - 2, cy + 18), (cx + 14, cy - 10), (cx + 26, cy + 18)],
                navy)
        cv.poly([(cx - 11, cy - 7), (cx - 6, cy - 16), (cx - 1, cy - 7)],
                (246, 239, 220))
        cv.poly([(cx + 10, cy - 2), (cx + 14, cy - 10), (cx + 18, cy - 2)],
                (246, 239, 220))
        cv.ellipse(cx, cy - 18, 5, 5, gold)
        cv.line(cx - 24, cy + 20, cx + 26, cy + 20, gold, 2)
        for sx, sy in ((cx - r + 8, cy - r + 14), (cx + r - 10, cy - r + 12)):
            cv.line(sx - 3, sy, sx + 3, sy, gold, 2)
            cv.line(sx, sy - 3, sx, sy + 3, gold, 2)
        return
    # rising sun: half disc + rays
    cv.ellipse(cx, cy - 2, r - 12, r - 12, gold, fill=True)
    cv.rect(cx - (r - 12), cy - 2, 2 * (r - 12), r - 12, CFG["paper"])
    for k in range(-4, 5):
        a = math.radians(-90 + k * 18)
        x0 = cx + int((r - 8) * math.cos(a))
        y0 = cy - 2 + int((r - 8) * math.sin(a))
        x1 = cx + int((r - 3) * math.cos(a))
        y1 = cy - 2 + int((r - 3) * math.sin(a))
        cv.line(x0, y0, x1, y1, gold, 2)
    # waves below the sun
    for k, yy in enumerate((cy + 4, cy + 10, cy + 16)):
        cv.arc(cx, yy, r - 12 - k * 2, math.radians(15), math.radians(165),
               navy, 2)
    # two small stars
    for sx, sy in ((cx - r + 8, cy - r + 14), (cx + r - 10, cy - r + 12)):
        cv.line(sx - 3, sy, sx + 3, sy, gold, 2)
        cv.line(sx, sy - 3, sx, sy + 3, gold, 2)


def draw_portrait(cv, x0, y0, w, h, holder):
    # background: vertical blue-grey gradient + soft diagonal light band
    top = (147, 167, 186)
    bot = (111, 130, 150)
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3))
        cv.rect(x0, y0 + yy, w, 1, col)
    cv.poly([(x0, y0 + 60), (x0 + w, y0 + 20), (x0 + w, y0 + 44),
             (x0, y0 + 84)], (255, 255, 255), alpha=0.07)
    skin, dark = holder["skin"], holder["skin_dark"]
    hair = holder["hair"]
    cx = x0 + w // 2
    # shoulders / jacket
    cv.poly([(x0, y0 + h), (x0, y0 + h - 34), (x0 + 26, y0 + h - 52),
             (cx - 14, y0 + h - 56), (cx + 14, y0 + h - 56),
             (x0 + w - 26, y0 + h - 52), (x0 + w, y0 + h - 34)],
            holder["jacket"])
    # blouse V
    cv.poly([(cx - 13, y0 + h - 56), (cx + 13, y0 + h - 56),
             (cx, y0 + h - 30)], (232, 226, 210))
    # neck
    cv.rect(cx - 11, y0 + h - 74, 22, 22, dark)
    # hair mass behind the face
    cv.ellipse(cx, y0 + 62, 40, 48, hair)
    # face
    cv.ellipse(cx, y0 + 76, 33, 41, skin)
    # hair: fringe cap + side locks (long style) or short crop
    if holder["hair_style"] == "long":
        cv.ellipse(cx, y0 + 44, 37, 24, hair)
        cv.ellipse(cx - 33, y0 + 88, 9, 42, hair)
        cv.ellipse(cx + 33, y0 + 88, 9, 42, hair)
        cv.ellipse(cx, y0 + 40, 30, 16, hair)
    else:
        cv.ellipse(cx, y0 + 42, 34, 20, hair)
        cv.ellipse(cx - 30, y0 + 66, 7, 18, hair)
        cv.ellipse(cx + 30, y0 + 66, 7, 18, hair)
    # soft cheek shade
    cv.ellipse(cx - 20, y0 + 92, 8, 5, dark, alpha=0.25)
    cv.ellipse(cx + 20, y0 + 92, 8, 5, dark, alpha=0.25)
    # brows
    cv.line(cx - 20, y0 + 66, cx - 8, y0 + 64, hair, 2)
    cv.line(cx + 8, y0 + 64, cx + 20, y0 + 66, hair, 2)
    # eyes
    cv.ellipse(cx - 14, y0 + 72, 4, 3, (30, 24, 20))
    cv.ellipse(cx + 14, y0 + 72, 4, 3, (30, 24, 20))
    cv.ellipse(cx - 13, y0 + 71, 1, 1, (255, 255, 255))
    cv.ellipse(cx + 15, y0 + 71, 1, 1, (255, 255, 255))
    # nose
    cv.line(cx + 1, y0 + 76, cx - 1, y0 + 90, dark, 2)
    cv.line(cx - 1, y0 + 90, cx + 3, y0 + 91, dark, 2)
    # lips
    cv.ellipse(cx, y0 + 101, 7, 3, holder["lips"])
    cv.line(cx - 7, y0 + 101, cx + 7, y0 + 101, (120, 50, 50), 1)
    # short beard shading around the jaw
    if holder.get("beard"):
        cv.ellipse(cx, y0 + 106, 24, 12, holder["hair"], alpha=0.25)
        cv.ellipse(cx, y0 + 101, 8, 3, holder["skin"])
        cv.line(cx - 8, y0 + 96, cx + 8, y0 + 96, holder["hair"], 2,
                alpha=0.7)
    # necklace: gold beads along a curve (atoll motif)
    if holder.get("necklace"):
        for k in range(9):
            t = k / 8.0
            bx = int(cx - 22 + 44 * t)
            by = int(y0 + h - 46 + 12 * math.sin(t * math.pi))
            cv.ellipse(bx, by, 2, 2, CFG["gold"])
        cv.ellipse(cx, y0 + h - 33, 4, 4, CFG["gold"])


def make_stamp(st):
    """Render one ink stamp on its own transparent canvas."""
    w, h = st["w"], st["h"]
    cv = Canvas(w, h, bg=(0, 0, 0), alpha=0)
    col = st["color"]
    if st["kind"] == "oval":
        cv.ellipse_outline(w // 2, h // 2, w // 2 - 3, h // 2 - 3, col, t=3)
        cv.ellipse_outline(w // 2, h // 2, w // 2 - 9, h // 2 - 9, col, t=1)
        y = 22
        cv.text_c(w // 2, y, st["country"], 2, col, spacing=0)
        y += 30
        cv.text_c(w // 2, y, st["action"], 3, col, spacing=2)
        y += 32
        cv.text_c(w // 2, y, st["date"], 2, col, spacing=1)
    else:
        cv.rect_outline(3, 3, w - 6, h - 6, col, t=3)
        cv.rect_outline(9, 9, w - 18, h - 18, col, t=1)
        y = 16
        cv.text_c(w // 2, y, st["country"], 2, col, spacing=0)
        y += 26
        cv.text_c(w // 2, y, st["action"], 3, col, spacing=2)
        y += 32
        cv.text_c(w // 2, y, st["date"], 2, col, spacing=1)
    return cv


def field(cv, x, y, label, value, scale=2, spacing=1):
    cv.text(x, y, label, 1, CFG["label"], spacing=1)
    cv.text(x, y + 11, value, scale, CFG["ink"], spacing=spacing)


def draw_spread():
    navy, gold, paper, ink = CFG["navy"], CFG["gold"], CFG["paper"], CFG["ink"]
    holder = CFG["holder"]
    cv = Canvas(W, H, bg=(24, 34, 54))
    # desk vignette: darker corners
    for yy in range(H):
        t = abs(yy - H / 2) / (H / 2)
        cv.rect(0, yy, W, 1, (18, 26, 44), alpha=t * 0.25)
    # spread pages
    cv.rect(36, 36, 952, 652, paper)
    # faint guilloche waves on both pages
    for base_y in (560, 580):
        for x in range(48, 976, 4):
            yy = base_y + int(3 * math.sin(x / 18.0))
            cv.set_px(x, yy, gold, alpha=0.30)
    # centre gutter shadow + fold line
    for k in range(10):
        cv.rect(508 - k, 36, 1, 652, (0, 0, 0), alpha=0.05 * (10 - k) / 10)
        cv.rect(514 + k, 36, 1, 652, (0, 0, 0), alpha=0.05 * (10 - k) / 10)
    cv.line(512, 36, 512, 688, (120, 100, 60), 1, alpha=0.5)
    # outer page border
    cv.rect_outline(36, 36, 952, 652, navy, t=3)
    cv.rect_outline(42, 42, 940, 640, gold, t=1, alpha=0.7)

    # ============================ LEFT PAGE: data page ==================
    lx = 274  # centre of left page
    cv.rect(56, 54, 436, 2, gold)
    cv.text_c(lx, 64, CFG["country"], 3, navy, spacing=1)
    cv.text_c(lx, 92, CFG["doc_title"], 2, navy, spacing=4)
    cv.rect(56, 116, 436, 1, gold, alpha=0.8)
    draw_emblem(cv, lx, 156, 34, navy, gold)

    # portrait (left or right of the data fields, per config)
    if CFG.get("photo_left", True):
        px0, fx = 56, 216
    else:
        px0, fx = 352, 56
    py0, pw, ph = 196, 140, 188
    cv.rect_outline(px0 - 3, py0 - 3, pw + 6, ph + 6, navy, t=2)
    draw_portrait(cv, px0, py0, pw, ph, holder)
    cv.text_c(px0 + pw // 2, py0 + ph + 10, "PHOTOGRAPH", 1,
              CFG["label"], spacing=1)

    # data fields beside the portrait
    field(cv, fx, 196, "SURNAME", holder["surname"])
    field(cv, fx, 238, "GIVEN NAMES", holder["given"])
    field(cv, fx, 280, "NATIONALITY", holder["nationality"])
    field(cv, fx, 322, "DATE OF BIRTH", holder["dob"])
    field(cv, fx, 364, "PLACE OF BIRTH", holder["pob"])

    # lower data rows
    field(cv, 56, 420, "DATE OF ISSUE", holder["issue"])
    field(cv, 300, 420, "DATE OF EXPIRY", holder["expiry"])
    field(cv, 56, 462, "PASSPORT No.", holder["number"])
    field(cv, 300, 462, "SEX", holder["sex"])
    field(cv, 56, 504, "ISSUING AUTHORITY", holder["authority"], spacing=0)
    cv.text(56, 528, holder["authority2"], 2, ink, spacing=0)

    # holder signature
    cv.text(300, 504, "SIGNATURE OF HOLDER", 1, CFG["label"], spacing=1)
    sig = []
    for k in range(60):
        t = k / 59.0
        sx = 300 + int(150 * t)
        sy = 528 + int(5 * math.sin(t * 9.0) - 3 * math.sin(t * 23.0))
        sig.append((sx, sy))
    for a, b in zip(sig, sig[1:]):
        cv.line(a[0], a[1], b[0], b[1], ink, 2)
    cv.line(300, 540, 452, 540, CFG["label"], 1)

    # MRZ
    cv.rect(52, 566, 444, 1, navy, alpha=0.8)
    line1, line2 = build_mrz(holder)
    cv.text(56, 578, line1, 2, ink, spacing=0)
    cv.text(56, 606, line2, 2, ink, spacing=0)
    cv.text_c(lx, 640,
              "P<" + holder["code"] + "  " +
              holder["number"].replace(" ", "") + "  " + holder["short"],
              1, CFG["label"], spacing=1)

    # ============================ RIGHT PAGE: visas =====================
    rx = 750  # centre of right page
    cv.rect(532, 54, 436, 2, gold)
    cv.text_c(rx, 64, "VISAS", 3, navy, spacing=1)
    cv.text_c(rx, 92, "ENTRIES - EXITS", 1, CFG["label"], spacing=2)
    cv.rect(532, 116, 436, 1, gold, alpha=0.8)
    cv.text(536, 124, "12", 2, CFG["label"], spacing=1)

    # stamps
    for st in CFG["stamps"]:
        scv = make_stamp(st)
        blit_rotated(cv, scv, st["cx"], st["cy"], st["rot"], alpha=0.88)

    # visa sticker
    vx, vy, vw, vh = 580, 470, 340, 118
    vcv = Canvas(vw, vh, bg=(238, 240, 226), alpha=255)
    vcv.rect_outline(0, 0, vw, vh, navy, t=2)
    vcv.rect(0, 0, vw, 26, navy)
    vcv.text_c(vw // 2, 6, CFG["visa"]["title"], 2, (246, 239, 220), spacing=1)
    yy = 36
    for lab, val in CFG["visa"]["fields"]:
        vcv.text(14, yy, lab, 1, CFG["label"], spacing=1)
        vcv.text(120, yy, val, 1, ink, spacing=1)
        yy += 15
    # diagonal security stripes on the sticker corner
    for k in range(5):
        vcv.line(vw - 40 + k * 8, vh - 2, vw - 20 + k * 8, vh - 22,
                 gold, 2, alpha=0.6)
    blit_rotated(cv, vcv, vx + vw // 2, vy + vh // 2, -2, alpha=0.97)

    # coral route permit box
    bx0, by0, bw, bh = 556, 606, 388, 62
    cv.rect_outline(bx0, by0, bw, bh, (148, 52, 40), t=2)
    cv.rect_outline(bx0 + 4, by0 + 4, bw - 8, bh - 8, (148, 52, 40), t=1)
    cv.text_c(bx0 + bw // 2, by0 + 10, CFG["permit"][0], 1, (148, 52, 40),
              spacing=1)
    cv.text_c(bx0 + bw // 2, by0 + 24, CFG["permit"][1], 1, (148, 52, 40),
              spacing=1)
    cv.text_c(bx0 + bw // 2, by0 + 42, CFG["permit"][2], 1, (148, 52, 40),
              spacing=2)
    return cv


# -------------------------------------------------------------- PNG -------
def write_png(path, cv):
    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    rows = bytearray()
    prev = bytearray(cv.w * 3)
    for y in range(cv.h):
        row = bytes(cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3])
        # filter type 2 (Up)
        enc = bytearray(len(row))
        for i, b in enumerate(row):
            enc[i] = (b - prev[i]) & 0xFF
        rows += b"\x02" + bytes(enc)
        prev = bytearray(row)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(rows), 9)) +
            chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    cv = draw_spread()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
        n = write_png(os.path.join(out_dir, "entry.png"), cv)
        print("wrote", os.path.join(out_dir, "entry.png"), n, "bytes")
    except OSError as e:
        print("cannot write", out_dir + ":", e)
    try:
        n = write_png("entry.png", cv)
        print("wrote ./entry.png", n, "bytes", cv.w, "x", cv.h)
    except OSError as e:
        print("cannot write ./entry.png:", e)


if __name__ == "__main__":
    main()

# THE WORLD TODAY -- Friday 20 November 2026
# A program that draws one newspaper front page (1024x1024 PNG) at runtime.
# Python standard library only. No network. No clock. No randomness.
# The same input always writes the same bytes.
import os
import struct
import sys
import zlib

W = 1024
H = 1024

PAPER = (247, 241, 222)
PAPER2 = (238, 229, 203)
PAPER3 = (228, 217, 186)
INK = (20, 20, 20)
GREY = (105, 100, 88)
RULE = (154, 145, 126)
RED = (179, 27, 27)
RED_DK = (140, 18, 18)
NAVY = (27, 42, 74)
NAVY2 = (43, 64, 104)
TEAL = (15, 94, 90)
TEAL_DK = (10, 66, 63)
GOLD = (192, 138, 0)
GOLD_LT = (217, 164, 65)
GREEN = (46, 107, 52)
WHITE = (255, 255, 255)
CREAM = (255, 250, 235)
SKY = (58, 84, 122)
SKY_DK = (36, 54, 84)
SEA = (28, 110, 108)
SAND = (226, 200, 148)

# ---------------------------------------------------------------- font
# 5x7 glyphs, rows top to bottom, '#' = ink. Uppercase-only newspaper face.
GLYPHS = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    ',': ("00000", "00000", "00000", "00000", "00110", "00100", "01000"),
    ':': ("00000", "00110", "00110", "00000", "00110", "00110", "00000"),
    ';': ("00000", "00110", "00110", "00000", "00110", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    '~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    '^': ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    '\u2014': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '\u2019': ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '\u2022': ("00000", "00000", "00110", "01110", "01110", "00110", "00000"),
    '\u00b0': ("01100", "10010", "10010", "01100", "00000", "00000", "00000"),
    '\u2192': ("00000", "00100", "00010", "11111", "00010", "00100", "00000"),
    '\u2191': ("00100", "01110", "10101", "00100", "00100", "00100", "00100"),
    '\u2193': ("00100", "00100", "00100", "00100", "10101", "01110", "00100"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def wrap_text(s, max_w, scale):
    """Greedy word wrap. Returns list of lines, each fitting max_w."""
    cell = 6 * scale
    max_chars = max(1, max_w // cell)
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        if len(wd) > max_chars:
            # hard-split an overlong word
            if cur:
                lines.append(cur)
                cur = ""
            while len(wd) > max_chars:
                lines.append(wd[:max_chars])
                wd = wd[max_chars:]
            cur = wd
            continue
        trial = wd if not cur else cur + " " + wd
        if len(trial) <= max_chars:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.px = bytearray(W * H * 3)
        self.fill(0, 0, W, H, PAPER)

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        for yy in range(y0, y1):
            base = (yy * W + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def rect(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=1):
        for yy in range(cy - r - 1, cy + r + 2):
            for xx in range(cx - r - 1, cx + r + 2):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - t) * (r - t) <= d2 <= r * r:
                    self.set(xx, yy, c)

    def poly(self, pts, c):
        # scanline fill, deterministic
        if not pts:
            return
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    if y1 != y0:
                        xs.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for xx in range(xs[k], xs[k + 1] + 1):
                    self.set(xx, yy, c)

    def stipple(self, x, y, w, h, c, step, seed):
        # deterministic halftone: dots where a fixed hash is small
        for yy in range(y, y + h, step):
            for xx in range(x, x + w, step):
                v = ((xx * 73856093) ^ (yy * 19349663) ^ seed) % 97
                if v < 34:
                    self.set(xx, yy, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = GLYPHS.get(ch.upper(), GLYPHS.get(ch))
            if g is None:
                cx += 6 * scale
                continue
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        self.fill(cx + col * scale, y + r * scale, scale, scale, c)
            cx += 6 * scale
        return cx - x

    def text_r(self, x_right, y, s, scale, c):
        return self.text(x_right - text_width(s, scale), y, s, scale, c)

    def text_c(self, x, w, y, s, scale, c):
        return self.text(x + (w - text_width(s, scale)) // 2, y, s, scale, c)

    def para(self, x, y, s, max_w, scale, c, leading=2):
        lh = 7 * scale + leading
        for i, ln in enumerate(wrap_text(s, max_w, scale)):
            self.text(x, y + i * lh, ln, scale, c)
        return len(wrap_text(s, max_w, scale)) * lh


    def grain_paper(self):
        # Fine luminance grain over the whole picture: deterministic,
        # low amplitude, so type stays crisp while flat colour gains
        # the tooth of newsprint. 42% of pixels shift by -4..+4.
        px = self.px
        for idx in range(W * H):
            i = idx * 3
            x = idx % W
            y = idx // W
            hv = (x * 374761393 + y * 668265263) & 0x7FFFFFFF
            if hv % 100 < 42:
                d = (hv // 100) % 9 - 4
                if d:
                    r = px[i] + d
                    g = px[i + 1] + d
                    b = px[i + 2] + d
                    px[i] = 0 if r < 0 else (255 if r > 255 else r)
                    px[i + 1] = 0 if g < 0 else (255 if g > 255 else g)
                    px[i + 2] = 0 if b < 0 else (255 if b > 255 else b)


# ---------------------------------------------------------------- png
def write_png(cv, path):
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw.extend(cv.px[yy * stride:(yy + 1) * stride])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- scenes
def caption(cv, x, y, w, s):
    # small black label strip at the foot of an illustration
    cv.fill(x, y, w, 12, INK)
    cv.text(x + 4, y + 2, s, 1, WHITE)


def scene_court(cv, x, y, w, h):
    cv.fill(x, y, w, h, NAVY)
    cv.stipple(x, y, w, h, NAVY2, 3, 11)
    for yy in range(y + 4, y + h - 14, 5):
        cv.hline(x + 2, yy, w - 4, NAVY2, 1)
    # sunburst behind the pediment
    cx, cy = x + w // 2, y + h - 8
    for k in range(-6, 7):
        cv.line(cx, cy, cx + k * 26, y + 2, GOLD_LT)
    # pediment + columns
    cv.poly([(x + 18, y + 34), (x + w - 18, y + 34), (cx, y + 10)], PAPER)
    cv.rect(x + 22, y + 34, w - 44, 4, INK)
    for i in range(5):
        px = x + 30 + i * ((w - 76) // 4)
        cv.fill(px, y + 40, 10, h - 52, PAPER)
        cv.fill(px - 2, y + 38, 14, 4, PAPER)
        cv.fill(px - 2, y + h - 16, 14, 4, PAPER)
    cv.fill(x + 14, y + h - 12, w - 28, 4, PAPER)
    # scales of justice on the pediment
    sx, sy = cx, y + 16
    cv.line(sx, sy, sx, sy + 12, INK)
    cv.line(sx - 9, sy + 3, sx + 9, sy + 3, INK)
    cv.poly([(sx - 12, sy + 4), (sx - 6, sy + 4), (sx - 9, sy + 11)], GOLD)
    cv.poly([(sx + 6, sy + 4), (sx + 12, sy + 4), (sx + 9, sy + 11)], GOLD)
    cv.disc(sx, sy - 1, 2, GOLD)
    # steps
    cv.fill(x + 8, y + h - 8, w - 16, 3, PAPER3)
    caption(cv, x, y + h - 12, w, "THE HAGUE  \u2022  19 NOV  \u2022  191 PAGES")


def scene_kyiv(cv, x, y, w, h):
    cv.fill(x, y, w, h, SKY_DK)
    cv.stipple(x, y, w, h, SKY, 4, 23)
    for yy in range(y + 4, y + h - 28, 6):
        cv.hline(x + 2, yy, w - 4, SKY, 1)
    # stars / drone dots with trails
    for k in range(9):
        dx = x + 14 + k * 34
        dy = y + 8 + (k * 7) % 18
        cv.set(dx, dy, WHITE)
        cv.line(dx - 10, dy + 4, dx, dy, WHITE)
    # skyline
    base = y + h - 26
    heights = [34, 52, 28, 62, 40, 48, 30, 56, 36, 44]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = x + i * bw + 2
        cv.fill(bx, base - hh, bw - 4, hh + 14, INK)
        for wy in range(4):
            for wx in range(2):
                if (i + wy + wx) % 2 == 0:
                    cv.fill(bx + 3 + wx * 6, base - hh + 5 + wy * 9, 3, 4, GOLD_LT)
    # river + bridge arcs
    cv.fill(x, base + 10, w, h - (base + 10 - y), TEAL)
    for bx in range(x + 10, x + w - 10, 46):
        cv.line(bx, base + 12, bx + 23, base + 2, WHITE)
        cv.line(bx + 23, base + 2, bx + 46, base + 12, WHITE)
    # explosions
    for ex, ey, r in ((x + w - 60, y + 26, 13), (x + 54, y + 18, 10), (x + w // 2, y + 40, 8)):
        cv.poly([(ex, ey - r), (ex + 3, ey - 3), (ex + r, ey - 2), (ex + 4, ey + 3),
                 (ex + r - 3, ey + r - 2), (ex, ey + 5), (ex - r + 3, ey + r - 2),
                 (ex - 4, ey + 3), (ex - r, ey - 2), (ex - 3, ey - 3)], GOLD)
        cv.disc(ex, ey, 3, RED)
    caption(cv, x, y + h - 12, w, "KYIV  \u2022  OVERNIGHT 20 NOV  \u2022  400+ DRONES")


def scene_shenzhen(cv, x, y, w, h):
    cv.fill(x, y, w, h, TEAL_DK)
    cv.stipple(x, y, w, h, TEAL, 3, 37)
    for yy in range(y + 4, y + h - 26, 5):
        cv.hline(x + 2, yy, w - 4, TEAL, 1)
    # towers
    for i, (tx, th) in enumerate(((x + 16, 46), (x + 44, 58), (x + w - 66, 52), (x + w - 34, 38))):
        cv.fill(tx, y + h - 30 - th, 22, th + 30, NAVY)
        cv.fill(tx + 8, y + h - 38 - th, 6, 8, GOLD_LT)
        for wy in range(3):
            cv.fill(tx + 4, y + h - 24 - th + wy * 14, 14, 3, GOLD_LT)
    # flags: USA, CHINA, RUSSIA (simplified)
    poles = [x + w // 2 - 52, x + w // 2 - 6, x + w // 2 + 40]
    for i, px in enumerate(poles):
        cv.vline(px, y + 16, 52, WHITE, 2)
        if i == 0:
            cv.fill(px + 2, y + 16, 34, 20, WHITE)
            for s in range(3):
                cv.fill(px + 2, y + 20 + s * 6, 34, 3, RED)
            cv.fill(px + 2, y + 16, 14, 10, NAVY)
        elif i == 1:
            cv.fill(px + 2, y + 16, 34, 20, RED)
            cv.disc(px + 10, y + 26, 3, GOLD)
            for k in range(4):
                cv.set(px + 20 + (k % 2) * 6, y + 19 + (k // 2) * 6, GOLD)
        else:
            cv.fill(px + 2, y + 16, 34, 7, WHITE)
            cv.fill(px + 2, y + 23, 34, 6, NAVY2)
            cv.fill(px + 2, y + 29, 34, 7, RED)
    # round table
    cv.poly([(x + w // 2 - 44, y + h - 24), (x + w // 2 + 44, y + h - 24),
             (x + w // 2 + 30, y + h - 12), (x + w // 2 - 30, y + h - 12)], GOLD)
    cv.fill(x + w // 2 - 30, y + h - 14, 60, 3, GOLD_LT)
    caption(cv, x, y + h - 12, w, "SHENZHEN  \u2022  KYLIN VILLA  \u2022  19 NOV")


def scene_akvan(cv, x, y, w, h):
    cv.fill(x, y, w, h, SEA)
    # spiral
    cx, cy = x + w // 2, y + h // 2 - 4
    for r in range(8, 44, 6):
        cv.ring(cx, cy, r, WHITE, 2)
        cv.disc(cx + r - 4, cy - 2, 2, WHITE)
    cv.disc(cx, cy, 6, GOLD)
    cv.ring(cx, cy, 6, INK, 1)
    # rain
    for k in range(14):
        rx = x + 8 + (k * 29) % (w - 10)
        ry = y + 6 + (k * 13) % (h - 22)
        cv.line(rx, ry, rx - 5, ry + 9, WHITE)
    # coastline + waves
    cv.poly([(x, y + h - 22), (x + w // 3, y + h - 30), (x + 2 * w // 3, y + h - 18),
             (x + w, y + h - 26), (x + w, y + h), (x, y + h)], SAND)
    for k in range(5):
        wx = x + 10 + k * 44
        cv.line(wx, y + h - 8, wx + 18, y + h - 8, WHITE)
        cv.line(wx + 4, y + h - 4, wx + 14, y + h - 4, WHITE)
    caption(cv, x, y + h - 12, w, "GOPALPUR  \u2022  LANDFALL 20 NOV  \u2022  70-80 KM/H")


def scene_markets(cv, x, y, w, h):
    cv.fill(x, y, w, h, CREAM)
    cv.stipple(x, y, w, h, PAPER3, 4, 51)
    # grid
    for gy in range(y + 8, y + h - 16, 14):
        cv.hline(x + 8, gy, w - 16, RULE, 1)
    # candlesticks: staircase falling left to right, inside the panel
    bw = (w - 24) // 7
    for i in range(7):
        bx = x + 12 + i * bw + 4
        top = y + 18 + i * 6
        bot = top + 16
        cv.vline(bx + bw // 2 - 2, top - 6, (bot - top) + 12, INK, 1)
        cv.fill(bx, top, bw - 8, bot - top, RED if i > 1 else GREEN)
    # falling arrow, inside the panel
    cv.line(x + 14, y + 20, x + w - 16, y + 74, RED_DK)
    cv.line(x + w - 16, y + 74, x + w - 32, y + 74, RED_DK)
    cv.line(x + w - 16, y + 74, x + w - 16, y + 60, RED_DK)
    cv.text(x + 8, y + 4, "S&P -3.7%  NASDAQ -5.28%", 1, RED_DK)
    caption(cv, x, y + h - 12, w, "NEW YORK  \u2022  CLOSE 20 NOV  \u2022  VIX 35.89")


def lead_panel(cv, x, y, w, h, scene, kicker, head, deck, foot, illus_h):
    cv.fill(x, y, w, h, PAPER2)
    cv.rect(x, y, w, h, INK, 1)
    scene(cv, x + 1, y + 1, w - 2, illus_h)
    ty = y + illus_h + 6
    cv.text(x + 8, ty, kicker, 1, RED)
    ty += 11
    lines = wrap_text(head, w - 16, 2)
    for ln in lines[:2]:
        cv.text(x + 8, ty, ln, 2, INK)
        ty += 18
    ty += 1
    dl = wrap_text(deck, w - 16, 1)
    for ln in dl[:3]:
        cv.text(x + 8, ty, ln, 1, INK)
        ty += 9
    cv.hline(x + 8, y + h - 14, w - 16, RULE, 1)
    cv.text(x + 8, y + h - 11, foot, 1, GREY)
    return ty


def brief(cv, x, y, w, head, body, avail_h):
    """One brief. Returns height used."""
    lh = 9
    head_lines = wrap_text(head, w, 1)
    body_lines = wrap_text(body, w, 1)
    total = len(head_lines) * lh + len(body_lines) * lh + 4
    if total > avail_h:
        # trim body lines to fit (data is tuned so this does not trigger)
        keep = max(0, (avail_h - 4) // lh - len(head_lines))
        body_lines = body_lines[:keep]
        total = len(head_lines) * lh + len(body_lines) * lh + 4
    ty = y
    for ln in head_lines:
        cv.text(x, ty, ln, 1, NAVY)
        ty += lh
    for ln in body_lines:
        cv.text(x, ty, ln, 1, INK)
        ty += lh
    cv.hline(x, ty + 1, w, RULE, 1)
    return total


def region_block(cv, x, y, w, h, title, count, items, color):
    cv.fill(x, y, w, h, PAPER2)
    cv.rect(x, y, w, h, INK, 1)
    cv.fill(x + 1, y + 1, w - 2, 18, color)
    cv.text(x + 8, y + 5, title, 1, WHITE)
    cv.text_r(x + w - 8, y + 5, count, 1, WHITE)
    inner_x = x + 8
    inner_w = w - 16
    top = y + 22
    avail = y + h - 4 - top
    # measure all briefs first, distribute slack as even gaps
    heights = []
    for head, body in items:
        hl = len(wrap_text(head, inner_w, 1))
        bl = len(wrap_text(body, inner_w, 1))
        heights.append((hl + bl) * 9 + 4)
    used = sum(heights)
    if used > avail:
        raise ValueError('region overflow: ' + title)
    gaps = len(items) + 1
    gap = max(2, (avail - used) // gaps) if avail > used else 2
    ty = top + gap
    for (head, body), hh in zip(items, heights):
        brief(cv, inner_x, ty, inner_w, head, body, hh)
        ty += hh + gap


# ---------------------------------------------------------------- data
# Every story is dated on the page. 19 NOV events are marked 19 NOV:
# the brief is the news of 20 NOVEMBER, including what was first
# reported, reacted to or closed on that day.
LEADS = [
    dict(scene=scene_court, kicker="LEAD  \u2022  INTERNATIONAL COURT OF JUSTICE",
         head="THE COURT SPEAKS: GENOCIDE",
         deck="MYANMAR COMMITTED GENOCIDE AGAINST THE ROHINGYA, THE ICJ RULED 9-6 IN ITS FIRST STATE RULING IN 80 YEARS. REPARATIONS AND SAFE RETURN ORDERED.",
         foot="THE HAGUE - GAMBIA BROUGHT THE CASE IN 2019 - MYANMAR CALLED IT UNFAIR ON FRIDAY"),
    dict(scene=scene_kyiv, kicker="LEAD  \u2022  UKRAINE",
         head="A NIGHT OF FIRE OVER KYIV",
         deck="MORE THAN 400 DRONES AND 110 MISSILES, 27 OF THEM BALLISTIC, HIT BRIDGES, POWER AND RAIL. AT LEAST 8 KILLED, 28 WOUNDED.",
         foot="KYIV - 3 BRIDGES HIT - POWER OUT IN 11 REGIONS"),
    dict(scene=scene_shenzhen, kicker="DIPLOMACY  \u2022  APEC",
         head="THREE FLAGS, ONE TABLE",
         deck="XI, TRUMP AND PUTIN MET FOR THE FIRST TIME AS THREE LEADERS. 80 MINUTES, A PEACE DECLARATION, AND TALKS ON NUCLEAR RISK.",
         foot="SHENZHEN - 80 MINUTES - NO DEAL ON REGULAR MEETINGS"),
    dict(scene=scene_akvan, kicker="WEATHER  \u2022  BAY OF BENGAL",
         head="AKVAN COMES ASHORE",
         deck="THE CYCLONE CROSSED NEAR GOPALPUR, 70-80 KM/H, THEN WEAKENED TO A DEPRESSION. NO MAJOR DAMAGE OR LOSS OF LIFE REPORTED.",
         foot="GOPALPUR - 50,000 EVACUATED - FIRST IN NOVEMBER SINCE 1995"),
    dict(scene=scene_markets, kicker="MARKETS  \u2022  THE AI ROUT",
         head="THE AI ROUT GOES GLOBAL",
         deck="S&P -3.7%, DOW -1.9%, NASDAQ -5.3% AND NEGATIVE FOR THE YEAR. THE VIX SAT AT 35.89, ITS HIGHEST IN 19 MONTHS.",
         foot="NEW YORK - WORST WEEK SINCE MARCH 2020"),
]

REGIONS_TOP = [
    ("EUROPE", "5 STORIES", RED, [
        ("POLAND: MISSILES FALL (20 NOV)",
         "2 MISSILES AND A DRONE FELL; NO CASUALTIES."),
        ("DENMARK EXPELS ATTACHE (20 NOV)",
         "PLOT TO KILL RAPPER KYIVSTONER; 7 DAYS TO LEAVE."),
        ("BERLIN: ALLIES HOLD LINE (19 NOV)",
         "25+ LEADERS; SECURITY GUARANTEES AGREED."),
        ("KYIV: CATHEDRAL, EMBASSIES HIT (19 NOV)",
         "THURSDAY STRIKES DAMAGED A CATHEDRAL AND 3 EMBASSIES."),
        ("EXERCISE KOALICJA (20 NOV)",
         "5,000-6,000 TROOPS REHEARSE POST-WAR MISSION."),
    ]),
    ("ASIA-PACIFIC", "5 STORIES", NAVY, [
        ("MYANMAR: RULING REJECTED (20 NOV)",
         "GOVERNMENT CALLED IT UNFAIR; GUTERRES WELCOMED IT."),
        ("TAKAICHI GETS COLD SHOULDER (19 NOV)",
         "SUBDUED WELCOME IN SHENZHEN AMID THE TAIWAN ROW."),
        ("TRUMP BRIEFS TAKAICHI (20 NOV)",
         "A 20-MINUTE CALL ON THE TRILATERAL, TOKYO SAID."),
        ("KOREA-CHINA FTA SEALED (18 NOV)",
         "SERVICES AND INVESTMENT TALKS END AFTER 8 YEARS."),
        ("APEC OUTLOOK ADOPTED (19 NOV)",
         "21 ECONOMIES BACK THE OUTLOOK; TRUCE TO 10 JAN."),
    ]),
    ("MIDDLE EAST", "4 STORIES", TEAL, [
        ("IRAN: TALK, NO DEAL YET (20 NOV)",
         "ARAGHCHI: HORMUZ CAN REOPEN IF TERMS MET; URANIUM STAYS. TRUMP: NO ACCEPTABLE DEAL YET."),
        ("RIYADH ALERTS, HODEIDAH HIT (20 NOV)",
         "3 MISSILES TOWARD RIYADH INTERCEPTED; COALITION STRUCK THE PORT; HOUTHIS DEMAND PORT EVACUATIONS."),
        ("GAZA: AT LEAST 5 KILLED (20 NOV)",
         "HOSPITAL SOURCES COUNT THE DEAD IN CENTRAL GAZA STRIKES; LEBANON'S QANTARA WAS ALSO HIT."),
        ("IRAQ MOVES; TANKERS HIT (20 NOV)",
         "FORCES ENTER A KATAEB HEZBOLLAH STRONGHOLD; 2 TANKERS STRUCK MINES EAST OF HORMUZ."),
    ]),
]

REGIONS_BOT = [
    ("AFRICA", "4 STORIES", GREEN, [
        ("MLAMBO-NGCUKA DIES, 71 (20 NOV)",
         "SOUTH AFRICA'S FIRST WOMAN DEPUTY PRESIDENT AND EX-UN WOMEN CHIEF; ANNOUNCED ON FRIDAY."),
        ("EGYPT: FINAL IMF REVIEW (20 NOV)",
         "THE $8BN PROGRAMME'S LAST REVIEW IS AGREED; $2.3BN RIDES ON A BOARD VOTE BEFORE 15 DEC."),
        ("GUINEA: IRON ORE NO. 3 (20 NOV)",
         "GUINEA OVERTAKES SOUTH AFRICA AND CANADA; SIMANDOU FEEDS CHINA, ITS BIGGEST BUYER."),
        ("HEALTH: EBOLA, MEASLES (20 NOV)",
         "CONGO EBOLA PASSES 11,000 CASES; THE US, MEXICO AND BOLIVIA LOSE MEASLES-FREE STATUS."),
    ]),
    ("AMERICAS", "5 STORIES", NAVY2, [
        ("SENATE: WAR POWERS FAIL (19 NOV)",
         "51-48; 3 REPUBLICANS CROSSED OVER."),
        ("TRUMP: GIVE HUANG A CHANCE (20 NOV)",
         "HE URGED REINSTATEMENT; THE BOARD SAID NO."),
        ("FUNDING FIGHT LOOMS (20 NOV)",
         "DUCKWORTH: NO BILL WITHOUT AN IRAN-SPENDING CUTOFF."),
        ("SANON CONVICTED (18 NOV)",
         "8 COUNTS IN THE 2021 HAITI PLOT."),
        ("CYBER CHIEF STEPS DOWN (20 NOV)",
         "CAIRNCROSS OUT; KIRSTEN DAVIES TAKES OVER."),
    ]),
    ("MARKETS + TECH", "5 STORIES", RED_DK, [
        ("ANTHROPIC: RECORD, THEN SLIDE (18-20 NOV)",
         "$81.3BN IPO; DEBUT +17%; FRIDAY -8.5% TO $89."),
        ("CHIPS LEAD THE FALL (20 NOV)",
         "NVIDIA -14%; AMD -13.3%; MICRON -13.9%."),
        ("ASIA FELL FIRST (20 NOV)",
         "NIKKEI AND KOSPI EACH DOWN OVER 5%; MSCI WORLD -3.4%."),
        ("BREADTH WAS BRUTAL (20 NOV)",
         "928 ROSE, 3,964 FELL; 826 NEW LOWS."),
        ("FEAR GAUGE SPIKES (20 NOV)",
         "VIX 35.89, +86% ON THE WEEK; 7TH LOSS IN A ROW."),
    ]),
]

LIFE = [
    ("CRICKET: TWO RESULTS (20 NOV)",
     "SOUTH AFRICA BEAT BANGLADESH BY 9 WICKETS; INDIA BOWLED NEW ZEALAND OUT FOR 368."),
    ("JEPCHIRCHIR BANNED (20 NOV)",
     "THE MARATHON CHAMPION GETS 3 YEARS AFTER ADMITTING EPO USE."),
    ("RAKSHITHA STUNS CHEN (20 NOV)",
     "THE 19-YEAR-OLD BEAT THE EX-OLYMPIC CHAMPION 21-18, 24-22 IN HONG KONG."),
    ("SPAIN-FRANCE DRAWN (20 NOV)",
     "NATIONS LEAGUE QUARTERS SET; ENGLAND FACE NORWAY."),
    ("POCHETTINO: UNITY CALL (20 NOV)",
     "THE NEW MANCHESTER UNITED BOSS PLEADS FOR LOVE BEFORE ANFIELD."),
]

TIMELINE = [
    ("18 NOV", ["ANTHROPIC PRICED $83", "KOREA-CHINA FTA SEALED",
                "SANON VERDICT (MIAMI)", "APEC WEEK OPENS"]),
    ("19 NOV", ["ICJ RULES: GENOCIDE", "SHENZHEN TRILATERAL, 80 MIN",
                "BERLIN ALLIES SUMMIT", "ANTHROPIC DEBUTS +17%",
                "SENATE VOTES 51-48"]),
    ("20 NOV", ["AKVAN LANDFALL, GOPALPUR", "KYIV BARRAGE OVERNIGHT",
                "MISSILES FALL IN POLAND", "DENMARK EXPELS ATTACHE",
                "NYSE ROUT AT THE CLOSE", "TRUMP: HUANG 2ND CHANCE"]),
]

NUMBERS = "400+ DRONES  \u2022  110+ MISSILES  \u2022  50,000 EVACUATED  \u2022  $81.3BN IPO  \u2022  -5.28% NASDAQ  \u2022  VIX 35.89  \u2022  ICJ 9-6  \u2022  SENATE 51-48"


# ---------------------------------------------------------------- layout
def build():
    cv = Canvas()
    cv.stipple(0, 0, W, H, PAPER3, 6, 3)
    # top bar
    cv.fill(0, 0, W, 22, INK)
    cv.text(8, 7, "THE WORLD TODAY", 1, WHITE)
    cv.text_c(0, W, 7, "ONE IMAGE, THE WHOLE DAY", 1, GOLD_LT)
    cv.text_r(1016, 7, "DRAWN AT RUNTIME  \u2022  NO PHOTOGRAPHS", 1, WHITE)
    # masthead
    cv.fill(0, 22, W, 86, PAPER)
    cv.hline(0, 24, W, INK, 3)
    cv.text_c(0, W, 34, "THE WORLD TODAY", 7, INK)
    cv.text(120, 90, "ONE IMAGE", 1, GREY)
    cv.text_r(904, 90, "EVERY STORY DATED", 1, GREY)
    cv.poly([(168, 94), (174, 88), (180, 94), (174, 100)], RED)
    cv.poly([(844, 94), (850, 88), (856, 94), (850, 100)], RED)
    cv.hline(0, 104, W, INK, 3)
    cv.hline(0, 107, W, RED, 1)
    # date band
    cv.fill(0, 108, W, 26, RED)
    cv.text(8, 113, "FRIDAY 20 NOVEMBER 2026", 2, WHITE)
    cv.text_r(1016, 117, "LATE EDITION  \u2022  38 STORIES  \u2022  7 REGIONS  \u2022  ALL TIMES UTC", 1, WHITE)
    cv.hline(0, 133, W, GOLD, 1)
    # leads
    lead_panel(cv, 8, 134, 664, 196, LEADS[0]["scene"], LEADS[0]["kicker"],
               LEADS[0]["head"], LEADS[0]["deck"], LEADS[0]["foot"], 110)
    lead_panel(cv, 680, 134, 336, 196, LEADS[1]["scene"], LEADS[1]["kicker"],
               LEADS[1]["head"], LEADS[1]["deck"], LEADS[1]["foot"], 110)
    for i, xx in enumerate((8, 344, 680)):
        ld = LEADS[2 + i]
        lead_panel(cv, xx, 330, 336, 176, ld["scene"], ld["kicker"],
                   ld["head"], ld["deck"], ld["foot"], 96)
    # timeline
    cv.fill(8, 506, 1008, 90, PAPER2)
    cv.rect(8, 506, 1008, 90, INK, 1)
    cv.fill(9, 507, 1006, 18, INK)
    cv.text(16, 511, "THE THREE DAYS THAT MADE FRIDAY  \u2022  DATED TIMELINE", 1, WHITE)
    cv.text_r(1008, 511, "18  \u2192  20 NOV", 1, GOLD_LT)
    for ci, (date, lines) in enumerate(TIMELINE):
        xx = 16 + ci * 336
        cv.text(xx, 530, date, 1, RED)
        cv.hline(xx, 541, 120, GOLD, 2)
        ty = 544
        for ln in lines:
            cv.text(xx, ty, "\u2022 " + ln, 1, INK)
            ty += 8
        if ci:
            cv.vline(8 + ci * 336, 528, 62, RULE, 1)
    # regions
    for i, (title, count, color, items) in enumerate(REGIONS_TOP):
        region_block(cv, 8 + i * 336, 596, 336, 160, title, count, items, color)
    for i, (title, count, color, items) in enumerate(REGIONS_BOT):
        region_block(cv, 8 + i * 336, 756, 336, 160, title, count, items, color)
    # life, science + sport
    cv.fill(8, 916, 1008, 68, PAPER2)
    cv.rect(8, 916, 1008, 68, INK, 1)
    cv.fill(9, 917, 1006, 16, TEAL)
    cv.text(16, 921, "LIFE, SCIENCE + SPORT", 1, WHITE)
    cv.text_r(1008, 921, "5 STORIES", 1, WHITE)
    for i, (head, body) in enumerate(LIFE):
        xx = 12 + i * 200
        if i:
            cv.vline(xx - 4, 936, 44, RULE, 1)
        cv.text(xx, 938, head, 1, NAVY)
        cv.para(xx, 949, body, 192, 1, INK, 2)
    # footer
    cv.fill(0, 984, W, 40, INK)
    cv.text_c(0, W, 990, NUMBERS, 1, GOLD_LT)
    cv.text_c(0, W, 1004, "SOURCES: UN NEWS  \u2022  AL JAZEERA  \u2022  REUTERS  \u2022  AP  \u2022  THE HINDU  \u2022  IMD  \u2022  XINHUA  \u2022  CNA  \u2022  NIKKEI  \u2014  19 NOV EVENTS MARKED 19 NOV", 1, (200, 196, 180))
    cv.grain_paper()
    cv.rect(0, 0, W, H, INK, 2)
    return cv


def main():
    cv = build()
    if os.path.isdir("/output"):
        path = "/output/entry.png"
    else:
        try:
            here = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            here = "."
        path = os.path.join(here, "entry.png")
    n = write_png(cv, path)
    sys.stdout.write("WROTE %s %d bytes\n" % (path, n))


if __name__ == "__main__":
    main()

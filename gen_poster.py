#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261120 round-2 poster.

Runs on the build VM only (Pillow is installed here); the grader never
executes it. Deterministic: no wall clock, no randomness, fixed fonts and
fixed layout, so two runs write byte-identical poster.png.

Layout: a 1024x1024 newspaper front page ("THE WORLD") on cream paper.
All facts come from the round-2 brief; nothing is invented here.
"""
import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 26                     # outer margin; content spans M..W-M
CW = W - 2 * M             # 972
GAP = 3                    # gap between sections
PX = 16                    # panel inner side padding
BAR = 4                    # red top bar height inside a panel

CREAM = (250, 244, 227)
PAPER = (255, 253, 245)
INK = (17, 17, 17)
RED = (185, 28, 28)
DARK = (20, 20, 20)
MUTED = (104, 98, 88)      # grey on cream / paper
DMUTED = (158, 152, 140)   # grey on the dark markets panel
CREAMTXT = (246, 241, 228) # cream text on the dark panel
FOOTGREY = (110, 104, 94)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def line_h(f):
    asc, desc = f.getmetrics()
    return asc + desc + 1


def wrap(d, text, f, maxw):
    """Greedy word wrap of one font; returns a list of lines."""
    lines, cur, curw = [], "", 0.0
    for w in text.split(" "):
        ww = d.textlength(w, font=f)
        sp = d.textlength(" ", font=f) if cur else 0.0
        if cur and curw + sp + ww > maxw:
            lines.append(cur)
            cur, curw = w, ww
        else:
            cur = (cur + " " + w) if cur else w
            curw += sp + ww
    if cur:
        lines.append(cur)
    return lines


def wrap_runs(d, runs, maxw):
    """Greedy wrap of [(text, font), ...]; returns lines of [(word, font)]."""
    words = []
    for text, f in runs:
        for w in text.split(" "):
            if w:
                words.append((w, f))
    lines, cur, curw = [], [], 0.0
    for w, f in words:
        ww = d.textlength(w, font=f)
        sp = d.textlength(" ", font=f) if cur else 0.0
        if cur and curw + sp + ww > maxw:
            lines.append(cur)
            cur, curw = [(w, f)], ww
        else:
            cur.append((w, f))
            curw += sp + ww
    if cur:
        lines.append(cur)
    return lines


def runs_width(d, line):
    total = 0.0
    for i, (w, f) in enumerate(line):
        total += d.textlength(w, font=f)
        if i < len(line) - 1:
            total += d.textlength(" ", font=f)
    return total


def draw_runs_line(d, x, y, line, fill=INK):
    cx = x
    for i, (w, f) in enumerate(line):
        d.text((cx, y), w, font=f, fill=fill)
        cx += d.textlength(w, font=f)
        if i < len(line) - 1:
            cx += d.textlength(" ", font=f)


def panel(d, y, h, dark=False):
    """Draw a panel; returns the y where its content starts."""
    fill = DARK if dark else PAPER
    d.rectangle([M, y, M + CW - 1, y + h - 1], fill=fill, outline=INK, width=1)
    d.rectangle([M + 1, y + 1, M + CW - 2, y + BAR], fill=RED)
    return y + BAR + 1


def label_line(d, x, y, text, f):
    d.text((x, y), text, font=f, fill=RED)
    return y + line_h(f)


# ---------------------------------------------------------------- sections

def masthead(d, y):
    f_title = font(SERIF_B, 36)
    title = "THE WORLD"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, y), title, font=f_title, fill=INK)
    y += line_h(f_title) + 1
    f_left = font(SANS_B, 14)
    f_right = font(SANS, 13)
    d.text((M, y), "FRIDAY 20 NOVEMBER 2026", font=f_left, fill=INK)
    right = "ONE IMAGE \u00b7 THE DAY'S NEWS"
    d.text((W - M - d.textlength(right, font=f_right), y), right,
           font=f_right, fill=MUTED)
    y += line_h(f_left) + 3
    d.rectangle([M, y, M + CW - 1, y + 1], fill=INK)
    y += 2 + 2
    d.rectangle([M, y, M + CW - 1, y + 1], fill=RED)
    y += 2
    return y


def story_panel(d, y, label, headline, deck, headline_size, deck_size):
    """White panel: red label, serif headline, wrapped sans deck."""
    f_lab = font(SANS_B, 13)
    f_head = font(SERIF_B, headline_size)
    f_deck = font(SANS, deck_size)
    inner = CW - 2 * PX
    deck_lines = wrap(d, deck, f_deck, inner)
    assert len(deck_lines) <= 3, "deck wrapped to %d lines" % len(deck_lines)
    h = (BAR + 1 + 4 + line_h(f_lab) + 2 + line_h(f_head) + 3
         + len(deck_lines) * (line_h(f_deck) - 1) + 4)
    top = panel(d, y, h)
    x = M + PX
    cy = top + 4
    cy = label_line(d, x, cy, label, f_lab) + 2
    d.text((x, cy), headline, font=f_head, fill=INK)
    cy += line_h(f_head) + 3
    for ln in deck_lines:
        d.text((x, cy), ln, font=f_deck, fill=INK)
        cy += line_h(f_deck) - 1
    return y + h


def markets_panel(d, y):
    f_head = font(SANS_B, 14)
    f_name = font(SANS_B, 12)
    f_val = font(SANS_B, 16)
    f_note = font(SANS, 10)
    f_val2 = font(SANS_B, 14)
    # Row 1: name + big value on one line, note below. Row 2: 6 tickers.
    row1 = [
        ("S&P 500", "\u22122.02%", "7,175.83"),
        ("DOW", "\u22121,101 pts (\u22122.19%)",
         "49,097.06 \u00b7 first close below 50,000 since June"),
        ("NASDAQ", "\u22122.25%", "23,879.20"),
    ]
    row2 = [
        ("NIKKEI", "\u22124.68%", None),
        ("KOSPI", "\u22124.74%", None),
        ("VIX", "above 29", "highest since March"),
        ("GOLD", "$3,588.20/oz", "14-month low"),
        ("US 10-YR", "5.05%", None),
        ("BRENT", "$89.72", None),
    ]
    row_h = line_h(f_val) + 2 + line_h(f_note)
    h = (BAR + 1 + 4 + line_h(f_head) + 2 + row_h + 3 + row_h + 4)
    top = panel(d, y, h, dark=True)
    x = M + PX
    cy = top + 4
    d.text((x, cy), "MARKETS", font=f_head, fill=RED)
    w = d.textlength("MARKETS", font=f_head)
    d.text((x + w + 8, cy), "\u2014 GLOBAL SELL-OFF", font=f_head, fill=CREAMTXT)
    cy += line_h(f_head) + 2
    # Row 1: three equal columns.
    colw = (CW - 2 * PX) / 3
    for i, (name, val, note) in enumerate(row1):
        cx = x + i * colw
        d.text((cx, cy), name, font=f_name, fill=DMUTED)
        nw = d.textlength(name, font=f_name)
        d.text((cx + nw + 8, cy - 1), val, font=f_val, fill=CREAMTXT)
        d.text((cx, cy + line_h(f_val) + 2), note, font=f_note, fill=DMUTED)
    cy += row_h + 3
    # Row 2: six equal columns.
    colw2 = (CW - 2 * PX) / 6
    for i, (name, val, note) in enumerate(row2):
        cx = x + i * colw2
        d.text((cx, cy), name, font=f_name, fill=DMUTED)
        nw = d.textlength(name, font=f_name)
        d.text((cx + nw + 6, cy - 2), val, font=f_val2, fill=CREAMTXT)
        if note:
            d.text((cx, cy + line_h(f_val) + 2), note, font=f_note,
                   fill=DMUTED)
    return y + h


def two_col(d, y, left, right):
    """Two white panels side by side. Each: label, headline, body."""
    f_lab = font(SANS_B, 12)
    f_head = font(SERIF_B, 20)
    f_body = font(SANS, 12)
    colw = (CW - GAP) / 2
    inner = colw - 2 * PX
    lb = wrap(d, left[2], f_body, inner)
    rb = wrap(d, right[2], f_body, inner)
    n = max(len(lb), len(rb))
    assert n <= 4, "two-col body wrapped to %d lines" % n
    h = (BAR + 1 + 4 + line_h(f_lab) + 1 + line_h(f_head) + 2
         + n * (line_h(f_body) - 1) + 4)
    for k, (lab, head, body_lines) in enumerate(
            [(left[0], left[1], lb), (right[0], right[1], rb)]):
        x0 = M + k * (colw + GAP)
        d.rectangle([x0, y, x0 + colw - 1, y + h - 1], fill=PAPER,
                    outline=INK, width=1)
        d.rectangle([x0 + 1, y + 1, x0 + colw - 2, y + BAR], fill=RED)
        x = x0 + PX
        cy = y + BAR + 1 + 4
        cy = label_line(d, x, cy, lab, f_lab) + 1
        d.text((x, cy), head, font=f_head, fill=INK)
        cy += line_h(f_head) + 2
        for ln in body_lines:
            d.text((x, cy), ln, font=f_body, fill=INK)
            cy += line_h(f_body) - 1
    return y + h


def conflict_panel(d, y):
    f_lab = font(SANS_B, 12)
    f_lead = font(SANS_B, 13)
    f_rest = font(SANS, 13)
    inner = CW - 2 * PX
    items = [
        ("IRAN \u2014 ", "Hormuz tanker attacks escalate: a tanker hit a "
         "mine and caught fire. Senate rejects Iran war powers, 51\u201348."),
        ("RIYADH \u2014 ", "Houthi missile hits PIF Tower, Riyadh's "
         "tallest; windows broken, no injuries. Houthis claim 4 Saudi "
         "targets."),
        ("KERCH BRIDGE \u2014 ", "Ukraine hits the Crimean bridge a third "
         "time in four days; traffic halted, Putin vows a harsher "
         "response. Leaked data: 400,000\u2013500,000 Russian deaths "
         "since 2022."),
    ]
    all_lines = []
    for lead, rest in items:
        lines = wrap_runs(d, [(lead, f_lead), (rest, f_rest)], inner)
        assert len(lines) <= 2, "conflict item wrapped to %d lines" % len(lines)
        all_lines.append(lines)
    lh = line_h(f_rest) - 1
    n_lines = sum(len(ls) for ls in all_lines)
    h = (BAR + 1 + 4 + line_h(f_lab) + 1 + n_lines * lh
         + (len(items) - 1) * 2 + 4)
    top = panel(d, y, h)
    x = M + PX
    cy = top + 4
    cy = label_line(d, x, cy, "CONFLICT", f_lab) + 1
    for li, lines in enumerate(all_lines):
        for ln in lines:
            draw_runs_line(d, x, cy, ln)
            cy += lh
        if li < len(all_lines) - 1:
            cy += 2
    return y + h


def briefs_panel(d, y):
    f_lab = font(SANS_B, 12)
    f_lead = font(SANS_B, 12)
    f_rest = font(SANS, 12)
    f_sport_lead = font(SANS_B, 12)
    f_sport = font(SANS, 12)
    inner = CW - 2 * PX
    items = [
        ("VENDOR HACK \u2014 ", "JPMorgan, Visa, Mastercard confirm a "
         "vendor hack; names and emails exposed, no card numbers."),
        ("CYBER CHIEF OUT \u2014 ", "White House cyber director Sean "
         "Cairncross out; Pentagon CIO Kirsten Davies to replace him."),
        ("PETE ROSE \u2014 ", "Trump announces a posthumous pardon for "
         "baseball star Pete Rose."),
        ("APPLE ORDER \u2014 ", "A UK court forces admission of a secret "
         "encryption order against Apple."),
        ("GAZA \u2014 ", "Five aid groups rate peace-plan implementation "
         "4 out of 26."),
        ("GREENLAND \u2014 ", "Denmark approves a Greenland defence deal, "
         "109\u20130."),
        ("TAIWAN \u2014 ", "Five measures unveiled to steady stocks; "
         "Taiwan stocks down 5,248 points in three days."),
        ("APEC \u2014 ", "Leaders adopt the Shenzhen Outlook on trade, "
         "data and AI."),
    ]
    # Every brief MUST fit on exactly one line: measure, shrink if needed.
    shrunk = []
    for lead, rest in items:
        size = 12
        while size >= 11:
            fl = font(SANS_B, size)
            fr = font(SANS, size)
            lines = wrap_runs(d, [(lead, fl), (rest, fr)], inner)
            if len(lines) == 1:
                break
            size -= 1
        assert size >= 11, "brief does not fit one line: %s" % lead
        assert len(lines) == 1, "brief wrapped: %s" % lead
        shrunk.append((lines[0], size))
    sport = [("SPORT \u2014 ", f_sport_lead),
             ("Thailand wins the AFC Diamond award as Asia's best football "
              "association, third year running; FIFA ranking 90th.",
              f_sport)]
    sport_lines = wrap_runs(d, sport, inner)
    assert len(sport_lines) == 1, "sport line wrapped"
    lh = line_h(f_rest) - 1
    h = (BAR + 1 + 4 + line_h(f_lab) + 1 + 8 * lh + 3 + 1
         + 3 + lh + 4)
    top = panel(d, y, h)
    x = M + PX
    cy = top + 4
    cy = label_line(d, x, cy, "WORLD BRIEFS", f_lab) + 1
    for line, _size in shrunk:
        draw_runs_line(d, x, cy, line)
        cy += lh
    cy += 3
    d.rectangle([x, cy, M + CW - PX - 1, cy], fill=RED)
    cy += 1 + 3
    draw_runs_line(d, x, cy, sport_lines[0])
    return y + h


def footer(d, y):
    f = font(SANS, 11)
    text = ("Sources: BBC, UN News, The Guardian, Reuters, AFP \u00b7 "
            "All figures as reported 19\u201320 Nov 2026 \u00b7 "
            "Built for make.fun")
    tw = d.textlength(text, font=f)
    d.text(((W - tw) / 2, y), text, font=f, fill=FOOTGREY)
    return y + line_h(f)


def build(out_path):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # Thin ink frame just outside the content margin.
    d.rectangle([M - 6, M - 6, W - M + 5, H - M + 5], outline=INK, width=1)
    y = M
    y = masthead(d, y) + GAP
    y = story_panel(
        d, y, "THE VERDICT \u00b7 THE HAGUE",
        "MYANMAR GUILTY OF GENOCIDE",
        "The International Court of Justice rules 9\u20136: Myanmar "
        "committed genocide against the Rohingya \u2014 the first time the "
        "court has held a state responsible for genocide. Case brought by "
        "The Gambia over the 2017 campaign; refugees in Bangladesh "
        "cheered.",
        26, 16) + GAP
    y = story_panel(
        d, y, "THE SUMMIT \u00b7 SHENZHEN",
        "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
        "First three-way summit agrees a four-point peace declaration "
        "\u2014 nuclear risk reduction, UN reform, oil & gas supply and "
        "international courts \u2014 after ~70 minutes of closed talks. "
        "The Ukraine and Iran wars are not mentioned.",
        26, 16) + GAP
    y = markets_panel(d, y) + GAP
    y = two_col(d, y,
                ("ANTHROPIC \u00b7 RECORD IPO", "RECORD IPO: $81.3 BILLION",
                 "Anthropic priced at $83, raising ~$81.3 BILLION \u2014 "
                 "the largest IPO in history. Shares opened ~$111.50 and "
                 "closed ~$97.17 (+17%), briefly valuing the firm at "
                 "~$2 TRILLION. Nasdaq ticker: ANT."),
                ("DIPLOMACY \u00b7 BERLIN", "ALLIES UNITE ON RUSSIA TALKS",
                 "European allies agree a united position for Russia "
                 "talks. US envoy Kushner says Russia is comfortable "
                 "with NATO Article 5-style guarantees for Ukraine; "
                 "Zelenskyy is unsure both sides mean the same. Macron "
                 "urges reopening NATO membership.")) + GAP
    y = conflict_panel(d, y) + GAP
    y = two_col(d, y,
                ("TECH", "NVIDIA PROBED AS CEO RESIGNS",
                 "California's attorney general subpoenaed Nvidia over "
                 "China chip disclosures; CEO Jensen Huang resigned amid "
                 "reports of an affair with a suspected Chinese spy. "
                 "Interim CEO: Colette Kress. AMD fell 7\u20138% on a "
                 "short-seller report on China ties."),
                ("CLIMATE \u00b7 COP31", "FINAL DAY IN ANTALYA",
                 "Negotiators from ~200 countries struggle for consensus "
                 "on fossil-fuel phase-out and climate finance on the "
                 "final day (9\u201320 Nov) in Antalya, T\u00fcrkiye "
                 "\u2014 divided over the 1.5\u00b0C limit.")) + GAP
    y = briefs_panel(d, y) + GAP
    y = footer(d, y)
    assert y <= H - M, "layout overflow: bottom y=%d, limit %d" % (y, H - M)
    img.save(out_path, "PNG")
    return out_path


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "poster.png")
    build(out)
    data = open(out, "rb").read()
    print("poster.png %d bytes sha256=%s"
          % (len(data), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

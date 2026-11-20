"""Poster generator for news-image-20261120.

Draws a 1024x1024 front-page newspaper summing up Friday 20 November
2026's world news. Stdlib + Pillow only, no network, fully deterministic.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 26
CW = W - 2 * MARGIN  # 972
GAP = 2  # vertical gap between sections

CREAM = (250, 244, 227)
PAPER = (255, 253, 245)
INK = (17, 17, 17)
RED = (185, 28, 28)
GREY = (96, 89, 75)
DARK = (20, 20, 20)
CREAM_TXT = (250, 244, 227)
MUTED_LT = (198, 190, 170)
RULE_GREY = (60, 60, 60)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_FONT_CACHE = {}


def font(path, size):
    key = (path, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]


def fit_font(draw, text, path, start, max_w, minimum=10):
    """Largest size <= start at which text fits max_w."""
    size = start
    while size > minimum:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, minimum)


def ink_h(draw, text, f):
    """Height of the actual glyph ink for text at font f."""
    bb = draw.textbbox((0, 0), text, font=f)
    return bb[3] - bb[1]


def ink_bottom(draw, text, f):
    """Distance from the draw anchor (top of em box) to the ink bottom.

    Use this, not ink_h, for vertical advances: with PIL's default anchor
    the glyph ink starts below the anchor, so ink_h under-measures the
    space a headline actually occupies and the next line strikes through it.
    """
    return draw.textbbox((0, 0), text, font=f)[3]


def line_h(f):
    a, d = f.getmetrics()
    return a + d


def rich_wrap(draw, runs, max_w):
    """Greedy-wrap runs [(text, font), ...] into lines of [(text, font), ...]."""
    words = []
    for text, f in runs:
        parts = text.split(" ")
        for i, p in enumerate(parts):
            if p == "" and i == len(parts) - 1:
                continue
            w = p + (" " if i < len(parts) - 1 else "")
            if w:
                words.append((w, f))
    lines, cur, cur_w = [], [], 0.0
    for w, f in words:
        ww = draw.textlength(w, font=f)
        if cur and cur_w + ww > max_w:
            lines.append(cur)
            cur, cur_w = [(w, f)], ww
        else:
            cur.append((w, f))
            cur_w += ww
    if cur:
        lines.append(cur)
    return lines


def draw_line(draw, x, y, line, fill=INK):
    cx = x
    for t, f in line:
        draw.text((cx, y), t, font=f, fill=fill)
        cx += draw.textlength(t, font=f)


def draw_lines(draw, x, y, lines, leading, fill=INK):
    for ln in lines:
        draw_line(draw, x, y, ln, fill=fill)
        y += leading
    return y


def label(draw, x, y, text, color=RED, size=14):
    f = font(SANS_B, size)
    draw.text((x, y), text, font=f, fill=color)
    return y + line_h(f) + 2


def section_box(draw, x, y, w, h, fill=None, outline=INK, width=2):
    if fill is not None:
        draw.rectangle([x, y, x + w, y + h], fill=fill)
    draw.rectangle([x, y, x + w, y + h], outline=outline, width=width)
    draw.rectangle([x, y, x + w, y + 4], fill=RED)


# ---------------------------------------------------------------- masthead
def draw_masthead(draw, y):
    f = fit_font(draw, "THE WORLD", SERIF_B, 72, CW)
    tw = draw.textlength("THE WORLD", font=f)
    draw.text(((W - tw) / 2, y), "THE WORLD", font=f, fill=INK)
    y += ink_bottom(draw, "THE WORLD", f) + 4
    dl = font(SANS_B, 14)
    left = "FRIDAY 20 NOVEMBER 2026"
    right = "ONE IMAGE · THE DAY'S NEWS"
    draw.text((MARGIN, y), left, font=dl, fill=INK)
    rw = draw.textlength(right, font=dl)
    draw.text((W - MARGIN - rw, y), right, font=dl, fill=INK)
    y += line_h(dl) + 4
    draw.rectangle([MARGIN, y, W - MARGIN, y + 3], fill=INK)
    y += 6
    draw.rectangle([MARGIN, y, W - MARGIN, y + 2], fill=RED)
    return y + 5


# ---------------------------------------------------------------- hero
def draw_hero(draw, y):
    x, w, pad = MARGIN, CW, 12
    head_txt = "MYANMAR GUILTY OF GENOCIDE"
    f_head = fit_font(draw, head_txt, SERIF_B, 44, w - 2 * pad)
    deck = rich_wrap(draw, [(
        "The International Court of Justice rules 9–6: Myanmar committed "
        "genocide against the Rohingya — the first time the court has held a "
        "state responsible for genocide. Case brought by The Gambia over the "
        "2017 campaign; refugees in Bangladesh cheered.", font(SANS, 16))],
        w - 2 * pad)
    lh = line_h(font(SANS, 16))
    head_bot = ink_bottom(draw, head_txt, f_head)
    h = 3 + 17 + 2 + head_bot + 3 + len(deck) * lh + 3
    section_box(draw, x, y, w, h, fill=PAPER)
    cy = y + 3
    cy = label(draw, x + pad, cy, "THE VERDICT  ·  THE HAGUE")
    draw.text((x + pad, cy), head_txt, font=f_head, fill=INK)
    cy += head_bot + 3
    draw_lines(draw, x + pad, cy, deck, lh)
    return y + h


# ---------------------------------------------------------------- summit
def draw_summit(draw, y):
    x, w, pad = MARGIN, CW, 12
    head_txt = "TRUMP, XI AND PUTIN MEET IN SHENZHEN"
    f_head = fit_font(draw, head_txt, SERIF_B, 31, w - 2 * pad)
    deck = rich_wrap(draw, [(
        "First three-way summit agrees a four-point peace declaration — nuclear "
        "risk reduction, UN reform, oil & gas supply and international courts — "
        "after ~70 minutes of closed talks. The Ukraine and Iran wars are not "
        "mentioned.", font(SANS, 16))], w - 2 * pad)
    lh = line_h(font(SANS, 16))
    head_bot = ink_bottom(draw, head_txt, f_head)
    h = 3 + 17 + 2 + head_bot + 2 + len(deck) * lh + 3
    section_box(draw, x, y, w, h, fill=PAPER)
    cy = y + 3
    cy = label(draw, x + pad, cy, "THE SUMMIT  ·  SHENZHEN")
    draw.text((x + pad, cy), head_txt, font=f_head, fill=INK)
    cy += head_bot + 2
    draw_lines(draw, x + pad, cy, deck, lh)
    return y + h


# ---------------------------------------------------------------- markets
def draw_markets(draw, y):
    x, w, pad = MARGIN, CW, 10
    inner = w - 2 * pad
    row_a = [
        ("S&P 500", "−2.02%", "7,175.83"),
        ("DOW", "−1,101 pts  (−2.19%)", "49,097.06 · first close below 50,000 since June"),
        ("NASDAQ", "−2.25%", "23,879.20"),
    ]
    row_b = [
        ("NIKKEI", "−4.68%", ""),
        ("KOSPI", "−4.74%", ""),
        ("VIX", "above 29", "highest since March"),
        ("GOLD", "$3,588.20/oz", "14-month low"),
        ("US 10-YR", "5.05%", ""),
        ("BRENT", "$89.72", ""),
    ]
    name_a, val_a, note_a = font(SANS_B, 12), font(SANS_B, 17), font(SANS, 11)
    name_b, val_b, note_b = font(SANS_B, 11), font(SANS_B, 14), font(SANS, 11)
    hf = font(SANS_B, 14)
    row_a_h = line_h(name_a) + line_h(val_a) + line_h(note_a) - 2
    row_b_h = line_h(name_b) + line_h(val_b) + line_h(note_b) - 2
    h = 4 + line_h(hf) + 3 + row_a_h + 5 + row_b_h + 4
    draw.rectangle([x, y, x + w, y + h], fill=DARK)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + 4], fill=RED)
    cy = y + 4
    draw.text((x + pad, cy), "MARKETS", font=hf, fill=RED)
    mw = draw.textlength("MARKETS ", font=hf)
    draw.text((x + pad + mw, cy), "—  GLOBAL SELL-OFF", font=hf, fill=CREAM_TXT)
    cy += line_h(hf) + 3
    cw_a = inner / 3
    for i, (name, val, note) in enumerate(row_a):
        cx = x + pad + i * cw_a
        draw.text((cx, cy), name, font=name_a, fill=MUTED_LT)
        draw.text((cx, cy + line_h(name_a) - 1), val, font=val_a, fill=CREAM_TXT)
        draw.text((cx, cy + line_h(name_a) + line_h(val_a) - 2), note,
                  font=note_a, fill=MUTED_LT)
        if i:
            draw.line([cx - 6, cy, cx - 6, cy + row_a_h - 4], fill=RULE_GREY)
    cy += row_a_h
    draw.line([x + pad, cy + 2, x + w - pad, cy + 2], fill=RULE_GREY)
    cy += 5
    cw_b = inner / 6
    for i, (name, val, note) in enumerate(row_b):
        cx = x + pad + i * cw_b
        draw.text((cx, cy), name, font=name_b, fill=MUTED_LT)
        draw.text((cx, cy + line_h(name_b) - 1), val, font=val_b, fill=CREAM_TXT)
        if note:
            draw.text((cx, cy + line_h(name_b) + line_h(val_b) - 2), note,
                      font=note_b, fill=MUTED_LT)
        if i:
            draw.line([cx - 5, cy, cx - 5, cy + row_b_h - 4], fill=RULE_GREY)
    return y + h


# ---------------------------------------------------------------- two-col
def draw_two_col(draw, y, left, right, body_size=14):
    x, w, gap, pad = MARGIN, CW, 10, 11
    col_w = (w - gap) / 2
    body_f = font(SANS, body_size)
    lh = line_h(body_f)
    cols = []
    for lab, head, body in (left, right):
        f_head = fit_font(draw, head, SERIF_B, 22, col_w - 2 * pad)
        lines = rich_wrap(draw, [(body, body_f)], col_w - 2 * pad)
        cols.append((lab, head, f_head, lines))
    n_lines = max(len(c[3]) for c in cols)
    head_adv = max(ink_bottom(draw, c[1], c[2]) for c in cols)
    h = 3 + 17 + 2 + head_adv + 2 + n_lines * lh + 3
    for i, (lab, head, f_head, lines) in enumerate(cols):
        cx = x + i * (col_w + gap)
        section_box(draw, cx, y, col_w, h, fill=PAPER)
        cy = y + 3
        cy = label(draw, cx + pad, cy, lab)
        draw.text((cx + pad, cy), head, font=f_head, fill=INK)
        cy += head_adv + 2
        draw_lines(draw, cx + pad, cy, lines, lh)
    return y + h


# ---------------------------------------------------------------- conflict
def draw_conflict(draw, y):
    x, w, pad = MARGIN, CW, 12
    items = [
        ("IRAN — ", "Hormuz tanker attacks escalate: a tanker hit a mine and "
         "caught fire. Senate rejects Iran war powers, 51–48."),
        ("RIYADH — ", "Houthi missile hits PIF Tower, Riyadh's tallest; "
         "windows broken, no injuries. Houthis claim 4 Saudi targets."),
        ("KERCH BRIDGE — ", "Ukraine hits the Crimean bridge a third time in "
         "four days; traffic halted, Putin vows a harsher response. Leaked "
         "data: 400,000–500,000 Russian deaths since 2022."),
    ]
    bold, reg = font(SANS_B, 14), font(SANS, 14)
    lh = line_h(reg)
    all_lines = []
    for lead, rest in items:
        all_lines.append(rich_wrap(draw, [(lead, bold), (rest, reg)],
                                   w - 2 * pad))
    n = sum(len(ls) for ls in all_lines)
    gaps = 1 * (len(items) - 1)
    h = 3 + 17 + 2 + n * lh + gaps + 3
    section_box(draw, x, y, w, h, fill=PAPER)
    cy = y + 3
    cy = label(draw, x + pad, cy, "CONFLICT")
    for ls in all_lines:
        cy = draw_lines(draw, x + pad, cy, ls, lh)
        cy += 1
    return y + h


# ---------------------------------------------------------------- briefs
def draw_briefs(draw, y):
    x, w, pad = MARGIN, CW, 12
    items = [
        ("VENDOR HACK — ", "JPMorgan, Visa, Mastercard confirm a vendor hack; "
         "names and emails exposed, no card numbers."),
        ("CYBER CHIEF OUT — ", "White House cyber director Sean Cairncross out; "
         "Pentagon CIO Kirsten Davies to replace him."),
        ("PETE ROSE — ", "Trump announces a posthumous pardon for baseball star "
         "Pete Rose."),
        ("APPLE ORDER — ", "A UK court forces admission of a secret encryption "
         "order against Apple."),
        ("GAZA — ", "Five aid groups rate peace-plan implementation 4 out of 26."),
        ("GREENLAND — ", "Denmark approves a Greenland defence deal, 109–0."),
        ("TAIWAN — ", "Five measures unveiled to steady stocks; Taiwan stocks "
         "down 5,248 points in three days."),
        ("APEC — ", "Leaders adopt the Shenzhen Outlook on trade, data and AI."),
    ]
    bold, reg = font(SANS_B, 12), font(SANS, 12)
    lh = line_h(reg)
    all_lines = []
    for lead, rest in items:
        ls = rich_wrap(draw, [(lead, bold), (rest, reg)], w - 2 * pad)
        assert len(ls) == 1, f"brief wraps to {len(ls)} lines: {lead}"
        all_lines.append(ls[0])
    sport = rich_wrap(draw, [
        ("SPORT — ", font(SANS_B, 13)),
        ("Thailand wins the AFC Diamond award as Asia's best football "
         "association, third year running; FIFA ranking 90th.",
         font(SANS, 13))], w - 2 * pad)
    sport_lh = line_h(font(SANS, 13))
    h = (3 + 17 + 2 + len(all_lines) * lh + 3 + 1 + 3
         + len(sport) * sport_lh + 3)
    section_box(draw, x, y, w, h, fill=PAPER)
    cy = y + 3
    cy = label(draw, x + pad, cy, "WORLD BRIEFS")
    for ln in all_lines:
        draw_line(draw, x + pad, cy, ln)
        cy += lh
    cy += 2
    draw.line([x + pad, cy, x + w - pad, cy], fill=RED, width=1)
    cy += 3
    draw_lines(draw, x + pad, cy, sport, sport_lh)
    return y + h


# ---------------------------------------------------------------- footer
def draw_footer(draw, y):
    f = font(SANS, 12)
    txt = ("Sources: BBC, UN News, The Guardian, Reuters, AFP  ·  "
           "All figures as reported 19–20 Nov 2026  ·  Built for make.fun")
    tw = draw.textlength(txt, font=f)
    draw.text(((W - tw) / 2, y), txt, font=f, fill=GREY)
    return y + line_h(f)


def build_poster(path):
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, W - 9, H - 9], outline=INK, width=2)
    y = 14
    y = draw_masthead(draw, y)
    y += GAP
    y = draw_hero(draw, y)
    y += GAP
    y = draw_summit(draw, y)
    y += GAP
    y = draw_markets(draw, y)
    y += GAP
    y = draw_two_col(draw, y,
        ("ANTHROPIC  ·  RECORD IPO", "RECORD IPO: $81.3 BILLION",
         "Anthropic priced at $83, raising ~$81.3 BILLION — the largest IPO in "
         "history. Shares opened ~$111.50 and closed ~$97.17 (+17%), briefly "
         "valuing the firm at ~$2 TRILLION. Nasdaq ticker: ANT."),
        ("DIPLOMACY  ·  BERLIN", "ALLIES UNITE ON RUSSIA TALKS",
         "European allies agree a united position for Russia talks. US envoy "
         "Kushner says Russia is comfortable with NATO Article 5-style "
         "guarantees for Ukraine; Zelenskyy is unsure both sides mean the "
         "same. Macron urges reopening NATO membership."))
    y += GAP
    y = draw_conflict(draw, y)
    y += GAP
    y = draw_two_col(draw, y,
        ("TECH", "NVIDIA PROBED AS CEO RESIGNS",
         "California's attorney general subpoenaed Nvidia over China chip "
         "disclosures; CEO Jensen Huang resigned amid reports of an affair "
         "with a suspected Chinese spy. Interim CEO: Colette Kress. AMD fell "
         "7–8% on a short-seller report on China ties."),
        ("CLIMATE  ·  COP31", "FINAL DAY IN ANTALYA",
         "Negotiators from ~200 countries struggle for consensus on "
         "fossil-fuel phase-out and climate finance on the final day "
         "(9–20 Nov) in Antalya, Türkiye — divided over the 1.5°C limit."))
    y += GAP
    y = draw_briefs(draw, y)
    y += GAP
    y = draw_footer(draw, y)
    print(f"final y: {y} (canvas {H})")
    assert y <= H - 8, f"layout overflow: final y {y} > {H - 8}"
    img.save(path, format="PNG")
    return path


if __name__ == "__main__":
    build_poster("/output/entry.png")

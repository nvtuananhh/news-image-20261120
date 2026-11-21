#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261120 round-3 poster.

Draws a 1024x1024 newspaper front page with Pillow. Runs only on this
build machine; the graded entrypoint (main.py) never imports it.
Deterministic: no clock, no randomness, fixed font sizes and layout.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 24
CONTENT_W = W - 2 * MARGIN

CREAM = (250, 244, 227)
PAPER = (255, 253, 245)
INK = (17, 17, 17)
RED = (185, 28, 28)
DARK = (20, 20, 20)
GREY = (90, 90, 86)
MUTED = (160, 158, 150)
LIGHT = (245, 240, 228)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = "DejaVuSerif-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that all fit max_w."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, name, size, max_w, min_size=9):
    """Largest font size (<= size) at which text fits on one line."""
    s = size
    while s > min_size:
        fnt = font(name, s)
        if text_w(draw, text, fnt) <= max_w:
            return fnt
        s -= 1
    fnt = font(name, min_size)
    assert text_w(draw, text, fnt) <= max_w, "line too long: %r" % text
    return fnt


def panel(draw, x, y, w, h, dark=False):
    fill = DARK if dark else PAPER
    draw.rectangle([x, y, x + w, y + h], fill=fill, outline=INK, width=1)
    draw.rectangle([x, y, x + w, y + 5], fill=RED)
    return y + 5


# ---------------------------------------------------------------- stories
# Story counts: hero 1, summit 1, markets 1, IPO 1, diplomacy 1,
# conflict 3, tech 1, climate 1, briefs 23, sport 3  =>  36 total.
BRIEFS = [
    # round-2 briefs (8)
    ("VENDOR HACK", "JPMorgan, Visa, Mastercard confirm a vendor hack; no card numbers."),
    ("CYBER CHIEF OUT", "White House cyber chief Cairncross out; Davies to replace him."),
    ("PETE ROSE", "Trump announces a posthumous pardon for baseball star Pete Rose."),
    ("APPLE ORDER", "A UK court forces admission of a secret encryption order against Apple."),
    ("GAZA", "Five aid groups rate peace-plan implementation 4 out of 26."),
    ("GREENLAND", "Denmark approves a Greenland defence deal, 109-0."),
    ("TAIWAN", "Five measures to steady stocks; Taiwan stocks down 5,248 pts in 3 days."),
    ("APEC", "Leaders adopt the Shenzhen Outlook on trade, data and AI."),
    # round-3 added briefs (14), each verified 20 Nov 2026 (see README)
    ("CYCLONE AKVAN", "Landfall near Gopalpur, India; winds 70-80 km/h, 300,000 evacuated."),
    ("KYIV BRIDGES", "Russian missiles hit 3 Dnipro bridges; 3 killed, about 15 hurt."),
    ("POLAND MISSILE", "Russian Kh-101 crashes in Poland; Tusk calls it a provocation."),
    ("UK-EU DEAL", "Food, youth mobility and carbon deals sealed in Brussels."),
    ("IRAN DECISION", "Trump says Iran strike decision can wait until after 1 Jan."),
    ("DENMARK PLOT", "Russia accused of plot to kill US-Ukrainian rapper; envoy expelled."),
    ("AI DATA CENTRES", "Trump threatens ban on US firms building AI centres abroad."),
    ("RIKERS", "Mamdani plans to close New York's Rikers Island jail by 2032."),
    ("ANC", "ANC fights to keep South Africa's big cities after election setback."),
    ("SA WOMEN", "Nearly 600 women killed in South Africa within three months."),
    ("S KOREA EXAM", "111 students caught cheating in South Korea's Suneung exam."),
    ("SIKH PLOT", "Indian man jailed 19+ years over plot to kill Sikh leader in US."),
    ("GTA 6", "Record launch: ~24.5m copies, est. $2.36bn in first-day sales."),
    ("RIEMANN", "Anthropic mathematician says AI proved Riemann; checks pending."),
    ("BUKELE", "El Salvador's Bukele registers to seek a third term in 2027."),
]

SPORT = [
    ("THAILAND", "Thailand wins the AFC Diamond award as Asia's best football association, third year running; FIFA ranking 90th."),
    ("ALCARAZ", "Alcaraz beats Cobolli 6-4, 6-1 at the ATP Finals in Turin; 3-0 in his group."),
    ("PRICE", "Lauren Price beats Kotaskova to become undisputed welterweight champion."),
]

CONFLICT = [
    ("IRAN", "Hormuz tanker attacks escalate: a tanker hit a mine and caught fire. Senate rejects Iran war powers, 51-48."),
    ("RIYADH", "Houthi missile hits PIF Tower, Riyadh's tallest; windows broken, no injuries. Houthis claim 4 Saudi targets."),
    ("KERCH BRIDGE", "Ukraine hits the Crimean bridge a third time in four days; traffic halted, Putin vows a harsher response. Leaked data: 400,000-500,000 Russian deaths since 2022."),
]

TOTAL_STORIES = 1 + 1 + 1 + 1 + 1 + 3 + 1 + 1 + len(BRIEFS) + len(SPORT)
assert TOTAL_STORIES == 36, TOTAL_STORIES


def build_poster():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=2)

    x0 = MARGIN
    y = 18

    # ---- masthead ----
    f_title = font(SERIF_B, 40)
    d.text((W / 2, y), "THE WORLD", font=f_title, fill=INK, anchor="ma")
    y += 50
    f_date = font(SANS_B, 15)
    d.text((x0, y), "FRIDAY 20 NOVEMBER 2026", font=f_date, fill=INK)
    right = "36 STORIES  \u00b7  7 REGIONS"
    d.text((W - x0, y), right, font=f_date, fill=RED, anchor="ra")
    y += 22
    d.rectangle([x0, y, W - x0, y + 3], fill=INK)
    y += 5
    d.rectangle([x0, y, W - x0, y + 1], fill=RED)
    y += 8

    def section_label(label, yy):
        fnt = font(SANS_B, 12)
        d.text((x0 + 10, yy), label, font=fnt, fill=RED)
        return yy + 17

    # ---- hero ----
    top = y
    panel(d, x0, top, CONTENT_W, 98)
    yy = section_label("THE VERDICT  \u00b7  THE HAGUE", top + 10)
    f_hero = font(SERIF_B, 30)
    d.text((x0 + 10, yy), "MYANMAR GUILTY OF GENOCIDE", font=f_hero, fill=INK)
    yy += 36
    f_deck = font(SANS, 13)
    deck = ("The International Court of Justice rules 9-6: Myanmar committed genocide "
            "against the Rohingya \u2014 the first time the court has held a state "
            "responsible for genocide. Case brought by The Gambia over the 2017 campaign; "
            "refugees in Bangladesh cheered.")
    lines = wrap(d, deck, f_deck, CONTENT_W - 20)
    assert len(lines) == 2, lines
    for ln in lines:
        d.text((x0 + 10, yy), ln, font=f_deck, fill=INK)
        yy += 17
    y = top + 98 + 6

    # ---- summit ----
    top = y
    panel(d, x0, top, CONTENT_W, 88)
    yy = section_label("THE SUMMIT  \u00b7  SHENZHEN", top + 11)
    f_sum = font(SERIF_B, 23)
    d.text((x0 + 10, yy), "TRUMP, XI AND PUTIN MEET IN SHENZHEN", font=f_sum, fill=INK)
    yy += 29
    deck = ("First three-way summit agrees a four-point peace declaration \u2014 nuclear risk "
            "reduction, UN reform, oil & gas supply and international courts \u2014 after "
            "~70 minutes of closed talks. The Ukraine and Iran wars are not mentioned.")
    lines = wrap(d, deck, f_deck, CONTENT_W - 20)
    assert len(lines) == 2, lines
    for ln in lines:
        d.text((x0 + 10, yy), ln, font=f_deck, fill=INK)
        yy += 17
    y = top + 88 + 6

    # ---- markets (dark) ----
    top = y
    panel(d, x0, top, CONTENT_W, 96, dark=True)
    yy = top + 11
    f_mh = font(SANS_B, 15)
    d.text((x0 + 10, yy), "MARKETS", font=f_mh, fill=(255, 90, 80))
    w_mk = text_w(d, "MARKETS ", f_mh)
    d.text((x0 + 10 + w_mk, yy), "\u2014 GLOBAL SELL-OFF", font=f_mh, fill=LIGHT)
    yy += 22

    def ticker(cx, name, value, note, fnt_n, fnt_v, fnt_no):
        d.text((cx, yy), name, font=fnt_n, fill=MUTED)
        nw = text_w(d, name + " ", fnt_n)
        d.text((cx + nw, yy), value, font=fnt_v, fill=LIGHT)
        if note:
            d.text((cx, yy + 17), note, font=fnt_no, fill=MUTED)

    f_tn = font(SANS_B, 12)
    f_tv = font(SANS_B, 14)
    f_tno = font(SANS, 10)
    row1 = [("S&P 500", "\u22122.02%", "7,175.83"),
            ("DOW", "\u22121,101 pts (\u22122.19%)", "49,097.06 \u00b7 first close below 50,000 since June"),
            ("NASDAQ", "\u22122.25%", "23,879.20")]
    cw1 = CONTENT_W // 3
    for i, (nm, val, note) in enumerate(row1):
        ticker(x0 + 10 + i * cw1, nm, val, note, f_tn, f_tv, f_tno)
    yy += 30
    row2 = [("NIKKEI", "\u22124.68%", ""), ("KOSPI", "\u22124.74%", ""),
            ("VIX", "above 29", "highest since March"),
            ("GOLD", "$3,588.20/oz", "14-month low"),
            ("US 10-YR", "5.05%", ""), ("BRENT", "$89.72", "")]
    cw2 = CONTENT_W // 6
    f_tn2 = font(SANS_B, 11)
    f_tv2 = font(SANS_B, 12)
    for i, (nm, val, note) in enumerate(row2):
        ticker(x0 + 10 + i * cw2, nm, val, note, f_tn2, f_tv2, f_tno)
    y = top + 96 + 6

    # ---- two-column panels ----
    def two_col(top, height, left, right):
        panel(d, x0, top, 482, height)
        panel(d, x0 + 494, top, 482, height)
        for px, (label, head, body) in ((x0, left), (x0 + 494, right)):
            d.text((px + 10, top + 11), label, font=font(SANS_B, 12), fill=RED)
            f_h = font(SERIF_B, 19)
            hl = wrap(d, head, f_h, 462)
            assert len(hl) == 1, hl
            d.text((px + 10, top + 28), hl[0], font=f_h, fill=INK)
            f_b = font(SANS, 12)
            bl = wrap(d, body, f_b, 462)
            assert len(bl) <= 4, bl
            yy2 = top + 48
            for ln in bl:
                d.text((px + 10, yy2), ln, font=f_b, fill=INK)
                yy2 += 14
        return top + height + 6

    y = two_col(y, 108, (
        "ANTHROPIC  \u00b7  RECORD IPO",
        "RECORD IPO: $81.3 BILLION",
        "Anthropic priced at $83, raising ~$81.3 BILLION \u2014 the largest IPO in history. "
        "Shares opened ~$111.50 and closed ~$97.17 (+17%), briefly valuing the firm at "
        "~$2 TRILLION. Nasdaq ticker: ANT."),
        ("DIPLOMACY  \u00b7  BERLIN",
         "ALLIES UNITE ON RUSSIA TALKS",
         "European allies agree a united position for Russia talks. US envoy Kushner says "
         "Russia is comfortable with NATO Article 5-style guarantees for Ukraine; Zelenskyy "
         "is unsure both sides mean the same. Macron urges reopening NATO membership."))

    # ---- conflict ----
    top = y
    panel(d, x0, top, CONTENT_W, 74)
    yy = section_label("CONFLICT", top + 11)
    for lead, rest in CONFLICT:
        lead_txt = lead + " \u2014 "
        full = lead_txt + rest
        fnt = fit_font(d, full, SANS, 12, CONTENT_W - 20, min_size=10)
        d.text((x0 + 10, yy), lead_txt, font=font(SANS_B, fnt.size), fill=INK)
        lw = text_w(d, lead_txt, font(SANS_B, fnt.size))
        d.text((x0 + 10 + lw, yy), rest, font=fnt, fill=INK)
        yy += 16
    y = top + 74 + 6

    # ---- two-column B ----
    y = two_col(y, 108, (
        "TECH",
        "NVIDIA PROBED AS CEO RESIGNS",
        "California's attorney general subpoenaed Nvidia over China chip disclosures; CEO "
        "Jensen Huang resigned amid reports of an affair with a suspected Chinese spy. "
        "Interim CEO: Colette Kress."),
        ("CLIMATE  \u00b7  COP31",
         "FINAL DAY IN ANTALYA",
         "Negotiators from ~200 countries struggle for consensus on fossil-fuel phase-out "
         "and climate finance on the final day (9-20 Nov) in Antalya, T\u00fcrkiye \u2014 "
         "divided over the 1.5\u00b0C limit."))

    # ---- world briefs: 23 one-liners, two columns ----
    top = y
    n_rows = (len(BRIEFS) + 1) // 2
    brief_h = 20 + n_rows * 14 + 7
    panel(d, x0, top, CONTENT_W, brief_h)
    section_label("WORLD BRIEFS  \u00b7  23 MORE STORIES", top + 11)
    col_w = (CONTENT_W - 20) // 2
    for i, (label, text) in enumerate(BRIEFS):
        col = i % 2
        row = i // 2
        bx = x0 + 10 + col * (col_w + 4)
        by = top + 26 + row * 14
        full = label + " \u2014 " + text
        fnt = fit_font(d, full, SANS, 12, col_w - 4, min_size=10)
        d.text((bx, by), label + " \u2014 ", font=font(SANS_B, fnt.size), fill=RED)
        lw = text_w(d, label + " \u2014 ", font(SANS_B, fnt.size))
        d.text((bx + lw, by), text, font=fnt, fill=INK)
    y = top + brief_h + 6

    # ---- sport: 3 one-liners ----
    top = y
    sport_h = 12 + len(SPORT) * 13 + 8
    panel(d, x0, top, CONTENT_W, sport_h)
    section_label("SPORT", top + 9)
    for i, (label, text) in enumerate(SPORT):
        by = top + 21 + i * 13
        full = label + " \u2014 " + text
        fnt = fit_font(d, full, SANS, 12, CONTENT_W - 20, min_size=10)
        d.text((x0 + 10, by), label + " \u2014 ", font=font(SANS_B, fnt.size), fill=RED)
        lw = text_w(d, label + " \u2014 ", font(SANS_B, fnt.size))
        d.text((x0 + 10 + lw, by), text, font=fnt, fill=INK)
    y = top + sport_h + 6

    # ---- footer ----
    f_f = font(SANS, 10)
    d.text((W / 2, y), "Sources: BBC, UN News, The Guardian, Reuters, AFP  \u00b7  "
                       "All figures as reported 19-20 Nov 2026  \u00b7  Built for make.fun",
           font=f_f, fill=GREY, anchor="ma")
    y += 16
    assert y <= H - 14, "layout overflow: bottom y=%d" % y
    return img


def main():
    img = build_poster()
    assert img.size == (1024, 1024)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "poster.png")
    img.save(out, format="PNG")
    print("wrote %s (%d bytes, %d stories)" % (out, os.path.getsize(out), TOTAL_STORIES))


if __name__ == "__main__":
    main()

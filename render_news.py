#!/usr/bin/env python3
"""Draw the front page of THE WORLD TODAY for Wednesday 25 November 2026.

A single 1024x1024 newspaper front page summarising the day's world news.
Everything is drawn from scratch with Pillow: masthead, headlines,
standfirsts, small pictorial panels and an In Brief strip.

Run:  python3 render_news.py            # writes entry.png next to this file
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (246, 241, 227)      # warm newsprint
INK = (26, 26, 26)
FAINT = (90, 84, 70)
RED = (163, 22, 33)
NAVY = (20, 33, 61)
NAVY_LT = (38, 58, 96)
GOLD = (201, 162, 39)
SKY = (126, 178, 214)
RULE = (60, 56, 48)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w, draw):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, leading, fill=INK):
    """Draw wrapped paragraph; returns y after the last line."""
    for line in wrap(text, fnt, max_w, draw):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def kicker(draw, x, y, text, size=15):
    fnt = font(SANS_B, size)
    draw.text((x, y), text, font=fnt, fill=RED)
    return y + size + 6


def headline(draw, x, y, text, size, max_w, leading=None):
    fnt = font(SERIF_B, size)
    leading = leading or int(size * 1.08)
    for line in wrap(text, fnt, max_w, draw):
        draw.text((x, y), line, font=fnt, fill=INK)
        y += leading
    return y


def rule(draw, x0, x1, y, width=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_globe(draw, cx, cy, r):
    """Small line globe: circle, meridians, parallels."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=3)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=NAVY, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=NAVY, width=2)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 360, fill=NAVY, width=2)
    draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=RED, width=3)


def draw_lock_panel(draw, x, y, w, h):
    """Lead illustration: night-blue panel, caption, nodes, padlock."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    draw.text((x + 12, y + 8), "UNCLASSIFIED NETWORK BREACHED",
              font=font(SANS_B, 12), fill=(220, 226, 238))
    # padlock, centred in the space below the caption
    cx, cy = x + w // 2, y + h // 2 + 14
    draw.arc([cx - 30, cy - 40, cx + 30, cy + 4], 180, 360, fill=GOLD, width=8)
    draw.rounded_rectangle([cx - 40, cy - 6, cx + 40, cy + 40],
                           radius=7, fill=GOLD)
    draw.ellipse([cx - 7, cy + 8, cx + 7, cy + 22], fill=NAVY)
    draw.rectangle([cx - 3, cy + 18, cx + 3, cy + 30], fill=NAVY)


def draw_ship_panel(draw, x, y, w, h):
    """Cargo ship on waves: sky, containers, hull, sea."""
    draw.rectangle([x, y, x + w, y + h], fill=(214, 228, 238))
    # containers
    cols = [(178, 52, 44), (201, 162, 39), (58, 96, 128), (178, 52, 44)]
    cw = (w - 120) // 4
    for i, col in enumerate(cols):
        cx0 = x + 62 + i * cw
        draw.rectangle([cx0, y + 14, cx0 + cw - 4, y + 34], fill=col)
    # funnel + mast
    draw.rectangle([x + w - 78, y + 8, x + w - 58, y + 34], fill=INK)
    draw.rectangle([x + 44, y + 4, x + 48, y + 34], fill=INK)
    draw.polygon([(x + 48, y + 6), (x + 74, y + 12), (x + 48, y + 18)], fill=RED)
    # hull
    draw.polygon([(x + 40, y + 34), (x + w - 30, y + 34), (x + w - 56, y + h - 16),
                  (x + 66, y + h - 16)], fill=(122, 32, 28))
    # sea
    draw.rectangle([x, y + h - 16, x + w, y + h], fill=(58, 96, 128))
    for wx in range(x + 6, x + w - 6, 44):
        draw.arc([wx, y + h - 22, wx + 28, y + h - 6], 0, 180,
                 fill=(240, 244, 248), width=3)


def draw_tower_panel(draw, x, y, w, h):
    """Riyadh tower at night with a small drone dot and smoke."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 28, 44))
    for sx in range(x + 10, x + w, 26):
        draw.ellipse([sx, y + 6 + (sx % 3) * 4, sx + 2, y + 8 + (sx % 3) * 4],
                     fill=(240, 240, 240))
    # tower with setbacks
    tx = x + w // 2
    draw.polygon([(tx - 52, y + h), (tx - 52, y + 28), (tx - 30, y + 12),
                  (tx + 30, y + 12), (tx + 52, y + 28), (tx + 52, y + h)],
                 fill=(96, 110, 138))
    for wy in range(y + 20, y + h - 6, 11):
        draw.line([(tx - 44, wy), (tx + 44, wy)], fill=GOLD, width=2)
    draw.line([(tx, y + 12), (tx, y + 28)], fill=GOLD, width=3)
    # drone + smoke wisp
    draw.ellipse([tx + 84, y + 14, tx + 92, y + 22], fill=RED)
    draw.arc([tx + 60, y + 6, tx + 96, y + 32], 300, 60, fill=(200, 200, 200), width=3)
    draw.rectangle([x, y + h - 6, x + w, y + h], fill=(58, 62, 78))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx, mx2 = 36, W - 36  # margins

    # ---- dateline bar -------------------------------------------------
    d.text((mx, 14), "WEDNESDAY 25 NOVEMBER 2026",
           font=font(SANS_B, 16), fill=INK)
    right = "THE WORLD IN ONE PAGE"
    d.text((mx2 - d.textlength(right, font=font(SANS_B, 16)), 14), right,
           font=font(SANS_B, 16), fill=INK)
    rule(d, mx, mx2, 40)

    # ---- masthead ------------------------------------------------------
    title = "THE WORLD TODAY"
    tf = font(SERIF_B, 80)
    tw = d.textlength(title, font=tf)
    tx = (W - tw) / 2
    draw_globe(d, int(tx) - 50, 92, 25)
    draw_globe(d, int(tx + tw) + 50, 92, 25)
    d.text((tx, 48), title, font=tf, fill=INK)
    tag = "S U M M I N G   U P   T H E   D A Y ' S   W O R L D   N E W S"
    tg = font(SANS, 15)
    d.text(((W - d.textlength(tag, font=tg)) / 2, 136), tag, font=tg, fill=FAINT)
    rule(d, mx, mx2, 160, width=3)
    rule(d, mx, mx2, 165, width=1)

    # ---- kicker strip ---------------------------------------------------
    note = "ALSO TODAY  •  INTERNATIONAL DAY FOR THE ELIMINATION OF VIOLENCE AGAINST WOMEN"
    nf = font(SANS_B, 14)
    d.text(((W - d.textlength(note, font=nf)) / 2, 176), note, font=nf, fill=RED)

    # ---- lead story + Huawei (row 1, y 200-506) -------------------------
    y = 200
    lx, lw = mx, 596          # lead column
    rx, rw = 668, W - 36 - 668  # right column (320 wide)

    yy = kicker(d, lx, y, "CYBERSECURITY  •  WASHINGTON")
    yy = headline(d, lx, yy, "Hackers breach the CIA and the spy chief's open-source network",
                  42, lw, leading=46)
    yy += 6
    para(d, lx, yy,
         "Intruders broke into an unclassified system the CIA and the Office "
         "of the Director of National Intelligence use to analyse public "
         "material. Officials say no classified information was affected — "
         "but who did it, and what was taken, is not known.",
         font(SERIF, 18), lw, 25)

    draw_lock_panel(d, rx, y, rw, 120)
    yy = kicker(d, rx, y + 130, "TECH  •  NEW YORK")
    yy = headline(d, rx, yy, "Huawei guilty of stealing trade secrets",
                  28, rw, leading=31)
    yy += 4
    para(d, rx, yy,
         "A Brooklyn jury convicted the Chinese telecoms giant on 10 of 12 "
         "counts, including bank fraud. It cleared Huawei of the top "
         "racketeering charge.",
         font(SERIF, 14), rw, 19)

    rule(d, mx, mx2, 506, width=2)

    # ---- middle row: ship + tower (row 2, y 522-734) --------------------
    y = 522
    cw = (mx2 - mx - 24) // 2  # 464
    c1x, c2x = mx, mx + cw + 24

    draw_ship_panel(d, c1x, y, cw, 72)
    yy = kicker(d, c1x, y + 82, "WAR IN UKRAINE  •  KYIV")
    yy = headline(d, c1x, yy,
                  "Zelenskyy: Ukraine struck the Russian ship in the Gulf of Finland",
                  26, cw, leading=29)
    yy += 4
    para(d, c1x, yy,
         "Kyiv confirmed it was behind Saturday's drone strike on the cargo "
         "ship Sparta II. Ally Norway urged caution.",
         font(SERIF, 15), cw, 20)

    draw_tower_panel(d, c2x, y, cw, 72)
    yy = kicker(d, c2x, y + 82, "MIDDLE EAST  •  RIYADH")
    yy = headline(d, c2x, yy, "Houthi drone hits Riyadh's tallest tower; 11 wounded",
                  26, cw, leading=29)
    yy += 4
    para(d, c2x, yy,
         "The strike hit the 385-metre Public Investment Fund tower, the Saudi "
         "capital's tallest building, for the second time in less than a week.",
         font(SERIF, 15), cw, 20)

    rule(d, mx, mx2, 734, width=2)

    # ---- bottom row: Giuliani + Anthropic (row 3, y 748-884) ------------
    y = 748
    yy = kicker(d, c1x, y, "UNITED STATES  •  WASHINGTON")
    yy = headline(d, c1x, yy, "Trump gives Giuliani the Medal of Freedom",
                  25, cw, leading=28)
    yy += 3
    para(d, c1x, yy,
         "The president awarded the nation's highest civilian honour to his "
         "longtime ally, the former New York mayor, at the White House.",
         font(SERIF, 15), cw, 20)

    yy = kicker(d, c2x, y, "MARKETS  •  NEW YORK")
    yy = headline(d, c2x, yy, "Anthropic shares slide below their $83 IPO price",
                  25, cw, leading=28)
    yy += 3
    para(d, c2x, yy,
         "The Claude maker's stock fell as much as 12% on Tuesday, days after "
         "its record Nasdaq debut, on track to shed nearly $200bn in value.",
         font(SERIF, 15), cw, 20)

    # ---- In Brief strip (y 876-988) --------------------------------------
    by = 876
    d.rectangle([mx, by, mx2, 988], fill=NAVY)
    d.text((mx + 16, by + 10), "IN BRIEF", font=font(SANS_B, 17), fill=GOLD)
    d.line([(mx + 16, by + 36), (mx2 - 16, by + 36)], fill=NAVY_LT, width=1)
    briefs = [
        "WHO evacuates health workers from an Ebola hospital in eastern Congo after three days sheltering from fighting.",
        "Trump pardons Thanksgiving turkeys Freedom and Feathers at the White House.",
        "Sarkozy corruption case — ex-president and wife Carla Bruni — ordered to trial in France.",
        "Swedish parliament votes on whether Kristersson stays PM.",
    ]
    col_w = (mx2 - mx - 32 - 24) // 2
    bx = [mx + 16, mx + 16 + col_w + 24]
    byy = [by + 44, by + 44]
    for i, item in enumerate(briefs):
        col = i % 2
        x = bx[col]
        yb = byy[col]
        d.text((x, yb), "•", font=font(SANS_B, 13), fill=GOLD)
        yb = para(d, x + 14, yb, item, font(SANS, 13), col_w - 14, 16,
                  fill=(232, 236, 244))
        byy[col] = yb + 4

    # ---- footer ------------------------------------------------------------
    foot = "Compiled from Reuters, AP, CNN, Bloomberg, The New York Times and Sky News  •  Wednesday 25 November 2026"
    ff = font(SANS, 13)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 996), foot, font=ff, fill=FAINT)

    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT}: {W}x{H}, {size} bytes")
    return OUT


if __name__ == "__main__":
    build()

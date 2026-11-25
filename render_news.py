#!/usr/bin/env python3
"""Render THE WORLD TODAY — the front page for Wednesday 25 November 2026.

Draws a 1024x1024 newspaper front page from scratch with Pillow: masthead,
six lead stories with small pictorial panels, and an In Brief strip. All text
is set in the file; nothing is fetched. The picture is deterministic — the
same code always writes the same bytes.

Run:  python3 render_news.py        # writes entry.png beside this file
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(ROOT, "entry.png")

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 36

# Newsprint palette.
PAPER = (246, 241, 227)
INK = (26, 26, 26)
MUTED = (90, 84, 70)
RULE_INK = (60, 56, 48)
SIGNAL = (163, 22, 33)
NAVY = (20, 33, 61)
NAVY_FADE = (38, 58, 96)
GOLD = (201, 162, 39)
SKY = (126, 178, 214)
SEA = (58, 96, 128)
HULL = (122, 32, 28)
NIGHT = (24, 28, 44)
CLOUD = (214, 228, 238)
PANEL_TEXT = (220, 226, 238)
BRIEF_TEXT = (232, 236, 244)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


class Typesetter:
    """Wraps an ImageDraw with a font cache and helpers that set wrapped
    blocks of type and report the y position after the block."""

    def __init__(self, draw):
        self.d = draw
        self._cache = {}

    def face(self, path, size):
        key = (path, size)
        if key not in self._cache:
            self._cache[key] = ImageFont.truetype(path, size)
        return self._cache[key]

    def measure(self, text, path, size):
        return self.d.textlength(text, font=self.face(path, size))

    def wrapped(self, text, path, size, max_width):
        """Greedy word wrap; every returned line fits inside max_width."""
        fnt = self.face(path, size)
        lines, current = [], ""
        for word in text.split():
            trial = (current + " " + word).strip()
            if self.d.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def block(self, x, y, text, path, size, max_width, leading, fill=INK):
        """Set a wrapped paragraph; returns the y after its last line."""
        for line in self.wrapped(text, path, size, max_width):
            self.d.text((x, y), line, font=self.face(path, size), fill=fill)
            y += leading
        return y

    def heading(self, x, y, text, size, max_width, leading=None, fill=INK):
        """Set a bold serif headline; returns the y after its last line."""
        if leading is None:
            leading = int(size * 1.08)
        return self.block(x, y, text, SERIF_BOLD, size, max_width, leading, fill)

    def kicker(self, x, y, text, size=15):
        """Set a small red section label; returns the y below it."""
        self.d.text((x, y), text, font=self.face(SANS_BOLD, size), fill=SIGNAL)
        return y + size + 6

    def hline(self, x0, x1, y, width=2, fill=RULE_INK):
        self.d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- pictures

def globe(ts, cx, cy, r):
    """Small line globe: circle, meridians, parallels, one red arc."""
    d = ts.d
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=3)
    d.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=NAVY, width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=NAVY, width=2)
    d.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 360, fill=NAVY, width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=SIGNAL, width=3)


def lock_panel(ts, x, y, w, h):
    """Lead illustration: night-blue panel, caption, padlock."""
    d = ts.d
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.text((x + 12, y + 8), "UNCLASSIFIED NETWORK BREACHED",
           font=ts.face(SANS_BOLD, 12), fill=PANEL_TEXT)
    cx, cy = x + w // 2, y + h // 2 + 14
    d.arc([cx - 30, cy - 40, cx + 30, cy + 4], 180, 360, fill=GOLD, width=8)
    d.rounded_rectangle([cx - 40, cy - 6, cx + 40, cy + 40],
                        radius=7, fill=GOLD)
    d.ellipse([cx - 7, cy + 8, cx + 7, cy + 22], fill=NAVY)
    d.rectangle([cx - 3, cy + 18, cx + 3, cy + 30], fill=NAVY)


def ship_panel(ts, x, y, w, h):
    """Cargo ship on waves: sky, containers, hull, sea."""
    d = ts.d
    d.rectangle([x, y, x + w, y + h], fill=CLOUD)
    cols = [(178, 52, 44), GOLD, SEA, (178, 52, 44)]
    cw = (w - 120) // 4
    for i, col in enumerate(cols):
        cx0 = x + 62 + i * cw
        d.rectangle([cx0, y + 14, cx0 + cw - 4, y + 34], fill=col)
    d.rectangle([x + w - 78, y + 8, x + w - 58, y + 34], fill=INK)
    d.rectangle([x + 44, y + 4, x + 48, y + 34], fill=INK)
    d.polygon([(x + 48, y + 6), (x + 74, y + 12), (x + 48, y + 18)], fill=SIGNAL)
    d.polygon([(x + 40, y + 34), (x + w - 30, y + 34), (x + w - 56, y + h - 16),
               (x + 66, y + h - 16)], fill=HULL)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=SEA)
    for wx in range(x + 6, x + w - 6, 44):
        d.arc([wx, y + h - 22, wx + 28, y + h - 6], 0, 180,
              fill=(240, 244, 248), width=3)


def tower_panel(ts, x, y, w, h):
    """Riyadh tower at night with a small drone dot and smoke."""
    d = ts.d
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    for sx in range(x + 10, x + w, 26):
        d.ellipse([sx, y + 6 + (sx % 3) * 4, sx + 2, y + 8 + (sx % 3) * 4],
                  fill=(240, 240, 240))
    tx = x + w // 2
    d.polygon([(tx - 52, y + h), (tx - 52, y + 28), (tx - 30, y + 12),
               (tx + 30, y + 12), (tx + 52, y + 28), (tx + 52, y + h)],
              fill=(96, 110, 138))
    for wy in range(y + 20, y + h - 6, 11):
        d.line([(tx - 44, wy), (tx + 44, wy)], fill=GOLD, width=2)
    d.line([(tx, y + 12), (tx, y + 28)], fill=GOLD, width=3)
    d.ellipse([tx + 84, y + 14, tx + 92, y + 22], fill=SIGNAL)
    d.arc([tx + 60, y + 6, tx + 96, y + 32], 300, 60, fill=(200, 200, 200), width=3)
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(58, 62, 78))


# ------------------------------------------------------------------- stories

STORIES = [
    {
        "kicker": "CYBERSECURITY  •  WASHINGTON",
        "headline": "Hackers breach the CIA and the spy chief's open-source network",
        "body": "Intruders broke into an unclassified system the CIA and the "
                "Office of the Director of National Intelligence use to analyse "
                "public material. Officials say no classified information was "
                "affected — but who did it, and what was taken, is not known.",
        "headline_size": 42,
        "headline_leading": 46,
        "body_size": 18,
        "body_leading": 25,
        "gap": 6,
    },
    {
        "kicker": "TECH  •  NEW YORK",
        "headline": "Huawei guilty of stealing trade secrets",
        "body": "A Brooklyn jury convicted the Chinese telecoms giant on 10 of "
                "12 counts, including bank fraud. It cleared Huawei of the top "
                "racketeering charge.",
        "headline_size": 28,
        "headline_leading": 31,
        "body_size": 14,
        "body_leading": 19,
        "gap": 4,
    },
    {
        "kicker": "WAR IN UKRAINE  •  KYIV",
        "headline": "Zelenskyy: Ukraine struck the Russian ship in the Gulf of Finland",
        "body": "Kyiv confirmed it was behind Saturday's drone strike on the "
                "cargo ship Sparta II. Ally Norway urged caution.",
        "headline_size": 26,
        "headline_leading": 29,
        "body_size": 15,
        "body_leading": 20,
        "gap": 4,
    },
    {
        "kicker": "MIDDLE EAST  •  RIYADH",
        "headline": "Houthi drone hits Riyadh's tallest tower; 11 wounded",
        "body": "The strike hit the 385-metre Public Investment Fund tower, the "
                "Saudi capital's tallest building, for the second time in less "
                "than a week.",
        "headline_size": 26,
        "headline_leading": 29,
        "body_size": 15,
        "body_leading": 20,
        "gap": 4,
    },
    {
        "kicker": "UNITED STATES  •  WASHINGTON",
        "headline": "Trump gives Giuliani the Medal of Freedom",
        "body": "The president awarded the nation's highest civilian honour to "
                "his longtime ally, the former New York mayor, at the White House.",
        "headline_size": 25,
        "headline_leading": 28,
        "body_size": 15,
        "body_leading": 20,
        "gap": 3,
    },
    {
        "kicker": "MARKETS  •  NEW YORK",
        "headline": "Anthropic shares slide below their $83 IPO price",
        "body": "The Claude maker's stock fell as much as 12% on Tuesday, days "
                "after its record Nasdaq debut, on track to shed nearly $200bn "
                "in value.",
        "headline_size": 25,
        "headline_leading": 28,
        "body_size": 15,
        "body_leading": 20,
        "gap": 3,
    },
]

BRIEFS = [
    "WHO evacuates health workers from an Ebola hospital in eastern Congo after three days sheltering from fighting.",
    "Trump pardons Thanksgiving turkeys Freedom and Feathers at the White House.",
    "Sarkozy corruption case — ex-president and wife Carla Bruni — ordered to trial in France.",
    "Swedish parliament votes on whether Kristersson stays PM.",
]

FOOTER = ("Compiled from Reuters, AP, CNN, Bloomberg, The New York Times and "
          "Sky News  •  Wednesday 25 November 2026")


def story(ts, x, y, width, item):
    """Set one story (kicker, headline, body) at x, y; returns the y after
    the body, with the story's own gap already added."""
    y = ts.kicker(x, y, item["kicker"])
    y = ts.heading(x, y, item["headline"], item["headline_size"], width,
                   leading=item["headline_leading"])
    y += item["gap"]
    y = ts.block(x, y, item["body"], SERIF, item["body_size"], width,
                 item["body_leading"])
    return y


def verify_saved(path):
    """Re-open the written PNG and confirm it is the whole 1024x1024 image
    the entry promises, so a truncated or mistyped save fails loudly."""
    with Image.open(path) as check:
        check.load()
        if check.size != (PAGE_W, PAGE_H) or check.format != "PNG":
            raise SystemExit(f"bad output {path}: {check.format} {check.size}")
    if os.path.getsize(path) > 1048576:
        raise SystemExit(f"output {path} is over the 1 MiB limit")


def compose():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    ts = Typesetter(ImageDraw.Draw(img))
    d = ts.d
    left, right = MARGIN, PAGE_W - MARGIN

    # Dateline bar.
    d.text((left, 14), "WEDNESDAY 25 NOVEMBER 2026",
           font=ts.face(SANS_BOLD, 16), fill=INK)
    flag = "THE WORLD IN ONE PAGE"
    d.text((right - ts.measure(flag, SANS_BOLD, 16), 14), flag,
           font=ts.face(SANS_BOLD, 16), fill=INK)
    ts.hline(left, right, 40)

    # Masthead.
    title = "THE WORLD TODAY"
    title_font = ts.face(SERIF_BOLD, 80)
    title_w = d.textlength(title, font=title_font)
    title_x = (PAGE_W - title_w) / 2
    globe(ts, int(title_x) - 50, 92, 25)
    globe(ts, int(title_x + title_w) + 50, 92, 25)
    d.text((title_x, 48), title, font=title_font, fill=INK)
    tag = "S U M M I N G   U P   T H E   D A Y ' S   W O R L D   N E W S"
    tag_font = ts.face(SANS, 15)
    d.text(((PAGE_W - d.textlength(tag, font=tag_font)) / 2, 136), tag,
           font=tag_font, fill=MUTED)
    ts.hline(left, right, 160, width=3)
    ts.hline(left, right, 165, width=1)

    # Notice strip.
    note = ("ALSO TODAY  •  INTERNATIONAL DAY FOR THE ELIMINATION OF "
            "VIOLENCE AGAINST WOMEN")
    note_font = ts.face(SANS_BOLD, 14)
    d.text(((PAGE_W - d.textlength(note, font=note_font)) / 2, 176), note,
           font=note_font, fill=SIGNAL)

    # Row one: lead story left, lock panel + Huawei right.
    y = 200
    lead_w = 596
    side_x, side_w = 668, PAGE_W - MARGIN - 668
    end_lead = story(ts, left, y, lead_w, STORIES[0])
    if end_lead > 500:
        raise SystemExit(f"lead story overflows its row (ends at y={end_lead})")
    lock_panel(ts, side_x, y, side_w, 120)
    story(ts, side_x, y + 130, side_w, STORIES[1])
    ts.hline(left, right, 506, width=2)

    # Row two: ship and tower.
    y = 522
    col_w = (right - left - 24) // 2
    col2_x = left + col_w + 24
    ship_panel(ts, left, y, col_w, 72)
    story(ts, left, y + 82, col_w, STORIES[2])
    tower_panel(ts, col2_x, y, col_w, 72)
    story(ts, col2_x, y + 82, col_w, STORIES[3])
    ts.hline(left, right, 734, width=2)

    # Row three: Giuliani and Anthropic.
    y = 748
    story(ts, left, y, col_w, STORIES[4])
    story(ts, col2_x, y, col_w, STORIES[5])

    # In Brief strip.
    top = 876
    d.rectangle([left, top, right, 988], fill=NAVY)
    d.text((left + 16, top + 10), "IN BRIEF", font=ts.face(SANS_BOLD, 17), fill=GOLD)
    d.line([(left + 16, top + 36), (right - 16, top + 36)], fill=NAVY_FADE, width=1)
    brief_w = (right - left - 32 - 24) // 2
    col_x = [left + 16, left + 16 + brief_w + 24]
    col_y = [top + 44, top + 44]
    for i, item in enumerate(BRIEFS):
        col = i % 2
        x = col_x[col]
        yb = col_y[col]
        d.text((x, yb), "•", font=ts.face(SANS_BOLD, 13), fill=GOLD)
        yb = ts.block(x + 14, yb, item, SANS, 13, brief_w - 14, 16,
                      fill=BRIEF_TEXT)
        col_y[col] = yb + 4

    # Footer.
    foot_font = ts.face(SANS, 13)
    d.text(((PAGE_W - d.textlength(FOOTER, font=foot_font)) / 2, 996), FOOTER,
           font=foot_font, fill=MUTED)

    img.save(TARGET, "PNG", optimize=True)
    verify_saved(TARGET)
    size = os.path.getsize(TARGET)
    print(f"wrote {TARGET}: {PAGE_W}x{PAGE_H}, {size} bytes")
    return TARGET


if __name__ == "__main__":
    compose()

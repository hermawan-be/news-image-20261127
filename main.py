#!/usr/bin/env python3
"""Generate entry.png: one image summing up the world news of 27 Nov 2026.

Deterministic, no network access. Only Pillow + the standard library.
Run:  python3 main.py
"""

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1024, 1024
OUT = "entry.png"

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---- palette ---------------------------------------------------------------
BG = (13, 27, 46)          # deep navy page
HEADER_BG = (10, 20, 36)
CARD = (255, 255, 255)
CARD_EDGE = (203, 213, 225)
INK = (15, 23, 42)
MUTED = (71, 85, 105)
ACCENT = (245, 158, 11)    # amber rule under the title
FOOTER_FG = (148, 163, 184)

TAG_COLORS = {
    "ECONOMY": (180, 83, 9),
    "DEFENCE": (29, 78, 216),
    "DISASTER": (190, 24, 93),
    "ENERGY": (5, 150, 105),
    "TECH": (109, 40, 217),
    "SOCIETY": (8, 145, 178),
}

# ---- the news (27 November 2026, verified from live news sources) ----------
STORIES = [
    (
        "ECONOMY",
        "World stocks tumble as Trump tariffs rattle markets",
        "Washington proposed new tariffs on 14 partners; the MSCI world "
        "index fell 0.6%.",
        "Reuters",
    ),
    (
        "DEFENCE",
        "US approves $622m F-16 support package for Ukraine",
        "The deal to keep Ukraine's F-16 jets flying, paid for by "
        "European allies.",
        "Reuters / AP",
    ),
    (
        "DISASTER",
        "Mount Mayon stays on Alert Level 3 in the Philippines",
        "PHIVOLCS recorded 9 volcanic quakes in 24 hours; the 6-km "
        "danger zone stays closed.",
        "PHIVOLCS / Malaya",
    ),
    (
        "ENERGY",
        "Houthi strike on Saudi refinery lifts oil to $94.61",
        "Brent crude jumped 3.5% after Yemen's Houthis said they hit a "
        "major Saudi oil refinery.",
        "Reuters",
    ),
    (
        "TECH",
        "Drone sets world speed record at 727 km/h",
        "A Quantum Technologies UAV hit 727 km/h in Germany, a record "
        "for its kind.",
        "News wires",
    ),
    (
        "SOCIETY",
        "UK net migration falls to near 30-year low",
        "Net migration hit its lowest in almost three decades, outside "
        "the Covid era.",
        "News wires",
    ),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_story(draw, x, y, w, h, tag, headline, summary, source):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=16,
                           fill=CARD, outline=CARD_EDGE, width=2)
    pad = 22
    cx = x + pad
    cy = y + 18
    inner = w - 2 * pad

    # tag pill
    tag_font = font(FONT_BOLD, 19)
    tag_w = draw.textlength(tag, font=tag_font) + 24
    tag_h = 30
    draw.rounded_rectangle([cx, cy, cx + tag_w, cy + tag_h], radius=15,
                           fill=TAG_COLORS[tag])
    draw.text((cx + 12, cy + 5), tag, font=tag_font, fill=(255, 255, 255))
    cy += tag_h + 12

    # headline
    head_font = font(FONT_BOLD, 26)
    for line in wrap(draw, headline, head_font, inner):
        draw.text((cx, cy), line, font=head_font, fill=INK)
        cy += 33
    cy += 6

    # summary, clipped so it can never run past the source line
    sum_font = font(FONT_REG, 20)
    max_sum_lines = max(1, (y + h - 44 - cy) // 26)
    sum_lines = wrap(draw, summary, sum_font, inner)[:max_sum_lines]
    for line in sum_lines:
        draw.text((cx, cy), line, font=sum_font, fill=MUTED)
        cy += 26
    cy += 8

    # source line, pinned near the bottom of the card
    src_font = font(FONT_REG, 17)
    draw.text((cx, y + h - 34), "Source: " + source,
              font=src_font, fill=(100, 116, 139))


def verify_output(path):
    """Open the generated image and confirm it is the expected 1024x1024."""
    with Image.open(path) as im:
        assert im.size == (WIDTH, HEIGHT), f"bad size: {im.size}"
        print("verified", path, im.size, im.mode)


def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    # ---- header ------------------------------------------------------------
    draw.rectangle([0, 0, WIDTH, 168], fill=HEADER_BG)
    title_font = font(FONT_BOLD, 54)
    draw.text((40, 26), "WORLD NEWS IN ONE IMAGE",
              font=title_font, fill=(255, 255, 255))
    date_font = font(FONT_REG, 28)
    draw.text((40, 96), "Friday, 27 November 2026  ·  Six stories that mattered",
              font=date_font, fill=(203, 213, 225))
    draw.rectangle([40, 150, 220, 156], fill=ACCENT)

    # ---- story grid: 2 columns x 3 rows ------------------------------------
    margin = 40
    gap_x, gap_y = 24, 20
    card_w = (WIDTH - 2 * margin - gap_x) // 2
    card_h = 236
    top = 192
    for i, (tag, headline, summary, source) in enumerate(STORIES):
        col, row = i % 2, i // 2
        x = margin + col * (card_w + gap_x)
        y = top + row * (card_h + gap_y)
        draw_story(draw, x, y, card_w, card_h, tag, headline, summary, source)

    # ---- footer ------------------------------------------------------------
    foot_font = font(FONT_REG, 19)
    foot = "Sources: Reuters, PHIVOLCS, Malaya Business Insight, news wires"
    tw = draw.textlength(foot, font=foot_font)
    draw.text(((WIDTH - tw) / 2, HEIGHT - 44), foot,
              font=foot_font, fill=FOOTER_FG)

    img.save(OUT)
    print("wrote", OUT, img.size)
    verify_output(OUT)


if __name__ == "__main__":
    main()

"""Draw THE WORLD TODAY — Saturday 21 November 2026.

A newspaper front page summing up the day's world news, drawn entirely in
code with PIL. Outputs entry.png (1024x1024, under 1 MiB).
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
PAPER = (246, 241, 227)
INK = (20, 20, 20)
NAVY = (27, 42, 74)
RED = (166, 30, 34)
BLUE = (46, 90, 136)
GREY = (90, 88, 80)
GOLD = (198, 148, 44)
SEA = (64, 110, 150)
TEAL = (32, 110, 96)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, bold=False, serif=True):
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            trial = cur + " " + w
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hrule(draw, x0, x1, y, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def kicker(draw, x, y, text, fill=RED):
    draw.text((x, y), text, font=font(14, bold=True, serif=False), fill=fill)
    return y + 22


def star_points(cx, cy, r_out, r_in, n=8, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def burst(draw, cx, cy, r, fill=(232, 122, 30), core=(250, 210, 90)):
    draw.polygon(star_points(cx, cy, r, r * 0.45, 10), fill=fill)
    draw.polygon(star_points(cx, cy, r * 0.55, r * 0.28, 10), fill=core)


def globe(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=3)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 208, 224))
    for frac in (-0.55, 0.0, 0.55):
        y = cy + frac * r
        half = math.sqrt(max(0.0, r * r - (frac * r) ** 2))
        draw.line([(cx - half, y), (cx + half, y)], fill=NAVY, width=2)
    for rx in (r * 0.45, r * 0.85):
        draw.arc([cx - rx, cy - r, cx + rx, cy + r], 270, 90, fill=NAVY, width=2)
        draw.arc([cx - rx, cy - r, cx + rx, cy + r], 90, 270, fill=NAVY, width=2)
    draw.ellipse([cx - r * 0.55, cy - r * 0.5, cx - r * 0.05, cy - r * 0.05],
                 fill=TEAL)
    draw.ellipse([cx + r * 0.05, cy + r * 0.1, cx + r * 0.5, cy + r * 0.5],
                 fill=TEAL)


def draw_lead_art(draw, x, y, w, h):
    """Gulf scene: sky, sea, Bahrain island, two strikes, a tanker."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + int(h * 0.42)], fill=(214, 226, 232))
    draw.rectangle([x, y + int(h * 0.42), x + w, y + h], fill=(150, 188, 214))
    draw.text((x + 10, y + 6), "GULF OF BAHRAIN", font=font(11, bold=True,
              serif=False), fill=NAVY)
    # Bahrain island
    draw.polygon([(x + 90, y + 26), (x + 150, y + 14), (x + 210, y + 22),
                  (x + 225, y + 42), (x + 180, y + 54), (x + 120, y + 52)],
                 fill=(226, 205, 150), outline=INK)
    draw.text((x + 118, y + 58), "BAHRAIN", font=font(12, bold=True,
              serif=False), fill=INK)
    # Qeshm Island, top right
    draw.polygon([(x + w - 190, y + 6), (x + w - 20, y + 6),
                  (x + w - 30, y + 26), (x + w - 160, y + 24)],
                 fill=(206, 190, 150), outline=INK)
    draw.text((x + w - 178, y + 30), "QESHM I.", font=font(11, bold=True,
              serif=False), fill=INK)
    burst(draw, x + 165, y + 34, 19)
    burst(draw, x + w - 80, y + 66, 15)
    # tanker
    draw.rectangle([x + w - 250, y + 66, x + w - 130, y + 78],
                   fill=(120, 40, 40), outline=INK)
    draw.rectangle([x + w - 205, y + 56, x + w - 178, y + 66],
                   fill=(240, 240, 240), outline=INK)
    # waves
    for wy in (y + h - 16, y + h - 6):
        for wx in range(x + 8, x + w - 8, 44):
            draw.arc([wx, wy, wx + 34, wy + 12], 180, 360, fill=SEA, width=2)


def draw_badge_art(draw, x, y, w, h):
    """Sheriff star + handcuffs, for the cartel capture."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + h], fill=(232, 226, 208))
    cx, cy = x + w // 2, y + h // 2 - 4
    r = int(h * 0.36)
    draw.polygon(star_points(cx, cy, r, int(r * 0.42), 5), fill=GOLD,
                 outline=INK)
    draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=NAVY)
    draw.text((cx - 8, cy - 11), "10", font=font(17, bold=True, serif=False),
              fill=(255, 255, 255))
    # handcuff links at the sides
    for hx in (x + 22, x + w - 52):
        draw.ellipse([hx, y + 12, hx + 30, y + 42], outline=INK, width=4)
    draw.line([(x + 52, y + 27), (x + w - 52, y + 27)], fill=INK, width=3)
    draw.text((x + 14, y + h - 24), "FBI'S 10 MOST WANTED",
              font=font(13, bold=True, serif=False), fill=INK)


def draw_skyline_art(draw, x, y, w, h):
    """City skyline under a missile burst."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + h], fill=(222, 214, 196))
    draw.text((x + 10, y + 5), "KRYVYI RIH", font=font(12, bold=True,
              serif=False), fill=RED)
    base = y + h
    heights = [0.42, 0.62, 0.35, 0.72, 0.5, 0.66, 0.38]
    bw = w // len(heights)
    for i, frac in enumerate(heights):
        bx = x + i * bw + 3
        top = base - int(h * frac)
        draw.rectangle([bx, top, bx + bw - 6, base], fill=NAVY, outline=INK)
        for wy in range(top + 10, base - 8, 16):
            for wx in range(bx + 7, bx + bw - 12, 13):
                draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(250, 210, 90))
    burst(draw, x + int(w * 0.68), y + int(h * 0.3), 17)


def draw_climate_art(draw, x, y, w, h):
    """Globe beside a clock running past the deadline."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + h], fill=(226, 234, 226))
    draw.text((x + 10, y + 5), "ANTALYA", font=font(12, bold=True,
              serif=False), fill=NAVY)
    draw.text((x + w - 108, y + 5), "PAST DEADLINE", font=font(12, bold=True,
              serif=False), fill=RED)
    r = int(h * 0.38)
    globe(draw, x + 78, y + h // 2 + 10, r)
    cx, cy = x + w - 92, y + h // 2 + 10
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
                 outline=INK, width=3)
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        x1 = cx + (r - 6) * math.sin(a)
        y1 = cy - (r - 6) * math.cos(a)
        x2 = cx + (r - 2) * math.sin(a)
        y2 = cy - (r - 2) * math.cos(a)
        draw.line([(x1, y1), (x2, y2)], fill=INK, width=2)
    draw.line([(cx, cy), (cx - 3, cy - int(r * 0.68))], fill=INK, width=3)
    draw.line([(cx, cy), (cx + int(r * 0.5), cy - 5)], fill=INK, width=3)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)


def draw_chart_art(draw, x, y, w, h):
    """Bitcoin's plunge and rebound, with stock tickers below."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    top = y + 20
    bot = y + h - 24
    for gy in range(top + 4, bot, 14):
        draw.line([(x + 8, gy), (x + w - 8, gy)], fill=(228, 228, 228), width=1)
    xs = [0.04, 0.24, 0.40, 0.55, 0.68, 0.83, 0.96]
    ys = [0.28, 0.38, 0.55, 0.85, 0.66, 0.48, 0.40]
    pts = [(x + int(fx * w), top + int(fy * (bot - top))) for fx, fy in zip(xs, ys)]
    draw.line(pts, fill=RED, width=4, joint="curve")
    lx, ly = pts[3]
    draw.ellipse([lx - 4, ly - 4, lx + 4, ly + 4], fill=RED)
    draw.text((lx - 30, ly - 22), "$55,130", font=font(11, bold=True,
              serif=False), fill=RED)
    draw.text((x + 10, y + 5), "BITCOIN", font=font(11, bold=True,
              serif=False), fill=NAVY)
    draw.text((x + w - 66, y + 5), "$60,255", font=font(11, bold=True,
              serif=False), fill=TEAL)
    draw.text((x + 10, y + h - 20), "S&P 500 -3.7%  |  NASDAQ -5.3%",
              font=font(11, bold=True, serif=False), fill=INK)


def draw_mosquito_art(draw, x, y, w, h):
    """A Wolbachia mosquito, drawn in code, scaled to the box."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + h], fill=(232, 240, 238))
    draw.text((x + 10, y + 5), "WOLBACHIA", font=font(11, bold=True,
              serif=False), fill=TEAL)
    cx, cy = x + w // 2, y + int(h * 0.52)
    u = h / 90.0
    # wings
    draw.ellipse([cx - 46 * u, cy - 36 * u, cx - 2, cy - 2],
                 outline=GREY, width=2, fill=(255, 255, 255))
    draw.ellipse([cx + 2, cy - 36 * u, cx + 46 * u, cy - 2],
                 outline=GREY, width=2, fill=(255, 255, 255))
    # body
    draw.ellipse([cx - 9 * u, cy - 12 * u, cx + 9 * u, cy + 26 * u], fill=INK)
    draw.ellipse([cx - 12 * u, cy - 24 * u, cx + 12 * u, cy - 6 * u], fill=INK)
    # legs
    for dx in (-1, 1):
        for k, (lx, ly) in enumerate([(-30, 18), (-36, 30), (-26, 40)]):
            draw.line([(cx + dx * 5 * u, cy + 4 + k * 6 * u),
                       (cx + dx * lx * u, cy + ly * u)], fill=INK, width=2)
    # antennae + proboscis
    draw.line([(cx - 5 * u, cy - 22 * u), (cx - 18 * u, cy - 38 * u)],
              fill=INK, width=2)
    draw.line([(cx + 5 * u, cy - 22 * u), (cx + 18 * u, cy - 38 * u)],
              fill=INK, width=2)
    draw.line([(cx, cy - 24 * u), (cx, cy - 40 * u)], fill=INK, width=2)


def draw_boat_art(draw, x, y, w, h):
    """Capsized boat on waves, scaled to the box."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + int(h * 0.55)], fill=(214, 226, 232))
    draw.rectangle([x, y + int(h * 0.55), x + w, y + h], fill=(120, 165, 200))
    draw.text((x + 10, y + 5), "NUN RIVER, BAYELSA", font=font(11, bold=True,
              serif=False), fill=NAVY)
    # capsized hull
    draw.polygon([(x + 60, y + int(h * 0.55)), (x + 210, y + int(h * 0.45)),
                  (x + 240, y + int(h * 0.62)), (x + 90, y + int(h * 0.68))],
                 fill=(120, 40, 40), outline=INK)
    draw.polygon([(x + 150, y + int(h * 0.45)), (x + 168, y + int(h * 0.30)),
                  (x + 178, y + int(h * 0.45))],
                 fill=(90, 90, 90), outline=INK)
    for wy in (y + h - 22, y + h - 10):
        for wx in range(x + 8, x + w - 8, 40):
            draw.arc([wx, wy, wx + 32, wy + 12], 180, 360, fill=NAVY, width=2)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 30
    rx = W - mx

    # --- masthead ---
    title = "THE WORLD TODAY"
    tf = font(62, bold=True)
    d.text(((W - d.textlength(title, font=tf)) / 2, 14), title, font=tf,
           fill=INK)
    hrule(d, mx, rx, 86, 3)
    hrule(d, mx, rx, 91, 1)

    # --- date band ---
    d.rectangle([mx, 100, rx, 140], fill=NAVY)
    date_text = "SATURDAY  21  NOVEMBER  2026"
    df = font(28, bold=True)
    d.text(((W - d.textlength(date_text, font=df)) / 2, 106), date_text,
           font=df, fill=(255, 255, 255))

    # --- deck line ---
    deck = ("Iran hits U.S. bases in Bahrain  •  Cartel kingpin seized in Mexico  •  "
            "Missiles strike Zelenskyy's hometown")
    d.text(((W - d.textlength(deck, font=font(15, serif=False))) / 2, 148),
           deck, font=font(15, serif=False), fill=GREY)
    hrule(d, mx, rx, 172, 2)

    # --- ROW A: lead + Mexico (flow-driven; both end near y=475) ---
    y = 182
    y = kicker(d, mx, y, "GULF CRISIS  —  MANAMA, BAHRAIN")
    y = para(d, mx, y, "IRAN HITS U.S. BASES IN BAHRAIN",
             font(40, bold=True), 590, leading=46)
    y = para(d, mx, y + 6,
             "Tehran says its Revolutionary Guards hit two American positions; "
             "Bahrain says an industrial site burned and no one was hurt. "
             "Two tankers were also struck off Oman.",
             font(16), 590, leading=21)
    draw_lead_art(d, mx, y + 10, 590, 100)
    lead_bottom = y + 10 + 100

    y2 = 182
    y2 = kicker(d, 648, y2, "MEXICO  —  SINALOA")
    y2 = para(d, 648, y2, "CARTEL KINGPIN 'EL CHAPO ISIDRO' CAPTURED",
              font(25, bold=True), 346, leading=30)
    y2 = para(d, 648, y2 + 6,
              "FBI most-wanted drug lord Fausto Isidro Meza Flores seized in a "
              "Guasave raid. Gunfights erupt across Sinaloa; 11 killed.",
              font(15), 346, leading=20)
    draw_badge_art(d, 648, y2 + 10, 346, 100)
    mex_bottom = y2 + 10 + 100

    row_a_bottom = max(lead_bottom, mex_bottom)
    hrule(d, mx, rx, row_a_bottom + 10, 2)

    # --- ROW B: Kryvyi Rih + COP31 ---
    y = row_a_bottom + 20
    y = kicker(d, mx, y, "WAR IN UKRAINE  —  KRYVYI RIH")
    y = para(d, mx, y, "MISSILE HITS ZELENSKYY'S HOMETOWN",
             font(22, bold=True), 460, leading=27)
    y = para(d, mx, y + 5,
             "A double-tap ballistic strike kills a boy of 7 and a woman of 20; "
             "60 wounded. Russian missiles and a drone also land in Poland.",
             font(14), 460, leading=18)
    draw_skyline_art(d, mx, y + 8, 460, 64)
    kry_bottom = y + 8 + 64

    y2 = row_a_bottom + 20
    y2 = kicker(d, 522, y2, "CLIMATE  —  ANTALYA, TURKEY")
    y2 = para(d, 522, y2, "COP31 TALKS RUN INTO OVERTIME WITH NO DEAL",
              font(22, bold=True), 472, leading=27)
    y2 = para(d, 522, y2 + 5,
              "Fossil fuels are missing from the draft text as negotiators chase "
              "a final agreement past the deadline.",
              font(14), 472, leading=18)
    draw_climate_art(d, 522, y2 + 8, 472, 64)
    cop_bottom = y2 + 8 + 64

    row_b_bottom = max(kry_bottom, cop_bottom)
    hrule(d, mx, rx, row_b_bottom + 10, 2)

    # --- ROW C: markets + dengue + Nigeria ---
    y = row_b_bottom + 20
    y = kicker(d, mx, y, "MARKETS")
    y = para(d, mx, y, "STOCKS SLIDE INTO CORRECTION",
             font(19, bold=True), 300, leading=23)
    y = para(d, mx, y + 4,
             "The AI sell-off deepens: the Nasdaq erases its 2026 gains.",
             font(13), 300, leading=17)
    draw_chart_art(d, mx, y + 8, 300, 72)

    y2 = row_b_bottom + 20
    y2 = kicker(d, 362, y2, "SCIENCE  —  BRAZIL")
    y2 = para(d, 362, y2, "MOSQUITOES CUT DENGUE BY 69%",
              font(19, bold=True), 300, leading=23)
    y2 = para(d, 362, y2 + 4,
              "Wolbachia mosquitoes shielded 5,757 children in a four-year "
              "trial in Belo Horizonte.",
              font(13), 300, leading=17)
    draw_mosquito_art(d, 362, y2 + 8, 300, 72)

    y3 = row_b_bottom + 20
    y3 = kicker(d, 694, y3, "NIGERIA  —  BAYELSA")
    y3 = para(d, 694, y3, "BOAT CAPSIZES; AT LEAST 24 DEAD",
              font(19, bold=True), 300, leading=23)
    y3 = para(d, 694, y3 + 4,
              "Mourners bound for a funeral sink on the Nun River; 24 rescued "
              "as the search goes on.",
              font(13), 300, leading=17)
    draw_boat_art(d, 694, y3 + 8, 300, 72)

    row_c_bottom = max(y + 8 + 72, y2 + 8 + 72, y3 + 8 + 72)

    # --- sport strip ---
    sy = row_c_bottom + 12
    d.rectangle([mx, sy, rx, sy + 40], outline=INK, width=2)
    d.text((mx + 12, sy + 11), "SPORT", font=font(15, bold=True, serif=False),
           fill=RED)
    sport = ("ALCARAZ v ZVEREV IN ATP FINALS DECIDER — Alcaraz beats Shelton "
             "3-6, 6-3, 7-6 (7-1) in Turin")
    d.text((mx + 92, sy + 12), sport, font=font(14, bold=True, serif=False),
           fill=INK)

    # --- footer ---
    foot = ("THE WORLD TODAY  •  Saturday 21 November 2026  •  All stories first "
            "reported on this day  •  Sources: AP  •  Reuters  •  BBC  •  AFP  •  CoinDesk")
    d.text(((W - d.textlength(foot, font=font(12, serif=False))) / 2, sy + 52),
           foot, font=font(12, serif=False), fill=GREY)

    print(f"row bottoms: A={row_a_bottom} B={row_b_bottom} C={row_c_bottom} "
          f"sport={sy} footer={sy + 52}")
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = build()
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"wrote {out}: {img.size[0]}x{img.size[1]}, {size} bytes")
    if size > 1048576:
        print("WARNING: over the 1 MiB limit", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

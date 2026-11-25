#!/usr/bin/env python3
"""Render the Wednesday 25 November 2026 world-news poster, 1024x1024.

Champion layout from news-image-20261122: giant date masthead, red
headline strip, three hero stories with big flat illustrations on the top
half, a THE DAY IN NUMBERS panel, region pills, twelve small cards,
eighteen one-line briefs in two columns, a world map with numbered pins,
a DATE CHECK box and a HOW SURE legend. Every story is dated 25 Nov
2026 (happened or first reported that day) and carries its source.
Drawn in code with Pillow; no network; deterministic output.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
RED = (193, 18, 31)
NAVY = (20, 33, 61)
TEAL = (15, 118, 110)
GOLD = (180, 83, 9)
GREY = (110, 105, 95)
LINE = (210, 203, 188)
CARD = (255, 255, 255)

NOTO = "/usr/share/fonts/truetype/noto/"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"


def pick(name, size):
    for path in (NOTO + name, DEJAVU % ("-Bold" if "Bold" in name else "")):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def serif_b(size):
    return pick("NotoSerif-Bold.ttf", size)


def sans_b(size):
    return pick("NotoSans-Bold.ttf", size)


def sans(size):
    return pick("NotoSans-Regular.ttf", size)


def fit_lines(d, text, font, width, max_lines):
    """Wrap text to fit width, at most max_lines (last line gets ...)."""
    words = text.split()
    lines, cur, used = [], "", 0
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
            used += 1
        elif len(lines) < max_lines - 1:
            lines.append(cur)
            cur = w
            used += 1
        else:
            break  # last line is full; the rest is dropped
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if used < len(words) and lines:
        # words remain unplaced: ellipsis on the last line
        last = lines[-1]
        while last and d.textlength(last + " ...", font=font) > width:
            last = last.rsplit(" ", 1)[0] if " " in last else ""
        lines[-1] = (last + " ...") if last else "..."
    return lines


# ------------------------------------------------------------------ data

HEROES = [
    dict(n=1, place="RIYADH", cat="MIDDLE EAST", status="CONFIRMED",
         src="Reuters", art="tower",
         banner="HOUTHIS STRIKE RIYADH TOWER",
         head="Houthis hit Riyadh's tallest tower",
         deck="Eleven wounded as a strike hits the PIF Tower — the second "
              "attack on the landmark in a week."),
    dict(n=2, place="SHANGHAI", cat="EAST ASIA", status="OFFICIAL",
         src="Associated Press", art="probe",
         banner="CHINA PROBES A POLITBURO MEMBER",
         head="China opens graft probe into Chen Jining",
         deck="Investigators target the Shanghai party chief in a shock "
              "move against a top official."),
    dict(n=3, place="NEW YORK", cat="NORTH AMERICA", status="CONFIRMED",
         src="Reuters", art="chart",
         banner="NVIDIA ROUT AFTER THE RALLY",
         head="Nvidia plunges a day after its 31% surge",
         deck="Nvidia falls about 6% and the Nasdaq 1.5% as chips give back "
              "Monday's surge."),
]

CARDS = [
    dict(n=4, place="GULF OF FINLAND", cat="EUROPE", status="CONFIRMED",
         src="Reuters",
         head="Zelenskiy confirms Ukraine hit a Russian ship",
         deck="Kyiv claims it; Norway urges caution."),
    dict(n=5, place="WASHINGTON", cat="EAST ASIA", status="CONFIRMED",
         src="Reuters / AP",
         head="US jury convicts Huawei of stealing trade secrets",
         deck="Trade-secret theft and bank fraud."),
    dict(n=6, place="WASHINGTON", cat="NORTH AMERICA", status="CONFIRMED",
         src="Associated Press",
         head="Trump awards Giuliani the Medal of Freedom",
         deck="Top US civilian honour for the ex-mayor."),
    dict(n=7, place="WASHINGTON", cat="NORTH AMERICA", status="REPORTED",
         src="Reuters",
         head="US envoy doubts Israel aid will end this year",
         deck="$3.8bn a year may continue, envoy says."),
    dict(n=8, place="GAZA CITY", cat="MIDDLE EAST", status="REPORTED",
         src="SCMP",
         head="Hamas security chief killed in Gaza strike",
         deck="Israeli strike kills senior Hamas figure."),
    dict(n=9, place="WASHINGTON", cat="NORTH AMERICA", status="REPORTED",
         src="New York Times",
         head="CIA and spy chief's office hit by cyber breach",
         deck="Unclassified data exposed, NYT reports."),
    dict(n=10, place="DAKAR", cat="AFRICA", status="CONFIRMED",
         src="The Hindu",
         head="Senegal wins back Africa Cup title in court",
         deck="CAS gives the title back to Senegal."),
    dict(n=11, place="PARIS", cat="EUROPE", status="CONFIRMED",
         src="Reuters",
         head="Sanofi to buy Insmed for $41bn in cash",
         deck="French drugmaker offers $175 a share."),
    dict(n=12, place="WASHINGTON", cat="NORTH AMERICA", status="OFFICIAL",
         src="Conference Board",
         head="US consumer confidence jumps to 103.3",
         deck="Up 11.4 points, best since January 2025."),
    dict(n=13, place="CANBERRA", cat="OCEANIA", status="OFFICIAL",
         src="ABS data",
         head="Australia inflation hits 4.9% in October",
         deck="Underlying 3.8%, hotter than forecast."),
    dict(n=14, place="LONDON", cat="NORTH AMERICA", status="REPORTED",
         src="Market data",
         head="Bitcoin slips below $60,000",
         deck="ETF outflows hit a record $4.71bn."),
    dict(n=15, place="GENEVA", cat="EUROPE", status="CONFIRMED",
         src="The Hindu",
         head="Gukesh holds Sindarov in chess title opener",
         deck="World champion draws game one in Geneva."),
]

BRIEFS = [
    ("16", "NORTH AMERICA", "Trump pardons turkeys Freedom and Feathers"),
    ("17", "NORTH AMERICA", "Fort Hood gunman Hasan seeks stay of execution"),
    ("18", "EUROPE", "Sarkozy corruption case ordered to trial"),
    ("19", "MIDDLE EAST", "Houthis 60 km from Aden, 'won't take city'"),
    ("20", "SOUTH ASIA", "BJP and Akali Dal reunite for Punjab polls"),
    ("21", "EUROPE", "Two held after break-in at Prince William's home"),
    ("22", "EUROPE", "Pelicot condemns publisher over nude images"),
    ("23", "EAST ASIA", "N. Korea threatens to shut Swiss office"),
    ("24", "EAST ASIA", "China cobalt firms race DR Congo export ban"),
    ("25", "SOUTHEAST ASIA", "Landmine casualties hit 5-year high: 7,000"),
    ("26", "NORTH AMERICA", "US soldier admits selling secrets to China"),
    ("27", "NORTH AMERICA", "Shein to pay $100m in FTC settlement"),
    ("28", "NORTH AMERICA", "UN: five women killed hourly by relatives"),
    ("29", "EAST ASIA", "Shenzhou-24 crew named; Pakistani to fly"),
    ("30", "EAST ASIA", "Most distant quasar found, 630m yrs on"),
    ("31", "EUROPE", "NATO plans early-warning jets for Poland"),
    ("32", "MIDDLE EAST", "Iran: three tankers hit by mines in Hormuz"),
    ("33", "LATIN AMERICA", "Gunmen take 25 hostage at Colombia store"),
]

NUMBERS = [
    ("DOW", "50,018.70", "+0.85%", "record close"),
    ("S&P 500", "7,201.09", "-0.50%", ""),
    ("NASDAQ", "23,733.54", "-1.48%", ""),
    ("GOLD", "$3,556", "-2.2%", "per oz"),
    ("BRENT", "$91.05", "+1.95%", "per barrel"),
    ("BITCOIN", "<$60,000", "", "ETF outflows record"),
]

REGIONS = [
    ("NORTH AMERICA", 12), ("EUROPE", 7), ("EAST ASIA", 6),
    ("MIDDLE EAST", 4), ("AFRICA", 1), ("OCEANIA", 1),
    ("SOUTHEAST ASIA", 1), ("SOUTH ASIA", 1), ("LATIN AMERICA", 1),
]

PINS = [
    (1, 24.7, 46.7), (2, 31.2, 121.5), (3, 40.7, -74.0),
    (4, 59.9, 25.0), (5, 38.9, -77.0), (8, 31.5, 34.5),
    (10, 14.7, -17.4), (13, -35.3, 149.1), (15, 46.2, 6.1),
    (19, 12.8, 45.0), (31, 52.2, 21.0), (33, 4.7, -74.1),
]

DATE_CHECK = ("LEFT OUT ON PURPOSE — earlier days: COP31 ended with no pact "
              "(22 Nov) · Huang reinstated as Nvidia CEO (23 Nov) · US "
              "midterms (early Nov) · AFCON final (Jan 2026).")


# ------------------------------------------------------------------ art

def scene_tower(d, box, bg):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=bg)
    d.rectangle([x0, y0 + 62, x1, y0 + 66], fill=(255, 176, 66))
    # skyline
    base = y1
    for bx, bw, bh, col in (
            (8, 34, 52, (52, 74, 110)), (46, 26, 66, (38, 58, 92)),
            (76, 30, 44, (52, 74, 110)), (200, 30, 58, (38, 58, 92)),
            (234, 26, 40, (52, 74, 110)), (264, 34, 62, (38, 58, 92))):
        d.rectangle([x0 + bx, base - bh, x0 + bx + bw, base], fill=col)
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(x0 + bx + 6, x0 + bx + bw - 4, 10):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 214, 120))
    # the tall tower, centre-left
    tx = x0 + 128
    d.polygon([(tx - 16, base), (tx - 10, y0 + 18), (tx + 10, y0 + 18),
               (tx + 16, base)], fill=(120, 140, 170))
    d.rectangle([tx - 3, y0 + 6, tx + 3, y0 + 18], fill=(160, 180, 210))
    for wy in range(y0 + 30, base - 8, 14):
        d.rectangle([tx - 6, wy, tx + 6, wy + 6], fill=(255, 214, 120))
    # blast burst at the tower top
    cx, cy = tx + 34, y0 + 34
    for r, col in ((30, (255, 120, 0)), (20, (255, 176, 66)), (11, (255, 240, 180))):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    for ang in range(0, 360, 30):
        import math
        a = math.radians(ang)
        d.line([(cx + 32 * math.cos(a), cy + 32 * math.sin(a)),
                (cx + 44 * math.cos(a), cy + 44 * math.sin(a))],
               fill=(255, 176, 66), width=3)
    d.ellipse([cx - 52, cy + 26, cx - 30, cy + 44], fill=(120, 120, 120))
    d.ellipse([cx - 20, cy + 34, cx + 4, cy + 50], fill=(90, 90, 90))


def scene_probe(d, box, bg):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=bg)
    # government hall: pediment, columns, steps
    cx = (x0 + x1) // 2
    d.polygon([(cx - 110, y0 + 52), (cx + 110, y0 + 52), (cx, y0 + 16)],
              fill=(232, 222, 200))
    d.ellipse([cx - 12, y0 + 30, cx + 12, y0 + 52], fill=RED)
    d.rectangle([cx - 108, y0 + 52, cx + 108, y0 + 60], fill=(232, 222, 200))
    for i in range(5):
        px = cx - 88 + i * 44
        d.rectangle([px - 7, y0 + 60, px + 7, y1 - 26], fill=(232, 222, 200))
    d.rectangle([cx - 108, y1 - 26, cx + 108, y1 - 18], fill=(232, 222, 200))
    d.rectangle([cx - 118, y1 - 18, cx + 118, y1 - 10], fill=(210, 198, 170))
    # gold magnifier over the hall
    mx, my, mr = cx + 62, y0 + 62, 34
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=(255, 200, 60), width=6)
    d.ellipse([mx - mr + 8, my - mr + 8, mx + mr - 8, my + mr - 8],
              outline=(255, 220, 120), width=2)
    d.line([(mx + 24, my + 24), (mx + 52, my + 52)], fill=(255, 200, 60), width=7)


def scene_chart(d, box, bg):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=bg)
    for gy in range(y0 + 22, y1 - 8, 24):
        d.line([(x0 + 8, gy), (x1 - 8, gy)], fill=(90, 96, 104))
    # Monday surge in green, Tuesday plunge in red
    pts_up = [(x0 + 14, y1 - 34), (x0 + 70, y1 - 52), (x0 + 120, y1 - 96),
              (x0 + 165, y1 - 108)]
    d.line(pts_up, fill=(74, 222, 128), width=5, joint="curve")
    pts_dn = [(x0 + 165, y1 - 108), (x0 + 215, y1 - 66), (x0 + 260, y1 - 40),
              (x0 + 300, y1 - 30)]
    d.line(pts_dn, fill=(255, 80, 80), width=5, joint="curve")
    d.ellipse([x0 + 158, y1 - 115, x0 + 172, y1 - 101], fill=(74, 222, 128))
    d.ellipse([x0 + 293, y1 - 37, x0 + 307, y1 - 23], fill=(255, 80, 80))
    d.text((x0 + 16, y0 + 10), "+31.5% MON", font=sans_b(13), fill=(74, 222, 128))
    d.text((x1 - 92, y0 + 10), "-6% TUE", font=sans_b(13), fill=(255, 80, 80))


SCENES = {"tower": scene_tower, "probe": scene_probe, "chart": scene_chart}

# ------------------------------------------------------------------ map

LAND = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-82, 66),
     (-76, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 44), (-75, 35),
     (-80, 32), (-84, 30), (-90, 21), (-97, 26), (-105, 23), (-115, 29),
     (-125, 40), (-124, 49), (-135, 58), (-155, 58), (-165, 60)],
    [(-80, 9), (-72, 12), (-62, 9), (-52, 5), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-58, -35), (-65, -41), (-70, -52), (-74, -54),
     (-73, -44), (-72, -30), (-77, -12), (-81, -6), (-80, 2)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (8, 57), (12, 56), (18, 56),
     (21, 55), (24, 59), (30, 60), (28, 70), (40, 68), (32, 60), (28, 55),
     (24, 45), (19, 42), (12, 44), (3, 43), (-2, 37)],
    [(-6, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12), (48, 11),
     (51, 12), (44, -1), (40, -10), (36, -18), (33, -26), (28, -33), (19, -35),
     (16, -29), (13, -18), (12, -6), (9, 4), (-8, 5), (-15, 12), (-17, 15)],
    [(60, 70), (70, 72), (90, 75), (110, 74), (130, 72), (150, 70), (170, 67),
     (178, 65), (162, 60), (158, 53), (142, 45), (140, 39), (130, 33),
     (122, 31), (120, 23), (109, 18), (105, 9), (100, 7), (97, 16), (92, 21),
     (88, 22), (80, 13), (77, 8), (72, 20), (66, 25), (60, 25), (57, 26),
     (52, 28), (48, 30), (44, 29), (40, 36), (36, 36), (30, 36), (27, 41),
     (23, 40), (22, 45), (19, 46), (15, 45), (12, 46), (8, 44), (5, 43)],
    [(113, -22), (114, -32), (124, -33), (134, -32), (140, -38), (147, -39),
     (150, -37), (153, -27), (153, -17), (146, -19), (142, -11), (137, -12),
     (132, -12), (126, -14), (122, -17), (114, -22)],
]


def project(lon, lat, box):
    x0, y0, x1, y1 = box
    x = x0 + (lon + 170.0) / 360.0 * (x1 - x0)
    y = y0 + (78.0 - lat) / 140.0 * (y1 - y0)
    return x, y


def draw_world(d, box, pins):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(214, 228, 235))
    for poly in LAND:
        pts = [project(lon, lat, box) for lon, lat in poly]
        d.polygon(pts, fill=(232, 222, 200), outline=(180, 168, 145))
    for lon in range(-150, 181, 30):
        gx, _ = project(lon, 0, box)
        d.line([(gx, y0), (gx, y1)], fill=(200, 214, 222))
    for lat in (-40, 0, 40):
        _, gy = project(0, lat, box)
        d.line([(x0, gy), (x1, gy)], fill=(200, 214, 222))
    placed = []
    for n, lat, lon in pins:
        px, py = project(lon, lat, box)
        while any((px - qx) ** 2 + (py - qy) ** 2 < 16 ** 2 for qx, qy in placed):
            px += 15
            py -= 13
        placed.append((px, py))
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED, outline=(255, 255, 255))
        d.text((px, py + 1), str(n), font=sans_b(8), fill=(255, 255, 255), anchor="mm")


# ------------------------------------------------------------------ bits

STATUS_FILL = {"CONFIRMED": TEAL, "OFFICIAL": NAVY, "REPORTED": GOLD,
               "CLAIM": RED}


def status_tag(d, x, y, status):
    f = sans_b(9)
    w = d.textlength(status, font=f) + 10
    d.rectangle([x, y, x + w, y + 13], fill=STATUS_FILL[status])
    d.text((x + 5, y + 6), status, font=f, fill=(255, 255, 255), anchor="lm")
    return w


def hero_card(d, s, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE)
    art_h = 108
    art_bg = {1: NAVY, 2: (96, 32, 32), 3: (48, 52, 58)}[s["n"]]
    SCENES[s["art"]](d, (x, y, x + w, y + art_h), art_bg)
    d.rectangle([x, y + art_h - 24, x + w, y + art_h], fill=RED)
    d.text((x + 10, y + art_h - 12), s["banner"], font=sans_b(13),
           fill=(255, 255, 255), anchor="lm")
    by = y + art_h + 9
    d.text((x + 10, by), "%d  %s" % (s["n"], s["place"]), font=sans_b(11), fill=INK)
    status_tag(d, x + w - 82, by - 1, s["status"])
    hy = by + 21
    head_lines = fit_lines(d, s["head"], serif_b(19), w - 20, 2)
    for i, line in enumerate(head_lines):
        d.text((x + 10, hy + i * 23), line, font=serif_b(19), fill=INK)
    dy = hy + len(head_lines) * 23 + 2
    for i, line in enumerate(fit_lines(d, s["deck"], sans(12), w - 20, 2)):
        d.text((x + 10, dy + i * 16), line, font=sans(12), fill=(60, 58, 52))
    d.text((x + 10, y + h - 13), "Source: " + s["src"], font=sans(10), fill=GREY)


def mini_card(d, s, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE)
    d.rectangle([x, y, x + 5, y + h], fill=RED)
    ly = y + 6
    d.text((x + 12, ly), "%d  %s" % (s["n"], s["place"]), font=sans_b(10), fill=INK)
    status_tag(d, x + w - 76, ly - 1, s["status"])
    hy = ly + 17
    head_lines = fit_lines(d, s["head"], sans_b(13), w - 22, 2)
    for i, line in enumerate(head_lines):
        d.text((x + 12, hy + i * 16), line, font=sans_b(13), fill=INK)
    dy = hy + len(head_lines) * 16 + 2
    for i, line in enumerate(fit_lines(d, s["deck"], sans(10), w - 22, 1)):
        d.text((x + 12, dy + i * 13), line, font=sans(10), fill=(60, 58, 52))
    d.text((x + 12, y + h - 11), s["src"], font=sans(9), fill=GREY)


# ------------------------------------------------------------------ page

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 14  # margin

    # masthead
    d.text((M, 12), "THE WORLD IN ONE PICTURE", font=sans_b(15), fill=RED)
    d.text((W - M, 12), "33 DATED STORIES  ·  9 REGIONS", font=sans_b(15),
           fill=GREY, anchor="ra")
    d.text((M, 30), "Wednesday 25 November 2026", font=serif_b(40), fill=INK)
    d.line([(M, 76), (W - M, 76)], fill=INK, width=2)

    # red headline strip
    d.rectangle([M, 82, W - M, 108], fill=RED)
    strip = "HOUTHIS HIT RIYADH TOWER   ·   CHINA PROBES POLITBURO MEMBER   ·   NVIDIA ROUT"
    d.text(((W) / 2, 95), strip, font=sans_b(16), fill=(255, 255, 255), anchor="mm")

    # three heroes
    hw, hg, gap = 324, 256, 6
    for i, s in enumerate(HEROES):
        hero_card(d, s, M + i * (hw + gap), 116, hw, hg)

    # numbers panel
    ny = 380
    d.rectangle([M, ny, W - M, ny + 48], fill=NAVY)
    d.text((M + 12, ny + 9), "THE DAY IN NUMBERS", font=sans_b(13),
           fill=(255, 200, 60))
    seg_w = (W - 2 * M - 190) / 6
    for i, (label, val, chg, note) in enumerate(NUMBERS):
        x = M + 190 + i * seg_w
        d.text((x, ny + 7), label, font=sans_b(10), fill=(170, 190, 220))
        d.text((x, ny + 21), val, font=sans_b(15), fill=(255, 255, 255))
        if chg:
            col = (74, 222, 128) if chg.startswith("+") else (255, 120, 120)
            d.text((x + d.textlength(val, font=sans_b(15)) + 5, ny + 24),
                   chg, font=sans_b(11), fill=col)
        if note:
            d.text((x, ny + 37), note, font=sans(9), fill=(170, 190, 220))

    # region pills
    py = 436
    x = M
    d.text((x, py + 2), "REGIONS", font=sans_b(11), fill=GREY)
    x += 62
    for name, count in REGIONS:
        label = "%s %d" % (name, count)
        w = d.textlength(label, font=sans_b(11)) + 16
        d.rounded_rectangle([x, py, x + w, py + 18], radius=9,
                            outline=NAVY, width=1)
        d.text((x + 8, py + 9), label, font=sans_b(11), fill=NAVY, anchor="lm")
        x += w + 6

    # twelve small cards, 4 cols x 3 rows
    cw, ch, cg = 241, 80, 6
    cy = 462
    for i, s in enumerate(CARDS):
        r, c = divmod(i, 4)
        mini_card(d, s, M + c * (cw + cg), cy + r * (ch + 6), cw, ch)
    by = cy + 3 * (ch + 6) + 4

    # map (left) + briefs (right, two columns)
    map_w = 330
    d.text((M, by), "WHERE IT HAPPENED", font=sans_b(12), fill=INK)
    map_box = (M, by + 18, M + map_w, by + 18 + 168)
    draw_world(d, map_box, PINS)
    d.text((M, by + 192), "Pins are story numbers on this page.",
           font=sans(10), fill=GREY)

    bx = M + map_w + 16
    bw = W - M - bx
    d.text((bx, by), "IN BRIEF", font=sans_b(12), fill=INK)
    col_w = (bw - 14) / 2
    for i, (num, region, text) in enumerate(BRIEFS):
        col, row = divmod(i, 9)
        x = bx + col * (col_w + 14)
        y = by + 20 + row * 20
        d.text((x, y), num, font=sans_b(12), fill=RED)
        d.text((x + 24, y), text, font=sans(12), fill=INK)

    # bottom band: DATE CHECK + HOW SURE
    fy = H - 78
    d.line([(M, fy), (W - M, fy)], fill=LINE, width=1)
    d.text((M, fy + 8), "DATE CHECK", font=sans_b(11), fill=RED)
    for i, line in enumerate(fit_lines(d, DATE_CHECK, sans(11), 560, 2)):
        d.text((M, fy + 24 + i * 15), line, font=sans(11), fill=(60, 58, 52))
    lx = M + 590
    d.text((lx, fy + 8), "HOW SURE", font=sans_b(11), fill=RED)
    legend_rows = [
        [("CONFIRMED", "verified by two sources"), ("OFFICIAL", "govt/company statement")],
        [("REPORTED", "one report, unconfirmed"), ("CLAIM", "one side's claim")],
    ]
    for ri, row in enumerate(legend_rows):
        y = fy + 24 + ri * 16
        x = lx
        for tag, meaning in row:
            w = status_tag(d, x, y - 1, tag)
            x += w + 5
            d.text((x, y), meaning, font=sans(10), fill=(60, 58, 52))
            x += d.textlength(meaning, font=sans(10)) + 14
    d.text((M, H - 14), "Sources: Reuters, Associated Press, New York Times, The Hindu, SCMP, Conference Board, market data  ·  All stories happened or were first reported on 25 November 2026.",
           font=sans(9), fill=GREY)
    return img


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    render().save(out, optimize=True)
    print("wrote", out)

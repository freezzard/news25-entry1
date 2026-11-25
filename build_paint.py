#!/usr/bin/env python3
"""Paint the news-image-20261125 digest: one 1024x1024 PNG summing up
Wednesday 25 November 2026, drawn deterministically with Pillow.

Run:  python3 build_paint.py  ->  writes entry.png next to this file.
No network is used. Two runs produce byte-identical output.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W = 1024
H = 1024
PAPER = (246, 241, 230)
INK = (25, 23, 19)
RED = (166, 30, 34)
NAVY = (31, 58, 95)
TEAL = (15, 107, 92)
GOLD = (185, 138, 29)
SLATE = (91, 107, 122)
PANEL = (255, 255, 255)
CREAM = (239, 231, 214)
SEA = (215, 227, 232)
LAND = (176, 196, 164)
LANDLINE = (120, 145, 110)
RULE = (25, 23, 19)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)
MONO_B = lambda s: font("DejaVuSansMono-Bold.ttf", s)


def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines = []
    cur = ""
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


def draw_wrapped(draw, text, fnt, x, y, max_w, fill, leading=None, max_lines=None):
    lines = wrap_text(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    lh = leading if leading is not None else int(fnt.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------- data
# region: Europe | Asia | Middle East | N. America | Africa | Oceania | Global
HEROES = [
    {
        "pin": 1, "tag": "UKRAINE WAR", "region": "Europe", "field": "Conflict",
        "title": "Kyiv claims ship strike in the Gulf",
        "deck": "Zelenskiy confirms a drone hit on a Russian cargo vessel; Norway urges caution as Kyiv's strikes reach beyond Europe.",
        "pict": "ship", "accent": NAVY,
    },
    {
        "pin": 7, "tag": "SPACE", "region": "Asia", "field": "Science",
        "title": "Pakistan's first astronaut lifts off",
        "deck": "Shenzhou-24 carries Muhammad Zeeshan Ali to Tiangong - the first foreign guest aboard China's space station.",
        "pict": "rocket", "accent": TEAL,
    },
    {
        "pin": 6, "tag": "MARKETS", "region": "N. America", "field": "Markets",
        "title": "Nvidia slides as the AI rally stalls",
        "deck": "Shares fall about 6% a day after a 31.5% surge on Huang's return; Nasdaq -1.5% as tariff fears spread.",
        "pict": "chip", "accent": RED,
    },
]

CARDS = [
    {
        "pin": 2, "tag": "YEMEN WAR", "region": "Middle East", "field": "Conflict",
        "title": "Houthis hit Riyadh's tallest tower",
        "deck": "11 wounded; the second strike on the tower in under a week.",
        "pict": "tower", "accent": RED,
    },
    {
        "pin": 3, "tag": "IRAN", "region": "Middle East", "field": "Conflict",
        "title": "Tehran vows to smash the blockade",
        "deck": "Guard says three tankers hit by mines in the Strait of Hormuz.",
        "pict": "tanker", "accent": NAVY,
    },
    {
        "pin": 4, "tag": "GAZA", "region": "Middle East", "field": "Conflict",
        "title": "Strike kills Hamas security chief",
        "deck": "Abu Nahel among 10 dead; meningitis spreads as winter closes in.",
        "pict": "city", "accent": TEAL,
    },
    {
        "pin": 5, "tag": "FRANCE", "region": "Europe", "field": "Law",
        "title": "Sarkozy and Bruni to stand trial",
        "deck": "Libya case goes to court; first hearing set for April 2027.",
        "pict": "court", "accent": NAVY,
    },
    {
        "pin": 6, "tag": "CYBER", "region": "N. America", "field": "Technology",
        "title": "CIA and spy chief's office breached",
        "deck": "Unclassified data hit; FBI crime database breached days earlier.",
        "pict": "shield", "accent": RED,
    },
    {
        "pin": 0, "tag": "CHINA", "region": "Asia", "field": "Law",
        "title": "Huawei guilty on 10 counts in US",
        "deck": "Bank fraud, sanctions breaches over Iran; racketeering fails.",
        "pict": "chip", "accent": GOLD,
    },
    {
        "pin": 6, "tag": "USA", "region": "N. America", "field": "Politics",
        "title": "Giuliani takes Medal of Freedom",
        "deck": "Trump honours the ex-mayor - and pardons two turkeys for Thanksgiving.",
        "pict": "medal", "accent": GOLD,
    },
    {
        "pin": 6, "tag": "USA", "region": "N. America", "field": "Politics",
        "title": "Abrego Garcia leaves for Spain",
        "deck": "Voluntary departure ends the deportation fight; he leaves a free man.",
        "pict": "plane", "accent": TEAL,
    },
    {
        "pin": 0, "tag": "IRAQ", "region": "Middle East", "field": "Energy",
        "title": "Baghdad moves on Kurdish oilfields",
        "deck": "Federal forces ordered to seize fields and crossings in Kurdish areas.",
        "pict": "derrick", "accent": NAVY,
    },
    {
        "pin": 8, "tag": "TURKEY", "region": "Europe", "field": "Disaster",
        "title": "Army helicopter crash kills 5",
        "deck": "Helicopter goes down in Eskisehir; ministry confirms the dead.",
        "pict": "heli", "accent": RED,
    },
    {
        "pin": 0, "tag": "SPAIN", "region": "Europe", "field": "Politics",
        "title": "20 weeks' leave in final package",
        "deck": "Birth leave extended in the last cabinet meeting before the election.",
        "pict": "ballot", "accent": TEAL,
    },
    {
        "pin": 0, "tag": "ISRAEL", "region": "Middle East", "field": "Politics",
        "title": "Coalition talks freeze in Israel",
        "deck": "Golan halts talks with Eisenkot as Likud presses a unity-government bid.",
        "pict": "court", "accent": GOLD,
    },
]

BRIEFS = [
    ("NEPAL", "Asia", "Disaster", "M5.6 quake hits Koshi near Tibet border."),
    ("UAE", "Middle East", "Disaster", "Bus-truck crash kills 13, injures 14."),
    ("HEALTH", "Global", "Health", "AIDS deaths 570,000, a 20-year low."),
    ("BANGLADESH", "Asia", "Politics", "Hasina plans return on 16 Dec."),
    ("MYANMAR", "Asia", "Politics", "Malaysia to return 6,500 Rohingya."),
    ("KOREA", "Asia", "Conflict", "Russian jets enter Seoul's defence zone."),
    ("NATO", "Europe", "Conflict", "Early-warning jets to deploy in Poland."),
    ("RUSSIA", "Europe", "Politics", "Duma passes record military budget."),
    ("RUSSIA", "Europe", "Law", "Murmansk governor held over bribes."),
    ("KENYA", "Africa", "Technology", "eCitizen users told to reset passwords."),
    ("LEBANON", "Middle East", "Politics", "Aoun: no vacuum after UNIFIL ends."),
    ("FOOTBALL", "Europe", "Sport", "Madrid 5-1 PSV; Bellingham goal."),
    ("FOOTBALL", "Europe", "Sport", "Man City 2-2 Napoli; late equaliser."),
    ("CRICKET", "Oceania", "Sport", "England beat Australia by 8 wickets."),
    ("FOOTBALL", "Africa", "Sport", "Senegal get AFCON title back."),
    ("COLOMBIA", "N. America", "Conflict", "Car bomb injures 23 in Cartagena."),
    ("INDONESIA", "Asia", "Politics", "Vice-president resigns amid strain."),
    ("AVIATION", "Asia", "Markets", "Xiamen Airlines orders 50 Boeing jets."),
    ("MARKETS", "N. America", "Markets", "Dell lifts forecasts on AI-server sales."),
    ("TRADE", "Global", "Markets", "Trump tariffs to hit India, China + 14."),
    ("USA", "N. America", "Law", "Fort Hood gunman seeks execution stay."),
    ("USA", "N. America", "Disaster", "Radar fault delays O'Hare flights."),
    ("CONGO", "Africa", "Conflict", "Rebels pull back from DR Congo areas."),
    ("CAMEROON", "Africa", "Law", "Separatist leader in Norway court."),
]

NUMBERS = [
    ("11", "wounded in the Houthi strike on Riyadh tower"),
    ("5", "soldiers killed in the Eskisehir helicopter crash"),
    ("13", "killed in the UAE bus-truck collision"),
    ("570,000", "AIDS deaths in 2025, lowest in 20+ years"),
    ("6,500", "Rohingya refugees Malaysia will return in Dec"),
    ("2,121", "migrants reach El Hierro in a day, a record"),
]

# lon, lat, label, dx, dy for the numbered pins on the world map
# (dx, dy) nudges the numbered circle off the true spot so neighbours do not collide
PINS = [
    (24.0, 60.0, "1", -16, -12),  # Gulf of Finland
    (46.7, 24.6, "2", 18, 10),    # Riyadh
    (56.5, 26.5, "3", 20, -10),   # Strait of Hormuz
    (34.5, 31.5, "4", -6, 16),    # Gaza
    (2.3, 48.9, "5", -20, 6),     # Paris
    (-77.0, 38.9, "6", 0, -16),   # Washington
    (100.3, 40.9, "7", 0, 0),     # Jiuquan
    (30.5, 39.8, "8", 16, -14),   # Eskisehir
]

# ---------------------------------------------------------------- pictograms
def pictogram(img, kind, x, y, w, h, ink, accent):
    tx, ty, tw, th = x, y, w, h
    tmp = Image.new("RGBA", (96, 72), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tmp)
    x = 0
    y = 0
    w = 96
    h = 72
    cx = x + w // 2
    cy = y + h // 2
    if kind == "ship":
        draw.polygon([(x + 8, cy + 12), (x + w - 8, cy + 12), (x + w - 20, cy + 26), (x + 20, cy + 26)], fill=ink)
        draw.rectangle([cx - 4, cy - 16, cx + 4, cy + 12], fill=ink)
        draw.polygon([(cx + 4, cy - 16), (cx + 26, cy - 4), (cx + 4, cy - 2)], fill=accent)
        draw.ellipse([x + w - 34, cy - 30, x + w - 14, cy - 10], fill=accent)
        draw.line([(x + 4, cy + 30), (x + w - 4, cy + 30)], fill=ink, width=2)
    elif kind == "rocket":
        draw.polygon([(cx, cy - 28), (cx + 10, cy - 6), (cx + 10, cy + 16), (cx, cy + 24), (cx - 10, cy + 16), (cx - 10, cy - 6)], fill=ink)
        draw.ellipse([cx - 4, cy - 16, cx + 4, cy - 8], fill=accent)
        draw.polygon([(cx - 10, cy + 8), (cx - 20, cy + 22), (cx - 10, cy + 16)], fill=accent)
        draw.polygon([(cx + 10, cy + 8), (cx + 20, cy + 22), (cx + 10, cy + 16)], fill=accent)
        for sx, sy in [(x + 10, y + 8), (x + w - 12, y + 12), (x + w - 16, y + h - 10), (x + 14, y + h - 14)]:
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=ink)
    elif kind == "chip":
        draw.rounded_rectangle([cx - 22, cy - 22, cx + 22, cy + 22], radius=4, fill=ink)
        draw.rectangle([cx - 11, cy - 11, cx + 11, cy + 11], fill=accent)
        for k in range(3):
            px = cx - 16 + k * 16
            draw.line([(px, cy - 30), (px, cy - 22)], fill=ink, width=3)
            draw.line([(px, cy + 22), (px, cy + 30)], fill=ink, width=3)
            py = cy - 16 + k * 16
            draw.line([(cx - 30, py), (cx - 22, py)], fill=ink, width=3)
            draw.line([(cx + 22, py), (cx + 30, py)], fill=ink, width=3)
        for k in range(3):
            bx = cx - 9 + k * 7
            bh = 14 - k * 4
            draw.rectangle([bx, cy + 10 - bh, bx + 4, cy + 10], fill=(255, 255, 255))
    elif kind == "tower":
        draw.polygon([(cx - 14, cy + 28), (cx - 6, cy - 28), (cx + 6, cy - 28), (cx + 14, cy + 28)], fill=ink)
        draw.rectangle([cx - 22, cy + 24, cx + 22, cy + 30], fill=ink)
        for k in range(4):
            wy = cy - 18 + k * 11
            draw.rectangle([cx - 4, wy, cx + 4, wy + 5], fill=accent)
        draw.ellipse([cx + 16, cy - 34, cx + 30, cy - 20], fill=accent)
        draw.line([(cx + 14, cy - 30), (cx + 24, cy - 24)], fill=accent, width=2)
    elif kind == "tanker":
        draw.polygon([(x + 6, cy + 6), (x + w - 6, cy + 6), (x + w - 14, cy + 24), (x + 14, cy + 24)], fill=ink)
        draw.rectangle([cx + 8, cy - 14, cx + 26, cy + 6], fill=ink)
        draw.rectangle([cx - 26, cy - 8, cx - 8, cy + 6], fill=accent)
        for mx, my in [(x + 12, cy - 22), (x + w - 18, cy - 24)]:
            draw.ellipse([mx - 4, my - 4, mx + 4, my + 4], outline=ink, width=2)
            draw.line([(mx - 7, my), (mx + 7, my)], fill=ink, width=1)
            draw.line([(mx, my - 7), (mx, my + 7)], fill=ink, width=1)
        draw.line([(x + 4, cy + 30), (x + w - 4, cy + 30)], fill=ink, width=2)
    elif kind == "city":
        for bx, bw, bh in [(x + 6, 14, 34), (x + 24, 18, 48), (x + 46, 14, 30), (x + 64, 18, 42)]:
            draw.rectangle([bx, cy + 28 - bh, bx + bw, cy + 28], fill=ink)
            draw.rectangle([bx + 3, cy + 28 - bh + 5, bx + bw - 3, cy + 28 - bh + 9], fill=accent)
        draw.ellipse([x + w - 26, cy - 28, x + w - 8, cy - 10], fill=accent)
    elif kind == "court":
        draw.rectangle([x + 8, cy - 26, x + w - 8, cy - 18], fill=ink)
        draw.polygon([(x + 8, cy - 26), (cx, cy - 34), (x + w - 8, cy - 26)], fill=ink)
        for k in range(4):
            px = x + 16 + k * 18
            draw.rectangle([px, cy - 16, px + 7, cy + 18], fill=ink)
        draw.rectangle([x + 8, cy + 18, x + w - 8, cy + 26], fill=ink)
        draw.ellipse([cx - 5, cy - 12, cx + 5, cy - 2], fill=accent)
    elif kind == "shield":
        draw.polygon([(cx, cy - 28), (cx + 22, cy - 18), (cx + 22, cy + 4), (cx, cy + 28), (cx - 22, cy + 4), (cx - 22, cy - 18)], fill=ink)
        draw.ellipse([cx - 7, cy - 10, cx + 7, cy + 4], outline=accent, width=3)
        draw.line([(cx, cy + 4), (cx, cy + 14)], fill=accent, width=3)
    elif kind == "medal":
        draw.ellipse([cx - 20, cy - 14, cx + 20, cy + 26], fill=ink)
        draw.ellipse([cx - 13, cy - 7, cx + 13, cy + 19], fill=accent)
        draw.polygon([(cx - 14, cy - 12), (cx - 4, cy - 30), (cx + 4, cy - 30), (cx + 14, cy - 12)], fill=RED)
        draw.text((cx - 4, cy - 2), "1", font=SANS_B(13), fill=(255, 255, 255))
    elif kind == "plane":
        draw.polygon([(x + 6, cy), (cx + 10, cy - 8), (x + w - 6, cy - 2), (cx + 4, cy + 4), (cx - 2, cy + 14), (cx - 8, cy + 4)], fill=ink)
        draw.polygon([(cx - 2, cy - 12), (cx + 8, cy - 26), (cx + 12, cy - 10)], fill=ink)
        draw.line([(x + 4, cy + 26), (x + w - 4, cy + 26)], fill=ink, width=2)
    elif kind == "derrick":
        draw.polygon([(cx - 16, cy + 28), (cx - 6, cy - 26), (cx + 6, cy - 26), (cx + 16, cy + 28)], fill=ink)
        draw.line([(cx - 10, cy + 8), (cx + 10, cy + 8)], fill=accent, width=3)
        draw.line([(cx - 13, cy - 6), (cx + 13, cy - 6)], fill=accent, width=3)
        draw.ellipse([cx + 14, cy - 32, cx + 28, cy - 18], fill=accent)
    elif kind == "heli":
        draw.ellipse([cx - 20, cy - 10, cx + 20, cy + 12], fill=ink)
        draw.rectangle([cx + 16, cy - 4, cx + 34, cy + 2], fill=ink)
        draw.line([(cx - 30, cy - 16), (cx + 30, cy - 16)], fill=ink, width=3)
        draw.line([(cx, cy - 16), (cx, cy - 10)], fill=ink, width=3)
        draw.line([(cx - 8, cy + 12), (cx - 12, cy + 24)], fill=ink, width=3)
        draw.line([(cx + 8, cy + 12), (cx + 12, cy + 24)], fill=ink, width=3)
        draw.ellipse([cx - 12, cy - 6, cx - 2, cy + 4], fill=accent)
    elif kind == "ballot":
        draw.rectangle([cx - 22, cy - 6, cx + 22, cy + 26], fill=ink)
        draw.rectangle([cx - 12, cy - 20, cx + 12, cy - 6], fill=ink)
        draw.line([(cx - 14, cy + 8), (cx - 4, cy + 18), (cx + 16, cy - 8)], fill=accent, width=4)
    tmp = tmp.resize((tw, th), Image.LANCZOS)
    img.paste(tmp, (tx, ty), tmp)


# ---------------------------------------------------------------- world map
CONTINENTS = [
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-112, 68), (-100, 69), (-95, 80), (-85, 80), (-76, 73), (-65, 62), (-55, 52), (-60, 46), (-70, 42), (-75, 35), (-80, 26), (-84, 30), (-90, 21), (-96, 16), (-104, 19), (-112, 24), (-117, 32), (-124, 40), (-124, 48), (-135, 58), (-150, 60), (-162, 58)],
    [(-44, 60), (-32, 68), (-22, 70), (-25, 76), (-45, 76), (-55, 74), (-58, 68), (-52, 64)],
    [(-79, 9), (-72, 12), (-62, 11), (-52, 5), (-44, 2), (-35, -8), (-38, -15), (-41, -23), (-48, -28), (-54, -34), (-58, -38), (-65, -41), (-68, -50), (-71, -54), (-74, -48), (-73, -38), (-72, -25), (-77, -12), (-81, -4), (-80, 2)],
    [(-17, 15), (-16, 21), (-10, 29), (-5, 35), (0, 36), (10, 37), (19, 32), (30, 31), (34, 28), (38, 22), (43, 12), (48, 11), (51, 11), (48, 2), (41, -5), (40, -12), (36, -19), (33, -26), (28, -33), (20, -35), (17, -30), (14, -22), (12, -17), (9, -4), (9, 4), (-8, 5), (-13, 9)],
    [(-10, 36), (-9, 43), (-4, 48), (-2, 50), (3, 53), (7, 55), (8, 57), (11, 59), (18, 56), (21, 55), (23, 58), (26, 59), (30, 62), (30, 65), (27, 68), (22, 70), (17, 69), (14, 67), (11, 64), (6, 62), (5, 58), (0, 51), (-5, 48), (-8, 43)],
    [(30, 62), (38, 67), (50, 69), (60, 69), (68, 72), (80, 73), (95, 75), (110, 76), (125, 73), (140, 72), (155, 70), (170, 67), (178, 65), (170, 60), (162, 56), (156, 51), (142, 50), (141, 44), (138, 38), (132, 34), (127, 38), (124, 33), (121, 28), (117, 23), (110, 20), (106, 10), (103, 7), (100, 8), (97, 14), (94, 17), (91, 22), (88, 22), (85, 19), (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (62, 25), (57, 26), (52, 28), (48, 29), (44, 30), (40, 36), (36, 36), (33, 38), (30, 41), (28, 45), (30, 55), (30, 62)],
    [(113, -22), (114, -29), (115, -34), (119, -34), (124, -33), (129, -32), (134, -33), (137, -35), (140, -38), (144, -39), (147, -39), (150, -37), (153, -27), (150, -22), (146, -19), (142, -11), (137, -12), (132, -11), (127, -14), (124, -15), (120, -19), (116, -21)],
]


def lonlat_to_xy(lon, lat, x0, y0, w, h):
    px = x0 + (lon + 180.0) / 360.0 * w
    py = y0 + (90.0 - lat) / 180.0 * h
    return (px, py)


def draw_map(draw, x0, y0, w, h):
    rounded(draw, [x0, y0, x0 + w, y0 + h], 6, fill=SEA)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, x0, y0, w, h) for lon, lat in poly]
        draw.polygon(pts, fill=LAND)
        draw.line(pts + [pts[0]], fill=LANDLINE, width=1)
    for lon, lat, num, dx, dy in PINS:
        px, py = lonlat_to_xy(lon, lat, x0, y0, w, h)
        qx, qy = px + dx, py + dy
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        draw.line([(px, py), (qx, qy)], fill=RED, width=1)
        draw.ellipse([qx - 9, qy - 9, qx + 9, qy + 9], fill=RED, outline=(255, 255, 255), width=2)
        tw = draw.textlength(num, font=SANS_B(11))
        draw.text((qx - tw / 2, qy - 6), num, font=SANS_B(11), fill=(255, 255, 255))

# ---------------------------------------------------------------- tallies
def tallies():
    regions = {}
    fields = {}
    for item in HEROES + CARDS:
        regions[item["region"]] = regions.get(item["region"], 0) + 1
        fields[item["field"]] = fields.get(item["field"], 0) + 1
    for _label, region, field, _text in BRIEFS:
        regions[region] = regions.get(region, 0) + 1
        fields[field] = fields.get(field, 0) + 1
    region_order = sorted(regions.items(), key=lambda kv: (-kv[1], kv[0]))
    field_order = sorted(fields.items(), key=lambda kv: (-kv[1], kv[0]))
    return region_order, field_order


def draw_tally(draw, x, y, w, title, items, total, bar_color):
    draw.text((x, y), title, font=SANS_B(12), fill=RED)
    yy = y + 20
    top = max(count for _name, count in items)
    for name, count in items:
        draw.text((x, yy), name, font=SANS(12), fill=INK)
        bar_x = x + 92
        bar_w = int((w - 92 - 30) * count / top)
        draw.rectangle([bar_x, yy + 2, bar_x + bar_w, yy + 12], fill=bar_color)
        num = str(count)
        draw.text((bar_x + bar_w + 6, yy), num, font=SANS_B(12), fill=INK)
        yy += 20
    return yy


def fit_text(draw, text, fnt, max_w):
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    words = text.split()
    kept = ""
    for word in words:
        trial = (kept + " " + word).strip()
        if draw.textlength(trial + " …", font=fnt) <= max_w:
            kept = trial
        else:
            break
    return kept + " …"


# ---------------------------------------------------------------- layout
def paint():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    total_stories = len(HEROES) + len(CARDS) + len(BRIEFS)

    # masthead
    draw.rectangle([0, 0, W, 5], fill=RED)
    draw.text((28, 20), "THE WORLD TODAY", font=SERIF_B(46), fill=INK)
    draw.text((28, 84), "ONE DAY  ·  ONE IMAGE  ·  THE NEWS THAT MATTERED", font=SANS_B(12), fill=SLATE)
    date_w = draw.textlength("25 NOVEMBER 2026", font=SERIF_B(30))
    draw.text((W - 28 - date_w, 22), "25 NOVEMBER 2026", font=SERIF_B(30), fill=RED)
    day_w = draw.textlength("WEDNESDAY", font=SANS_B(15))
    draw.text((W - 28 - day_w, 60), "WEDNESDAY", font=SANS_B(15), fill=INK)
    draw.text((W - 28 - day_w, 80), "39 STORIES · 6 REGIONS", font=SANS(11), fill=SLATE)
    draw.line([(28, 106), (W - 28, 106)], fill=RULE, width=2)
    draw.line([(28, 110), (W - 28, 110)], fill=RULE, width=1)

    # hero row
    hero_y = 116
    hero_h = 176
    hero_w = 317
    hero_gap = 8
    for idx, hero in enumerate(HEROES):
        hx = 28 + idx * (hero_w + hero_gap)
        rounded(draw, [hx, hero_y, hx + hero_w, hero_y + hero_h], 6, fill=PANEL, outline=RULE, width=1)
        pic_h = 74
        draw.rounded_rectangle([hx + 1, hero_y + 1, hx + hero_w - 1, hero_y + pic_h], radius=6, fill=hero["accent"])
        draw.rectangle([hx + 1, hero_y + pic_h - 12, hx + hero_w - 1, hero_y + pic_h], fill=hero["accent"])
        pictogram(img, hero["pict"], hx + 10, hero_y + 3, 90, 68, (255, 255, 255), (255, 255, 255))
        draw.text((hx + 108, hero_y + 14), "HERO " + str(idx + 1), font=SANS_B(11), fill=(255, 255, 255))
        draw_wrapped(draw, hero["tag"], SANS_B(12), hx + 108, hero_y + 32, hero_w - 120, (255, 255, 255))
        draw.text((hx + 108, hero_y + 52), "PIN " + str(hero["pin"]) + " ON THE MAP", font=SANS(10), fill=(235, 235, 235))
        ty = hero_y + pic_h + 10
        draw_wrapped(draw, hero["title"], SERIF_B(19), hx + 12, ty, hero_w - 24, INK, leading=22, max_lines=2)
        draw_wrapped(draw, hero["deck"], SANS(12), hx + 12, ty + 48, hero_w - 24, (60, 58, 52), leading=14, max_lines=3)

    # map band + tallies
    band_y = 300
    band_h = 132
    map_x, map_w = 28, 540
    draw_map(draw, map_x, band_y, map_w, band_h - 16)
    draw.text((map_x, band_y + band_h - 13), "PINNED: 1 GULF OF FINLAND  2 RIYADH  3 HORMUZ  4 GAZA  5 PARIS  6 WASHINGTON  7 JIUQUAN  8 ESKISEHIR",
              font=SANS(10), fill=SLATE)
    region_order, field_order = tallies()
    tx = 592
    draw_tally(draw, tx, band_y, 190, "BY REGION", region_order[:5], total_stories, NAVY)
    draw_tally(draw, tx + 210, band_y, 190, "BY SUBJECT", field_order[:5], total_stories, TEAL)

    # cards grid
    grid_y = 436
    card_w = 236
    card_h = 100
    gap = 8
    for idx, card in enumerate(CARDS):
        row = idx // 4
        col = idx % 4
        cx = 28 + col * (card_w + gap)
        cy = grid_y + row * (card_h + gap)
        rounded(draw, [cx, cy, cx + card_w, cy + card_h], 5, fill=PANEL, outline=(200, 192, 175), width=1)
        pic_h = 38
        draw.rounded_rectangle([cx + 1, cy + 1, cx + card_w - 1, cy + pic_h], radius=5, fill=card["accent"])
        draw.rectangle([cx + 1, cy + pic_h - 10, cx + card_w - 1, cy + pic_h], fill=card["accent"])
        pictogram(img, card["pict"], cx + 6, cy + 2, 48, 34, (255, 255, 255), (255, 255, 255))
        draw.text((cx + 62, cy + 8), card["tag"], font=SANS_B(11), fill=(255, 255, 255))
        pin_note = ""
        if card["pin"]:
            pin_note = "  ·  PIN " + str(card["pin"])
        draw.text((cx + 62, cy + 24), card["region"].upper() + " · " + card["field"].upper() + pin_note,
                  font=SANS(9), fill=(235, 235, 235))
        ty = cy + pic_h + 6
        draw_wrapped(draw, card["title"], SANS_B(13), cx + 8, ty, card_w - 16, INK, leading=14, max_lines=2)
        draw_wrapped(draw, card["deck"], SANS(11), cx + 8, ty + 28, card_w - 16, (60, 58, 52), leading=12, max_lines=2)

    # day in numbers
    num_y = 760
    num_h = 58
    rounded(draw, [28, num_y, W - 28, num_y + num_h], 6, fill=NAVY)
    draw.text((44, num_y + 8), "THE DAY", font=SANS_B(11), fill=(255, 255, 255))
    draw.text((44, num_y + 24), "IN NUMBERS", font=SANS_B(11), fill=(255, 255, 255))
    seg_w = (W - 28 - 170) // 6
    for idx, (big, label) in enumerate(NUMBERS):
        sx = 28 + 170 + idx * seg_w
        if idx:
            draw.line([(sx - 6, num_y + 8), (sx - 6, num_y + num_h - 8)], fill=(120, 140, 170), width=1)
        draw.text((sx, num_y + 5), big, font=SANS_B(20), fill=GOLD)
        draw_wrapped(draw, label, SANS(9), sx, num_y + 28, seg_w - 12, (225, 230, 238), leading=11, max_lines=2)

    # briefs
    brief_y = 822
    draw.text((28, brief_y), "THE REST OF THE DAY", font=SANS_B(13), fill=RED)
    draw.line([(28, brief_y + 20), (W - 28, brief_y + 20)], fill=RULE, width=1)
    col_w = 316
    for idx, (label, _region, _field, text) in enumerate(BRIEFS):
        col = idx // 8
        row = idx % 8
        bx = 28 + col * (col_w + 8)
        by = brief_y + 26 + row * 18
        draw.text((bx, by), str(idx + 1).rjust(2) + ".", font=MONO_B(11), fill=RED)
        draw.text((bx + 24, by), label + " — ", font=SANS_B(11), fill=INK)
        lw = draw.textlength(label + " — ", font=SANS_B(11))
        fitted = fit_text(draw, text, SANS(11), col_w - 24 - lw)
        draw.text((bx + 24 + lw, by), fitted, font=SANS(11), fill=(60, 58, 52))

    # footer
    draw.line([(28, 1000), (W - 28, 1000)], fill=RULE, width=1)
    draw.text((28, 1006), "SOURCES: REUTERS · AP · THE HEAR FRONT PAGES · 25 NOVEMBER 2026",
              font=SANS(10), fill=SLATE)
    draw.text((W - 28 - draw.textlength("THE WORLD TODAY — 25 NOV 2026", font=SANS_B(10)), 1006),
              "THE WORLD TODAY — 25 NOV 2026", font=SANS_B(10), fill=SLATE)

    img.save(OUT, format="PNG", optimize=True)
    size = os.path.getsize(OUT)
    print("wrote", OUT, size, "bytes", img.size)
    return size


if __name__ == "__main__":
    paint()

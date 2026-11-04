"""LessBill Pinterest cover (1000x1500) with a different look every day.

Usage:
  python3 tools/make_lessbill_cover.py "Headline" "Subtitle" covers/YYYY-MM-DD-slug.jpg \
      [--icon NAME] [--palette NAME] [--layout NAME] [--stat "92%"] [--tag "TEXT"]

Defaults: palette and layout rotate by the date in the file name, so consecutive
days never share a look. --icon should match the topic:
  gpu, server, cloud, coins, pods, network, storage, chart, bell, tag, robot, gauge
--stat puts a big number on the cover (used by the "stat" layout; optional).
"""
import argparse, datetime, hashlib, math, os, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1000, 1500
F = "/usr/share/fonts/opentype/inter/"

# bg top, bg bottom, accent, accent2, text, muted, line
PALETTES = {
    "midnight": ((11, 22, 48), (20, 40, 82), (45, 212, 191), (255, 107, 91), (255, 255, 255), (190, 196, 215), (40, 62, 105)),
    "forest":   ((8, 38, 32), (14, 70, 56), (163, 230, 53), (250, 204, 21), (255, 255, 255), (186, 214, 200), (30, 90, 72)),
    "sunset":   ((60, 16, 40), (140, 40, 50), (255, 183, 77), (255, 255, 255), (255, 255, 255), (250, 210, 200), (120, 50, 70)),
    "paper":    ((248, 244, 236), (236, 228, 214), (232, 76, 61), (20, 120, 110), (22, 28, 45), (90, 96, 112), (210, 200, 185)),
    "violet":   ((30, 18, 70), (70, 30, 120), (129, 230, 217), (244, 114, 182), (255, 255, 255), (205, 195, 235), (75, 55, 130)),
    "ocean":    ((6, 52, 84), (8, 100, 140), (255, 214, 102), (255, 255, 255), (255, 255, 255), (190, 225, 240), (30, 110, 150)),
    "charcoal": ((24, 24, 27), (39, 39, 42), (250, 204, 21), (59, 130, 246), (255, 255, 255), (180, 180, 190), (63, 63, 70)),
    "mint":     ((225, 245, 238), (200, 235, 222), (15, 118, 110), (234, 88, 12), (15, 40, 40), (70, 100, 95), (170, 215, 200)),
}
LAYOUTS = ["top", "bottom", "stat", "split"]
ICONS = ["gpu", "server", "cloud", "coins", "pods", "network", "storage", "chart", "bell", "tag", "robot", "gauge"]


def font(w, s): return ImageFont.truetype(F + f"Inter-{w}.otf", s)


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    return lines


def fit(d, text, weight, start, maxw, maxlines):
    s = start
    while s > 30:
        f = font(weight, s); ls = wrap(d, text, f, maxw)
        if len(ls) <= maxlines and all(d.textlength(l, font=f) <= maxw for l in ls): return f, ls
        s -= 4
    return f, ls


# ---------- icons: drawn in a box (cx, cy, size) ----------
def icon(d, name, cx, cy, s, A, B, L, T):
    h = s / 2
    if name == "gpu":
        d.rounded_rectangle([cx-h, cy-h*.6, cx+h, cy+h*.6], 24, fill=L, outline=A, width=6)
        for i in range(2):
            fx = cx - h*.45 + i*h*.9
            d.ellipse([fx-h*.32, cy-h*.32, fx+h*.32, cy+h*.32], outline=A, width=6)
            for k in range(6):
                a = k*math.pi/3
                d.line([fx, cy, fx+math.cos(a)*h*.28, cy+math.sin(a)*h*.28], fill=A, width=5)
        for i in range(8):
            x = cx - h*.8 + i*h*.23
            d.rectangle([x, cy+h*.6, x+h*.12, cy+h*.75], fill=B)
    elif name == "server":
        for i in range(3):
            y = cy - h + i*h*.7
            d.rounded_rectangle([cx-h, y, cx+h, y+h*.55], 16, fill=L, outline=A, width=5)
            d.ellipse([cx+h*.6, y+h*.2, cx+h*.75, y+h*.35], fill=B if i == 1 else A)
            for k in range(4):
                d.line([cx-h*.8+k*h*.15, y+h*.15, cx-h*.8+k*h*.15, y+h*.4], fill=A, width=5)
    elif name == "cloud":
        d.ellipse([cx-h, cy-h*.1, cx-h*.2, cy+h*.6], fill=A)
        d.ellipse([cx-h*.55, cy-h*.6, cx+h*.35, cy+h*.4], fill=A)
        d.ellipse([cx, cy-h*.3, cx+h, cy+h*.6], fill=A)
        d.rectangle([cx-h*.6, cy+h*.1, cx+h*.6, cy+h*.6], fill=A)
        d.text((cx, cy+h*.15), "$", font=font("Black", int(s*.32)), fill=B, anchor="mm")
    elif name == "coins":
        for i in range(5):
            y = cy + h*.5 - i*h*.25
            d.ellipse([cx-h*.9, y-h*.12, cx+h*.1, y+h*.12], fill=A, outline=L, width=4)
        d.ellipse([cx, cy-h*.6, cx+h, cy+h*.4], fill=B, outline=A, width=6)
        d.text((cx+h*.5, cy-h*.1), "$", font=font("Black", int(s*.35)), fill=L, anchor="mm")
    elif name == "pods":
        for r in range(3):
            for c in range(3 - (r % 2)):
                x = cx - h*.7 + c*h*.7 + (h*.35 if r % 2 else 0); y = cy - h*.6 + r*h*.6
                pts = [(x+math.cos(math.pi/6+k*math.pi/3)*h*.32, y+math.sin(math.pi/6+k*math.pi/3)*h*.32) for k in range(6)]
                d.polygon(pts, fill=A if (r+c) % 3 else B, outline=L)
    elif name == "network":
        nodes = [(cx, cy-h*.8), (cx-h*.8, cy), (cx+h*.8, cy), (cx-h*.4, cy+h*.8), (cx+h*.4, cy+h*.8), (cx, cy)]
        for a in nodes[:-1]: d.line([a, nodes[-1]], fill=A, width=6)
        d.line([nodes[1], nodes[3]], fill=A, width=4); d.line([nodes[2], nodes[4]], fill=A, width=4)
        for i, (x, y) in enumerate(nodes):
            r = h*.2 if i == 5 else h*.13
            d.ellipse([x-r, y-r, x+r, y+r], fill=B if i == 5 else A)
    elif name == "storage":
        for i in range(3):
            y = cy - h*.7 + i*h*.5
            d.rectangle([cx-h*.8, y, cx+h*.8, y+h*.5], fill=L, outline=A, width=5)
            d.ellipse([cx-h*.8, y-h*.15, cx+h*.8, y+h*.15], fill=A if i else B, outline=A, width=5)
        d.ellipse([cx-h*.8, cy+h*.65, cx+h*.8, cy+h*.95], fill=L, outline=A, width=5)
    elif name == "chart":
        for i, v in enumerate([.35, .5, .45, .7, 1.0]):
            x = cx - h + i*h*.42
            d.rounded_rectangle([x, cy+h-v*h*1.8, x+h*.3, cy+h], 8, fill=B if i == 4 else A)
        d.line([cx-h, cy+h, cx+h, cy+h], fill=L, width=5)
    elif name == "bell":
        d.chord([cx-h*.7, cy-h*.9, cx+h*.7, cy+h*.5], 180, 360, fill=A)
        d.polygon([(cx-h*.7, cy-h*.2), (cx+h*.7, cy-h*.2), (cx+h*.9, cy+h*.5), (cx-h*.9, cy+h*.5)], fill=A)
        d.ellipse([cx-h*.18, cy+h*.45, cx+h*.18, cy+h*.8], fill=B)
        for r in (h*1.05, h*1.25):
            d.arc([cx-r, cy-r-h*.2, cx+r, cy+r-h*.2], 300, 350, fill=B, width=6)
            d.arc([cx-r, cy-r-h*.2, cx+r, cy+r-h*.2], 190, 240, fill=B, width=6)
    elif name == "tag":
        pts = [(cx-h*.9, cy-h*.5), (cx+h*.4, cy-h*.5), (cx+h*.9, cy), (cx+h*.4, cy+h*.5), (cx-h*.9, cy+h*.5)]
        d.polygon(pts, fill=A); d.ellipse([cx+h*.2, cy-h*.1, cx+h*.4, cy+h*.1], fill=L)
        d.text((cx-h*.3, cy), "%", font=font("Black", int(s*.4)), fill=B, anchor="mm")
    elif name == "robot":
        d.rounded_rectangle([cx-h*.8, cy-h*.5, cx+h*.8, cy+h*.7], 30, fill=A)
        d.line([cx, cy-h*.5, cx, cy-h*.85], fill=A, width=8); d.ellipse([cx-h*.1, cy-h, cx+h*.1, cy-h*.8], fill=B)
        for x in (cx-h*.35, cx+h*.35): d.ellipse([x-h*.15, cy-h*.15, x+h*.15, cy+h*.15], fill=L)
        d.rounded_rectangle([cx-h*.4, cy+h*.3, cx+h*.4, cy+h*.45], 8, fill=B)
    elif name == "gauge":
        d.arc([cx-h, cy-h, cx+h, cy+h], 180, 250, fill=A, width=int(s*.1))
        d.arc([cx-h, cy-h, cx+h, cy+h], 250, 310, fill=T, width=int(s*.1))
        d.arc([cx-h, cy-h, cx+h, cy+h], 310, 360, fill=B, width=int(s*.1))
        a = math.radians(330); d.line([cx, cy, cx+math.cos(a)*h*.8, cy+math.sin(a)*h*.8], fill=T, width=10)
        d.ellipse([cx-h*.1, cy-h*.1, cx+h*.1, cy+h*.1], fill=T)


def bg(P, seed):
    top, bot = P[0], P[1]
    img = Image.new("RGB", (W, H), top); d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H; d.line([(0, y), (W, y)], fill=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3)))
    # soft decorative shapes, varied by seed
    deco = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(deco)
    kind = seed % 3
    if kind == 0:
        for i in range(6): g.ellipse([700-i*30, -200+i*20, 1300-i*30, 400+i*20], outline=P[6] + (110,), width=3)
    elif kind == 1:
        for x in range(-H, W, 70): g.line([(x, H), (x+H, 0)], fill=P[6] + (60,), width=2)
    else:
        for x in range(40, W, 60):
            for y in range(40, H, 60): g.ellipse([x-3, y-3, x+3, y+3], fill=P[6] + (120,))
    deco = deco.filter(ImageFilter.GaussianBlur(1))
    img.paste(deco, (0, 0), deco)
    return img


def text_block(d, P, tag, title, sub, x, y, maxw, tsize=92, tlines=4):
    tf = font("SemiBold", 26); tw = d.textlength(tag, font=tf)
    d.rounded_rectangle([x, y, x+tw+44, y+50], 25, fill=P[2])
    d.text((x+22, y+25), tag, font=tf, fill=P[0] if sum(P[0]) < 300 else (255, 255, 255), anchor="lm")
    y += 100
    f, ls = fit(d, title, "ExtraBold", tsize, maxw, tlines)
    for l in ls: d.text((x, y), l, font=f, fill=P[4]); y += int(f.size*1.12)
    sf, sl = fit(d, sub, "Medium", 42, maxw, 3); y += 24
    for l in sl: d.text((x, y), l, font=sf, fill=P[5]); y += int(sf.size*1.3)
    return y


def footer(d, P):
    d.line([(80, 1385), (W-80, 1385)], fill=P[6], width=2)
    d.text((80, 1430), "LessBill.org", font=font("Bold", 40), fill=P[2], anchor="lm")
    d.text((W-80, 1430), "Cut cloud waste", font=font("Medium", 28), fill=P[5], anchor="rm")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("title"); ap.add_argument("subtitle"); ap.add_argument("out")
    ap.add_argument("--icon"); ap.add_argument("--palette"); ap.add_argument("--layout")
    ap.add_argument("--stat"); ap.add_argument("--tag", default="CLOUD COST GUIDE")
    a = ap.parse_args()

    m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(a.out))
    day = datetime.date.fromisoformat(m.group(1)) if m else datetime.date.today()
    n = day.toordinal()
    pal = a.palette or list(PALETTES)[n % len(PALETTES)]
    lay = a.layout or LAYOUTS[(n // 2 + n) % len(LAYOUTS)]
    if lay == "stat" and not a.stat:
        nums = re.findall(r"(?<![A-Za-z\d])(\$\d[\d,.]*[KMB]?|\d[\d,.]*(?:%|x\b))", a.title)
        if nums: a.stat = nums[0]
        else: lay = "split"
    ic = a.icon or ICONS[int(hashlib.md5(a.title.encode()).hexdigest(), 16) % len(ICONS)]
    P = PALETTES[pal]; A, B, L, T = P[2], P[3], P[6], P[4]

    img = bg(P, n); d = ImageDraw.Draw(img)
    tag = a.tag.upper()
    if lay == "top":
        text_block(d, P, tag, a.title, a.subtitle, 80, 90, W-160)
        d.ellipse([250, 830, 750, 1330], fill=L); icon(d, ic, 500, 1080, 300, A, B, P[0], T)
    elif lay == "bottom":
        d.ellipse([280, 80, 720, 520], fill=L); icon(d, ic, 500, 300, 260, A, B, P[0], T)
        text_block(d, P, tag, a.title, a.subtitle, 80, 640, W-160, tsize=84, tlines=4)
    elif lay == "stat":
        sf = font("Black", 300)
        while d.textlength(a.stat, font=sf) > W-160: sf = font("Black", sf.size-20)
        d.text((80, 140), a.stat, font=sf, fill=A)
        d.rectangle([80, 140+sf.size+40, 280, 140+sf.size+52], fill=B)
        text_block(d, P, tag, a.title, a.subtitle, 80, 140+sf.size+100, W-160, tsize=72, tlines=4)
        icon(d, ic, 700, 1110, 360, A, B, L, T)
    else:  # split: colored panel with icon on top, text below
        d.rounded_rectangle([60, 60, W-60, 620], 40, fill=A)
        icon(d, ic, 500, 340, 300, P[0], B, A, P[0])
        text_block(d, P, tag, a.title, a.subtitle, 80, 690, W-160, tsize=80, tlines=4)
    footer(d, P)
    img.save(a.out, quality=88, optimize=True)
    print(f"palette={pal} layout={lay} icon={ic}")


if __name__ == "__main__":
    main()

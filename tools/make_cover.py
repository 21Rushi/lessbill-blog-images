"""Pinterest cover (1000x1500).

Usage: python3 make_cover.py "Title" "Subtitle" out.jpg [lessbill|bft] ["TAG TEXT"]
  lessbill (default): LessBill cloud-cost style (navy/teal, cost-spike chart)
  bft: Blog For Today trending style (plum/amber, trend graphic)
"""
import sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1000, 1500
F = "/usr/share/fonts/opentype/inter/"
WHITE, MUTED = (255, 255, 255), (190, 196, 215)

BRANDS = {
    "lessbill": dict(bg=((11, 22, 48), (20, 40, 82)), glow=(35, 90, 120), grid=(40, 62, 105),
                     a=(45, 212, 191), b=(255, 107, 91), tag="CLOUD COST GUIDE",
                     name="LessBill.org", right="Cut cloud waste"),
    "bft": dict(bg=((24, 16, 40), (60, 22, 66)), glow=(120, 40, 90), grid=(70, 44, 92),
                a=(255, 190, 60), b=(255, 84, 128), tag="TRENDING NOW",
                name="Blog For Today", right="21stbirthd.blogspot.com"),
}


def font(w, s): return ImageFont.truetype(F + f"Inter-{w}.otf", s)


def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    return lines


def fit(d, text, weight, start, maxw, maxlines):
    s = start
    while s > 30:
        f = font(weight, s); ls = wrap(d, text, f, maxw)
        if len(ls) <= maxlines: return f, ls
        s -= 4
    return f, ls


def draw_chart(d, B, seed):
    for x in range(80, W - 60, 84): d.line([(x, 900), (x, 1300)], fill=B["grid"], width=1)
    for y in range(900, 1301, 80): d.line([(80, y), (W - 80, y)], fill=B["grid"], width=1)
    random.seed(seed)
    pts, x = [], 80
    while x <= W - 80:
        base = 1230 - (x - 80) * 0.12 + random.randint(-18, 18)
        if x > W - 260: base -= (x - (W - 260)) * 1.9
        pts.append((x, base)); x += 40
    d.line(pts, fill=B["a"], width=8, joint="curve")
    px, py = pts[-1]
    d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=B["b"])
    cx, cy = 500, 830
    for r in (150, 115, 82):
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=B["b"], width=6)
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=B["b"])
    d.text((cx, cy + 2), "$", font=font("Bold", 64), fill=WHITE, anchor="mm")


def draw_trend(d, B, seed):
    cx, cy = 500, 1060
    for i, r in enumerate((300, 240, 180, 120)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=B["grid"] if i % 2 else B["b"], width=4)
    pts = [(250, 1220), (400, 1110), (500, 1160), (720, 930)]
    d.line(pts, fill=B["a"], width=14, joint="curve")
    d.polygon([(770, 880), (690, 900), (750, 965)], fill=B["a"])
    for x, y in pts[:-1]:
        d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=B["b"])


def main(title, subtitle, out, brand="lessbill", tag=None):
    B = BRANDS[brand]
    top, bot = B["bg"]
    img = Image.new("RGB", (W, H), top)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    glow = Image.new("RGB", (W, H), (0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse([200, 760, 800, 1360], fill=B["glow"])
    mask = glow.convert("L").point(lambda p: 255 if p else 0)
    img = Image.blend(img, Image.composite(glow, img, mask).filter(ImageFilter.GaussianBlur(120)), 0.6)
    d = ImageDraw.Draw(img)

    (draw_trend if brand == "bft" else draw_chart)(d, B, len(title))

    tf = font("SemiBold", 26)
    tag = (tag or B["tag"]).upper()
    tw = d.textlength(tag, font=tf)
    d.rounded_rectangle([80, 90, 80 + tw + 44, 140], 25, fill=B["a"])
    d.text((80 + 22, 115), tag, font=tf, fill=top, anchor="lm")

    tfnt, tlines = fit(d, title, "ExtraBold", 92, W - 160, 4)
    y = 190
    for ln in tlines:
        d.text((80, y), ln, font=tfnt, fill=WHITE); y += int(tfnt.size * 1.12)
    sf, slines = fit(d, subtitle, "Medium", 42, W - 160, 3)
    y += 24
    for ln in slines:
        d.text((80, y), ln, font=sf, fill=MUTED); y += int(sf.size * 1.3)

    d.line([(80, 1385), (W - 80, 1385)], fill=B["grid"], width=2)
    d.text((80, 1430), B["name"], font=font("Bold", 40), fill=B["a"], anchor="lm")
    d.text((W - 80, 1430), B["right"], font=font("Medium", 28), fill=MUTED, anchor="rm")
    img.save(out, quality=88, optimize=True)


if __name__ == "__main__":
    main(*sys.argv[1:6])

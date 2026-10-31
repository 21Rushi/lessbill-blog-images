"""LessBill Pinterest cover (1000x1500). Usage: python3 make_cover.py "Title" "Subtitle" out.jpg"""
import sys, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1000, 1500
F = "/usr/share/fonts/opentype/inter/"
NAVY, NAVY2 = (11, 22, 48), (20, 40, 82)
TEAL, CORAL, WHITE, MUTED = (45, 212, 191), (255, 107, 91), (255, 255, 255), (170, 185, 210)

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

def main(title, subtitle, out):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    for y in range(H):  # vertical gradient
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(NAVY[i] + (NAVY2[i] - NAVY[i]) * t) for i in range(3)))
    # soft glow
    glow = Image.new("RGB", (W, H), (0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse([200, 760, 800, 1360], fill=(35, 90, 120))
    img = Image.blend(img, Image.composite(glow, img, glow.convert("L").point(lambda p: 255 if p else 0)).filter(ImageFilter.GaussianBlur(120)), 0.6)
    d = ImageDraw.Draw(img)
    # grid
    for x in range(80, W - 60, 84): d.line([(x, 900), (x, 1300)], fill=(40, 62, 105), width=1)
    for y in range(900, 1301, 80): d.line([(80, y), (W - 80, y)], fill=(40, 62, 105), width=1)
    # cost line with spike
    random.seed(len(title))
    pts, x = [], 80
    while x <= W - 80:
        base = 1230 - (x - 80) * 0.12 + random.randint(-18, 18)
        if x > W - 260: base -= (x - (W - 260)) * 1.9
        pts.append((x, base)); x += 40
    d.line(pts, fill=TEAL, width=8, joint="curve")
    px, py = pts[-1]
    d.ellipse([px - 16, py - 16, px + 16, py + 16], fill=CORAL)
    # alert badge
    cx, cy = 500, 830
    for r, a in [(150, 40), (115, 70), (82, 110)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=CORAL + (a,), width=6)
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=CORAL)
    d.text((cx, cy + 2), "$", font=font("Bold", 64), fill=WHITE, anchor="mm")
    # tag
    tf = font("SemiBold", 26)
    tag = "CLOUD COST GUIDE"
    tw = d.textlength(tag, font=tf)
    d.rounded_rectangle([80, 90, 80 + tw + 44, 140], 25, fill=TEAL)
    d.text((80 + 22, 115), tag, font=tf, fill=NAVY, anchor="lm")
    # title
    tfnt, tlines = fit(d, title, "ExtraBold", 92, W - 160, 4)
    y = 190
    for ln in tlines:
        d.text((80, y), ln, font=tfnt, fill=WHITE); y += int(tfnt.size * 1.12)
    # subtitle
    sf, slines = fit(d, subtitle, "Medium", 42, W - 160, 3)
    y += 24
    for ln in slines:
        d.text((80, y), ln, font=sf, fill=MUTED); y += int(sf.size * 1.3)
    # footer
    d.line([(80, 1385), (W - 80, 1385)], fill=(50, 75, 120), width=2)
    d.text((80, 1430), "LessBill.org", font=font("Bold", 40), fill=TEAL, anchor="lm")
    d.text((W - 80, 1430), "Cut cloud waste", font=font("Medium", 30), fill=MUTED, anchor="rm")
    img.save(out, quality=88, optimize=True)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1400
FONT_DIRS = ["/System/Library/Fonts/Supplemental", "/usr/share/fonts/truetype/dejavu"]
BOLD = ["Arial Bold.ttf", "DejaVuSans-Bold.ttf"]
BOOK = ["Arial.ttf", "DejaVuSans.ttf"]


def font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = Path(d) / n
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def gradient():
    img = Image.new("RGB", (SIZE, SIZE))
    draw = ImageDraw.Draw(img)
    top, bottom = (14, 22, 48), (6, 8, 18)
    for y in range(SIZE):
        f = y / SIZE
        draw.line([(0, y), (SIZE, y)], fill=tuple(int(top[i] + (bottom[i] - top[i]) * f) for i in range(3)))
    return img


def centered(draw, y, text, font, fill):
    w = draw.textlength(text, font=font)
    draw.text(((SIZE - w) / 2, y), text, font=font, fill=fill)


def court(draw, left, top, width):
    scale = width / 6.4
    line = (235, 240, 250)
    lw = 6
    x = lambda m: left + m * scale
    y = lambda m: top + m * scale
    draw.rectangle([x(0), y(0), x(6.4), y(9.75)], outline=line, width=lw)
    draw.line([x(0), y(5.44), x(6.4), y(5.44)], fill=line, width=lw)
    draw.line([x(3.2), y(5.44), x(3.2), y(9.75)], fill=line, width=lw)
    for x0, x1 in ((0, 1.6), (4.8, 6.4)):
        draw.rectangle([x(x0), y(5.44), x(x1), y(7.04)], outline=line, width=lw)
    ball = (255, 150, 40)
    path = [(1.2, 8.6), (0.55, 0.0), (0.55, 8.8)]
    draw.line([(x(a), y(b)) for a, b in path], fill=ball, width=8)
    r = 20
    for a, b in ((0.55, 0.0), (0.55, 8.8)):
        draw.ellipse([x(a) - r, y(b) - r, x(a) + r, y(b) + r], fill=ball)


def make(subtitle, footer, path):
    img = gradient()
    draw = ImageDraw.Draw(img)
    court(draw, 500, 545, 400)
    centered(draw, 130, "SQUASH", font(BOLD, 190), (255, 255, 255))
    centered(draw, 340, "SOLO ROUTINE", font(BOLD, 96), (255, 150, 40))
    centered(draw, 1250, subtitle, font(BOOK, 56), (220, 228, 240))
    centered(draw, 1325, footer, font(BOOK, 40), (160, 170, 195))
    img.save(path, quality=92)

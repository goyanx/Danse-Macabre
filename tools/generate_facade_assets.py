from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "game" / "images"
GUI = ROOT / "game" / "gui"


W, H = 1920, 1080


def gradient(size, top, bottom):
    img = Image.new("RGB", size, top)
    pix = img.load()
    for y in range(size[1]):
        t = y / max(1, size[1] - 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(size[0]):
            pix[x, y] = color
    return img


def save_bg(name, img):
    img.save(IMAGES / name)


def draw_window_wall(draw, x0, y0, x1, y1, glow):
    draw.rectangle((x0, y0, x1, y1), fill=(18, 23, 32), outline=(185, 171, 140), width=4)
    for i in range(1, 4):
        x = x0 + (x1 - x0) * i // 4
        draw.line((x, y0, x, y1), fill=(78, 91, 111), width=3)
    draw.rectangle((x0 + 12, y0 + 12, x1 - 12, y1 - 12), outline=glow, width=2)


def street():
    img = gradient((W, H), (18, 28, 43), (6, 9, 16))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 760, W, H), fill=(22, 22, 25))
    draw.polygon([(1060, 260), (1680, 210), (1810, 760), (920, 760)], fill=(45, 44, 48))
    draw.polygon([(1120, 300), (1600, 260), (1690, 730), (1000, 730)], fill=(24, 25, 29))
    draw.rectangle((1260, 410, 1430, 735), fill=(169, 143, 96))
    draw.rectangle((1285, 435, 1405, 735), fill=(23, 20, 22))
    for x in (1030, 1210, 1460, 1630):
        draw_window_wall(draw, x, 350, x + 130, 520, (206, 183, 124))
    draw.ellipse((1410, 545, 1442, 577), fill=(230, 199, 118))
    draw.rectangle((0, 735, W, 800), fill=(15, 16, 18))
    draw.line((0, 805, W, 750), fill=(79, 82, 91), width=5)
    img = img.filter(ImageFilter.GaussianBlur(0.2))
    save_bg("bg facade street.png", img)


def salon():
    img = gradient((W, H), (53, 44, 50), (23, 23, 30))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 720, W, H), fill=(58, 46, 40))
    draw.rectangle((80, 160, 1840, 730), fill=(44, 39, 43))
    draw.rectangle((730, 190, 1190, 530), fill=(34, 31, 35), outline=(214, 186, 128), width=12)
    draw.line((955, 190, 975, 530), fill=(201, 211, 224), width=4)
    draw.line((705, 165, 1215, 555), fill=(116, 121, 132), width=3)
    draw.rectangle((210, 565, 600, 720), fill=(94, 54, 55))
    draw.rectangle((1230, 575, 1690, 720), fill=(34, 34, 37))
    draw.rectangle((1320, 520, 1610, 580), fill=(91, 74, 55))
    for x in (1375, 1460, 1545):
        draw.polygon([(x, 500), (x + 20, 500), (x + 12, 550), (x + 8, 550)], fill=(219, 223, 224))
        draw.rectangle((x + 7, 550, x + 14, 572), fill=(219, 223, 224))
    draw.ellipse((250, 410, 390, 560), fill=(201, 176, 117))
    draw.rectangle((160, 695, 1760, 730), fill=(145, 110, 68))
    save_bg("bg facade salon.png", img)


def kitchen():
    img = gradient((W, H), (35, 48, 52), (16, 21, 23))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 690, W, H), fill=(34, 36, 36))
    draw.rectangle((180, 500, 1740, 750), fill=(76, 78, 75))
    draw.rectangle((220, 360, 680, 620), fill=(34, 38, 39), outline=(178, 178, 160), width=5)
    draw.rectangle((760, 270, 1570, 620), fill=(26, 29, 31), outline=(174, 151, 103), width=4)
    draw.rectangle((850, 565, 1470, 620), fill=(103, 96, 86))
    for x in (900, 1010, 1120):
        draw.polygon([(x, 472), (x + 24, 472), (x + 16, 542), (x + 8, 542)], fill=(210, 218, 220))
        draw.rectangle((x + 8, 542, x + 16, 576), fill=(210, 218, 220))
    draw.ellipse((1380, 420, 1515, 555), fill=(172, 106, 67))
    draw.arc((1340, 380, 1560, 600), 200, 335, fill=(223, 188, 113), width=6)
    draw.rectangle((0, 748, W, 775), fill=(126, 113, 96))
    save_bg("bg facade kitchen.png", img)


def study():
    img = gradient((W, H), (44, 35, 47), (16, 14, 20))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 700, W, H), fill=(39, 31, 28))
    draw.rectangle((250, 170, 720, 700), fill=(42, 27, 26))
    for i in range(8):
        y = 215 + i * 55
        draw.rectangle((280, y, 690, y + 25), fill=(87, 62, 50))
    draw.rectangle((950, 540, 1640, 755), fill=(84, 58, 46))
    draw.rectangle((1060, 610, 1530, 685), fill=(42, 29, 26))
    draw.rectangle((1180, 500, 1415, 545), fill=(226, 214, 174))
    draw.line((1180, 500, 1415, 545), fill=(112, 71, 72), width=3)
    draw.rectangle((1530, 250, 1620, 560), fill=(191, 157, 93))
    draw.ellipse((1510, 205, 1640, 315), fill=(224, 196, 125))
    draw.rectangle((0, 755, W, 790), fill=(118, 91, 65))
    save_bg("bg facade study.png", img)


def map_bg():
    img = gradient((W, H), (38, 42, 48), (18, 20, 24))
    draw = ImageDraw.Draw(img)
    draw.rectangle((470, 230, 1450, 810), outline=(210, 190, 150), width=8)
    draw.line((470, 520, 1450, 520), fill=(210, 190, 150), width=5)
    draw.line((930, 230, 930, 810), fill=(210, 190, 150), width=5)
    draw.rectangle((520, 285, 880, 470), outline=(120, 160, 180), width=4)
    draw.rectangle((990, 285, 1390, 470), outline=(120, 160, 180), width=4)
    draw.rectangle((990, 585, 1390, 755), outline=(120, 160, 180), width=4)
    draw.text((610, 360), "SALON", fill=(230, 220, 190))
    draw.text((1090, 360), "KITCHEN", fill=(230, 220, 190))
    draw.text((1120, 655), "STUDY", fill=(230, 220, 190))
    save_bg("bg facade map.png", img)


def character(name, palette, pose_shift=0):
    out = IMAGES / name
    if out.exists():
        print(f"Skipping existing character sprite: {out}")
        return

    img = Image.new("RGBA", (620, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = 310 + pose_shift
    draw.ellipse((cx - 75, 120, cx + 75, 270), fill=palette["skin"], outline=palette["line"], width=4)
    draw.polygon([(cx - 55, 130), (cx + 75, 130), (cx + 45, 105), (cx - 70, 105)], fill=palette["hair"])
    draw.arc((cx - 35, 188, cx + 35, 230), 0, 180, fill=palette["line"], width=3)
    draw.line((cx - 135, 350, cx - 235, 690), fill=palette["cloth"], width=52)
    draw.line((cx + 135, 350, cx + 230, 690), fill=palette["cloth"], width=52)
    draw.polygon([(cx - 145, 285), (cx + 145, 285), (cx + 205, 910), (cx - 205, 910)], fill=palette["cloth"], outline=palette["line"])
    draw.polygon([(cx - 65, 292), (cx + 65, 292), (cx + 20, 480), (cx - 20, 480)], fill=palette["shirt"])
    draw.line((cx, 480, cx, 900), fill=palette["line"], width=3)
    draw.ellipse((cx - 245, 680, cx - 190, 740), fill=palette["skin"])
    draw.ellipse((cx + 200, 680, cx + 255, 740), fill=palette["skin"])
    img.save(out)


def menu_backgrounds():
    GUI.mkdir(parents=True, exist_ok=True)
    img = gradient((W, H), (18, 24, 32), (5, 7, 10))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 470, H), fill=(8, 9, 12))
    draw.rectangle((470, 0, 486, H), fill=(173, 146, 94))
    draw.polygon([(720, 210), (1690, 120), (1845, 930), (610, 930)], fill=(31, 33, 38))
    draw.polygon([(790, 280), (1600, 210), (1710, 890), (700, 890)], fill=(15, 17, 21))
    for x in (820, 1060, 1300, 1540):
        draw_window_wall(draw, x, 350, x + 150, 620, (194, 170, 110))
    draw.line((560, 760, 1860, 700), fill=(90, 94, 103), width=4)
    draw.text((85, 780), "THE GLASS HOUSE", fill=(232, 222, 196))
    draw.text((88, 830), "An after-midnight chamber mystery", fill=(158, 150, 134))
    img.save(GUI / "main_menu_glass.png")

    game_menu = img.filter(ImageFilter.GaussianBlur(1.2))
    overlay = Image.new("RGBA", (W, H), (7, 8, 10, 126))
    game_menu = Image.alpha_composite(game_menu.convert("RGBA"), overlay).convert("RGB")
    game_menu.save(GUI / "game_menu_glass.png")


def main():
    IMAGES.mkdir(parents=True, exist_ok=True)
    street()
    salon()
    kitchen()
    study()
    map_bg()
    character(
        "lila normal.png",
        {"skin": (219, 184, 154), "hair": (44, 32, 34), "cloth": (111, 34, 62), "shirt": (230, 211, 191), "line": (25, 21, 25)},
        -18,
    )
    character(
        "malcolm normal.png",
        {"skin": (202, 169, 136), "hair": (32, 34, 38), "cloth": (31, 61, 75), "shirt": (218, 220, 210), "line": (18, 22, 26)},
        16,
    )
    menu_backgrounds()


if __name__ == "__main__":
    main()

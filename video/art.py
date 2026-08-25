#!/usr/bin/env python3
"""
Рисунки предметов и фон для видеовыпусков.

Зачем рисунки. Семилетний ребёнок запоминает слово по картинке, а не по
подписи: он ещё не читает ни латиницу, ни бегло кириллицу. Пока на экране
было только слово и перевод, выпуск про алфавит работал для того, кто уже
умеет читать, то есть не для того, кому он нужен.

Всё рисуется кодом, файлов картинок нет. Причина та же, что у аватара в
приложении: предмет должен подстраиваться под кадр и цвет темы, а не быть
готовой картинкой в одном размере.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter

# ─────────────────────────────── предметы
# Ключ совпадает с английским словом из ТЗ, поэтому рисунок находится сам.


def _apple(d, x, y, s):
    red, light, leaf, stem = (222, 52, 66), (255, 122, 122), (74, 176, 96), (122, 78, 42)
    d.ellipse([x - 46 * s, y - 62 * s, x + 42 * s, y + 40 * s], fill=red)
    d.ellipse([x - 88 * s, y - 50 * s, x + 8 * s, y + 66 * s], fill=red)
    d.ellipse([x - 8 * s, y - 50 * s, x + 88 * s, y + 66 * s], fill=red)
    d.ellipse([x - 66 * s, y - 34 * s, x - 30 * s, y + 6 * s], fill=light)
    d.line([x + 2 * s, y - 56 * s, x + 10 * s, y - 92 * s], fill=stem, width=max(int(9 * s), 1))
    d.ellipse([x + 8 * s, y - 98 * s, x + 74 * s, y - 62 * s], fill=leaf)


def _ball(d, x, y, s):
    d.ellipse([x - 80 * s, y - 80 * s, x + 80 * s, y + 80 * s], fill=(255, 196, 61))
    d.ellipse([x - 60 * s, y - 62 * s, x - 16 * s, y - 22 * s], fill=(255, 226, 150))
    for angle in (0, 60, 120):
        a = math.radians(angle)
        d.line([x - 78 * s * math.cos(a), y - 78 * s * math.sin(a),
                x + 78 * s * math.cos(a), y + 78 * s * math.sin(a)],
               fill=(232, 120, 40), width=max(int(7 * s), 1))


def _cat_obj(d, x, y, s):
    body, cream, dark, pink = (247, 158, 74), (255, 232, 205), (36, 29, 61), (240, 137, 155)
    d.line([(x + 62 * s, y + 48 * s), (x + 96 * s, y + 10 * s), (x + 86 * s, y - 34 * s)],
           fill=(214, 122, 44), width=max(int(16 * s), 1), joint="curve")
    d.rounded_rectangle([x - 58 * s, y - 10 * s, x + 58 * s, y + 70 * s], radius=int(40 * s), fill=body)
    d.polygon([(x - 52 * s, y - 46 * s), (x - 62 * s, y - 92 * s), (x - 18 * s, y - 66 * s)], fill=body)
    d.polygon([(x + 52 * s, y - 46 * s), (x + 62 * s, y - 92 * s), (x + 18 * s, y - 66 * s)], fill=body)
    d.polygon([(x - 48 * s, y - 50 * s), (x - 55 * s, y - 80 * s), (x - 26 * s, y - 64 * s)], fill=pink)
    d.polygon([(x + 48 * s, y - 50 * s), (x + 55 * s, y - 80 * s), (x + 26 * s, y - 64 * s)], fill=pink)
    d.ellipse([x - 58 * s, y - 64 * s, x + 58 * s, y + 22 * s], fill=body)
    d.ellipse([x - 34 * s, y - 26 * s, x + 34 * s, y + 18 * s], fill=cream)
    for side in (-1, 1):
        d.ellipse([x + side * 22 * s - 9 * s, y - 38 * s, x + side * 22 * s + 9 * s, y - 18 * s], fill=dark)
    d.polygon([(x - 7 * s, y - 12 * s), (x + 7 * s, y - 12 * s), (x, y - 3 * s)], fill=pink)


def _dog(d, x, y, s):
    body, light, dark = (176, 124, 78), (232, 196, 150), (36, 29, 61)
    d.rounded_rectangle([x - 56 * s, y - 6 * s, x + 56 * s, y + 72 * s], radius=int(38 * s), fill=body)
    d.ellipse([x - 60 * s, y - 66 * s, x + 60 * s, y + 24 * s], fill=body)
    d.ellipse([x - 92 * s, y - 56 * s, x - 46 * s, y + 16 * s], fill=(140, 96, 58))
    d.ellipse([x + 46 * s, y - 56 * s, x + 92 * s, y + 16 * s], fill=(140, 96, 58))
    d.ellipse([x - 32 * s, y - 20 * s, x + 32 * s, y + 24 * s], fill=light)
    for side in (-1, 1):
        d.ellipse([x + side * 22 * s - 9 * s, y - 40 * s, x + side * 22 * s + 9 * s, y - 20 * s], fill=dark)
    d.ellipse([x - 11 * s, y - 12 * s, x + 11 * s, y + 6 * s], fill=dark)


def _egg(d, x, y, s):
    d.ellipse([x - 54 * s, y - 74 * s, x + 54 * s, y + 66 * s], fill=(255, 246, 226))
    d.ellipse([x - 34 * s, y - 52 * s, x - 4 * s, y - 14 * s], fill=(255, 255, 255))
    d.arc([x - 54 * s, y - 20 * s, x + 54 * s, y + 66 * s], 20, 160, fill=(228, 214, 186),
          width=max(int(4 * s), 1))


def _fish(d, x, y, s):
    d.ellipse([x - 70 * s, y - 40 * s, x + 40 * s, y + 40 * s], fill=(76, 176, 224))
    d.polygon([(x + 34 * s, y), (x + 88 * s, y - 44 * s), (x + 88 * s, y + 44 * s)], fill=(52, 148, 200))
    d.ellipse([x - 50 * s, y - 16 * s, x - 30 * s, y + 4 * s], fill=(255, 255, 255))
    d.ellipse([x - 45 * s, y - 11 * s, x - 35 * s, y - 1 * s], fill=(36, 29, 61))


def _key(d, x, y, s):
    gold = (240, 196, 74)
    d.ellipse([x - 76 * s, y - 40 * s, x - 4 * s, y + 32 * s], outline=gold, width=max(int(18 * s), 1))
    d.line([x - 14 * s, y, x + 78 * s, y], fill=gold, width=max(int(16 * s), 1))
    d.line([x + 46 * s, y, x + 46 * s, y + 34 * s], fill=gold, width=max(int(14 * s), 1))
    d.line([x + 74 * s, y, x + 74 * s, y + 26 * s], fill=gold, width=max(int(14 * s), 1))


def _milk(d, x, y, s):
    d.polygon([(x - 44 * s, y + 70 * s), (x - 44 * s, y - 34 * s), (x, y - 74 * s),
               (x + 44 * s, y - 34 * s), (x + 44 * s, y + 70 * s)], fill=(244, 246, 252))
    d.rounded_rectangle([x - 44 * s, y + 6 * s, x + 44 * s, y + 70 * s], radius=int(8 * s), fill=(79, 110, 229))
    d.ellipse([x - 20 * s, y + 22 * s, x + 20 * s, y + 54 * s], fill=(244, 246, 252))


def _sun(d, x, y, s):
    for step in range(12):
        a = math.radians(step * 30)
        d.line([x + 62 * s * math.cos(a), y + 62 * s * math.sin(a),
                x + 92 * s * math.cos(a), y + 92 * s * math.sin(a)],
               fill=(255, 196, 61), width=max(int(9 * s), 1))
    d.ellipse([x - 56 * s, y - 56 * s, x + 56 * s, y + 56 * s], fill=(255, 214, 92))


def _book(d, x, y, s):
    d.polygon([(x, y - 46 * s), (x - 84 * s, y - 26 * s), (x - 84 * s, y + 54 * s), (x, y + 34 * s)],
              fill=(96, 132, 232))
    d.polygon([(x, y - 46 * s), (x + 84 * s, y - 26 * s), (x + 84 * s, y + 54 * s), (x, y + 34 * s)],
              fill=(126, 158, 240))
    d.line([x, y - 46 * s, x, y + 34 * s], fill=(60, 92, 190), width=max(int(5 * s), 1))


def _house(d, x, y, s):
    d.polygon([(x, y - 78 * s), (x - 88 * s, y - 4 * s), (x + 88 * s, y - 4 * s)], fill=(224, 96, 88))
    d.rounded_rectangle([x - 66 * s, y - 4 * s, x + 66 * s, y + 72 * s], radius=int(6 * s), fill=(246, 232, 208))
    d.rounded_rectangle([x - 20 * s, y + 16 * s, x + 20 * s, y + 72 * s], radius=int(6 * s), fill=(150, 106, 66))


def _girl(d, x, y, s):
    skin, hair, dress = (255, 218, 190), (108, 72, 52), (236, 96, 128)
    d.ellipse([x - 54 * s, y + 6 * s, x + 54 * s, y + 96 * s], fill=dress)
    d.polygon([(x - 54 * s, y + 96 * s), (x + 54 * s, y + 96 * s), (x + 70 * s, y + 120 * s),
               (x - 70 * s, y + 120 * s)], fill=dress)
    d.ellipse([x - 56 * s, y - 92 * s, x + 56 * s, y + 24 * s], fill=hair)
    d.ellipse([x - 44 * s, y - 78 * s, x + 44 * s, y + 18 * s], fill=skin)
    d.ellipse([x - 66 * s, y - 46 * s, x - 34 * s, y + 34 * s], fill=hair)
    d.ellipse([x + 34 * s, y - 46 * s, x + 66 * s, y + 34 * s], fill=hair)
    for side in (-1, 1):
        d.ellipse([x + side * 18 * s - 6 * s, y - 34 * s, x + side * 18 * s + 6 * s, y - 20 * s], fill=(40, 32, 60))
    d.arc([x - 18 * s, y - 20 * s, x + 18 * s, y + 6 * s], 20, 160, fill=(180, 90, 100), width=max(int(5 * s), 1))


def _hand(d, x, y, s):
    skin, line = (255, 214, 178), (226, 172, 132)
    d.rounded_rectangle([x - 46 * s, y - 20 * s, x + 46 * s, y + 76 * s], radius=int(30 * s), fill=skin)
    for index, dx in enumerate((-34, -12, 10, 32)):
        top = y - 86 * s + abs(index - 1.5) * 12 * s
        d.rounded_rectangle([x + dx * s - 11 * s, top, x + dx * s + 11 * s, y + 10 * s],
                            radius=int(11 * s), fill=skin)
    d.rounded_rectangle([x + 34 * s, y - 4 * s, x + 76 * s, y + 26 * s], radius=int(15 * s), fill=skin)
    d.line([x - 26 * s, y + 34 * s, x + 26 * s, y + 34 * s], fill=line, width=max(int(4 * s), 1))


def _insect(d, x, y, s):
    body, dot, leg = (226, 68, 68), (40, 34, 62), (40, 34, 62)
    for side in (-1, 1):
        for dy in (-26, 0, 26):
            d.line([x + side * 40 * s, y + dy * s, x + side * 84 * s, y + (dy - 16) * s],
                   fill=leg, width=max(int(6 * s), 1))
    d.ellipse([x - 62 * s, y - 58 * s, x + 62 * s, y + 62 * s], fill=body)
    d.ellipse([x - 40 * s, y - 78 * s, x + 40 * s, y - 10 * s], fill=dot)
    d.line([x, y - 40 * s, x, y + 60 * s], fill=dot, width=max(int(6 * s), 1))
    for cx, cy, r in ((-34, -4, 13), (30, 10, 11), (-22, 34, 10), (34, -22, 9)):
        d.ellipse([x + cx * s - r * s, y + cy * s - r * s, x + cx * s + r * s, y + cy * s + r * s], fill=dot)


def _jam(d, x, y, s):
    glass, jam, lid = (246, 240, 226), (206, 44, 86), (120, 96, 200)
    d.rounded_rectangle([x - 52 * s, y - 46 * s, x + 52 * s, y + 74 * s], radius=int(18 * s), fill=glass)
    d.rounded_rectangle([x - 46 * s, y - 10 * s, x + 46 * s, y + 68 * s], radius=int(14 * s), fill=jam)
    d.rounded_rectangle([x - 58 * s, y - 76 * s, x + 58 * s, y - 40 * s], radius=int(12 * s), fill=lid)
    d.ellipse([x - 34 * s, y + 8 * s, x - 14 * s, y + 32 * s], fill=(238, 96, 128))


def _lamp(d, x, y, s):
    glow, glass, base = (255, 226, 138), (255, 246, 206), (120, 128, 158)
    d.ellipse([x - 78 * s, y - 92 * s, x + 78 * s, y + 34 * s], fill=(255, 226, 138, 90))
    d.ellipse([x - 52 * s, y - 72 * s, x + 52 * s, y + 30 * s], fill=glass)
    d.rounded_rectangle([x - 22 * s, y + 18 * s, x + 22 * s, y + 60 * s], radius=int(8 * s), fill=base)
    d.rounded_rectangle([x - 28 * s, y + 56 * s, x + 28 * s, y + 76 * s], radius=int(8 * s), fill=(90, 98, 128))
    for angle in (200, 250, 290, 340):
        a = math.radians(angle)
        d.line([x + 66 * s * math.cos(a), y - 20 * s + 66 * s * math.sin(a),
                x + 92 * s * math.cos(a), y - 20 * s + 92 * s * math.sin(a)],
               fill=glow, width=max(int(7 * s), 1))


def _nose(d, x, y, s):
    """Лицо крупным планом со стрелкой на нос: сам по себе нос не читается."""
    skin, shade, dark, blush = (255, 216, 184), (240, 178, 140), (56, 44, 40), (250, 168, 172)
    d.ellipse([x - 84 * s, y - 92 * s, x + 84 * s, y + 92 * s], fill=skin)
    d.ellipse([x - 78 * s, y - 118 * s, x + 78 * s, y - 40 * s], fill=(108, 72, 52))
    for side in (-1, 1):
        d.ellipse([x + side * 38 * s - 12 * s, y - 34 * s, x + side * 38 * s + 12 * s, y - 10 * s], fill=dark)
        d.ellipse([x + side * 56 * s - 16 * s, y + 18 * s, x + side * 56 * s + 16 * s, y + 40 * s], fill=blush)
    d.arc([x - 30 * s, y + 30 * s, x + 30 * s, y + 66 * s], 20, 160, fill=dark, width=max(int(6 * s), 1))
    d.ellipse([x - 24 * s, y - 16 * s, x + 24 * s, y + 34 * s], fill=shade)
    d.ellipse([x - 15 * s, y + 14 * s, x - 4 * s, y + 26 * s], fill=dark)
    d.ellipse([x + 4 * s, y + 14 * s, x + 15 * s, y + 26 * s], fill=dark)
    d.line([x + 96 * s, y + 4 * s, x + 42 * s, y + 4 * s], fill=(255, 214, 102), width=max(int(8 * s), 1))
    d.polygon([(x + 30 * s, y + 4 * s), (x + 54 * s, y - 12 * s), (x + 54 * s, y + 20 * s)], fill=(255, 214, 102))


def _orange(d, x, y, s):
    peel, light, leaf = (245, 148, 36), (255, 190, 110), (74, 176, 96)
    d.ellipse([x - 80 * s, y - 76 * s, x + 80 * s, y + 84 * s], fill=peel)
    d.ellipse([x - 56 * s, y - 52 * s, x - 20 * s, y - 12 * s], fill=light)
    d.line([x, y - 76 * s, x, y - 96 * s], fill=(122, 78, 42), width=max(int(8 * s), 1))
    d.ellipse([x - 2 * s, y - 112 * s, x + 62 * s, y - 80 * s], fill=leaf)


def _pen(d, x, y, s):
    body, tip, cap = (60, 92, 190), (255, 214, 102), (36, 56, 130)
    d.polygon([(x - 78 * s, y + 78 * s), (x - 58 * s, y + 44 * s), (x + 62 * s, y - 76 * s),
               (x + 84 * s, y - 54 * s), (x - 36 * s, y + 66 * s)], fill=body)
    d.polygon([(x - 78 * s, y + 78 * s), (x - 58 * s, y + 44 * s), (x - 36 * s, y + 66 * s)], fill=tip)
    d.polygon([(x + 46 * s, y - 60 * s), (x + 62 * s, y - 76 * s), (x + 84 * s, y - 54 * s),
               (x + 68 * s, y - 38 * s)], fill=cap)


def _queen(d, x, y, s):
    gold, gem, skin, hair = (255, 202, 66), (226, 68, 122), (255, 218, 190), (92, 60, 44)
    d.ellipse([x - 56 * s, y - 40 * s, x + 56 * s, y + 76 * s], fill=hair)
    d.ellipse([x - 46 * s, y - 32 * s, x + 46 * s, y + 62 * s], fill=skin)
    for side in (-1, 1):
        d.ellipse([x + side * 18 * s - 6 * s, y + 4 * s, x + side * 18 * s + 6 * s, y + 18 * s], fill=(40, 32, 60))
    d.arc([x - 18 * s, y + 20 * s, x + 18 * s, y + 44 * s], 20, 160, fill=(180, 90, 100), width=max(int(5 * s), 1))
    d.polygon([(x - 60 * s, y - 34 * s), (x - 60 * s, y - 96 * s), (x - 26 * s, y - 58 * s),
               (x, y - 104 * s), (x + 26 * s, y - 58 * s), (x + 60 * s, y - 96 * s),
               (x + 60 * s, y - 34 * s)], fill=gold)
    d.ellipse([x - 10 * s, y - 56 * s, x + 10 * s, y - 36 * s], fill=gem)


def _red(d, x, y, s):
    _colour_blob(d, x, y, s, (226, 48, 60), (255, 122, 122))


def _yellow(d, x, y, s):
    _colour_blob(d, x, y, s, (250, 196, 40), (255, 228, 140))


def _colour_blob(d, x, y, s, main, light):
    """Цвет показываем кляксой краски: у слова «red» предмета нет."""
    d.ellipse([x - 86 * s, y - 76 * s, x + 86 * s, y + 84 * s], fill=main)
    for cx, cy, r in ((-96, 30, 22), (92, -34, 18), (46, 80, 16), (-58, -76, 14)):
        d.ellipse([x + cx * s - r * s, y + cy * s - r * s, x + cx * s + r * s, y + cy * s + r * s], fill=main)
    d.ellipse([x - 58 * s, y - 50 * s, x - 20 * s, y - 12 * s], fill=light)


def _table(d, x, y, s):
    top, leg = (186, 128, 74), (150, 100, 56)
    d.rounded_rectangle([x - 96 * s, y - 32 * s, x + 96 * s, y + 2 * s], radius=int(10 * s), fill=top)
    d.rounded_rectangle([x - 82 * s, y + 2 * s, x - 62 * s, y + 84 * s], radius=int(6 * s), fill=leg)
    d.rounded_rectangle([x + 62 * s, y + 2 * s, x + 82 * s, y + 84 * s], radius=int(6 * s), fill=leg)


def _umbrella(d, x, y, s):
    dome, dome2, stick = (226, 68, 96), (255, 255, 255), (120, 96, 60)
    d.pieslice([x - 100 * s, y - 92 * s, x + 100 * s, y + 48 * s], 180, 360, fill=dome)
    for start in (200, 240, 280, 320):
        if (start // 40) % 2 == 0:
            d.pieslice([x - 100 * s, y - 92 * s, x + 100 * s, y + 48 * s], start, start + 40, fill=dome2)
    d.line([x, y - 22 * s, x, y + 78 * s], fill=stick, width=max(int(9 * s), 1))
    d.arc([x - 40 * s, y + 54 * s, x, y + 96 * s], 0, 180, fill=stick, width=max(int(9 * s), 1))


def _van(d, x, y, s):
    body, glass, wheel = (72, 148, 220), (198, 232, 250), (44, 40, 56)
    d.rounded_rectangle([x - 100 * s, y - 44 * s, x + 40 * s, y + 40 * s], radius=int(16 * s), fill=body)
    d.polygon([(x + 40 * s, y - 20 * s), (x + 78 * s, y - 20 * s), (x + 100 * s, y + 10 * s),
               (x + 100 * s, y + 40 * s), (x + 40 * s, y + 40 * s)], fill=body)
    d.rounded_rectangle([x + 46 * s, y - 12 * s, x + 84 * s, y + 12 * s], radius=int(6 * s), fill=glass)
    d.rounded_rectangle([x - 88 * s, y - 32 * s, x - 20 * s, y + 4 * s], radius=int(8 * s), fill=glass)
    for cx in (-62, 58):
        d.ellipse([x + cx * s - 24 * s, y + 22 * s, x + cx * s + 24 * s, y + 70 * s], fill=wheel)
        d.ellipse([x + cx * s - 10 * s, y + 36 * s, x + cx * s + 10 * s, y + 56 * s], fill=(180, 186, 200))


def _water(d, x, y, s):
    glass, liquid = (226, 240, 250), (74, 168, 226)
    d.polygon([(x - 54 * s, y - 74 * s), (x + 54 * s, y - 74 * s), (x + 40 * s, y + 80 * s),
               (x - 40 * s, y + 80 * s)], fill=glass)
    d.polygon([(x - 46 * s, y - 20 * s), (x + 46 * s, y - 20 * s), (x + 40 * s, y + 76 * s),
               (x - 40 * s, y + 76 * s)], fill=liquid)
    d.ellipse([x - 46 * s, y - 32 * s, x + 46 * s, y - 8 * s], fill=(126, 198, 240))
    d.ellipse([x - 30 * s, y + 6 * s, x - 16 * s, y + 26 * s], fill=(168, 218, 246))


def _box(d, x, y, s):
    face, side, tape = (206, 158, 104), (176, 128, 78), (232, 214, 180)
    d.polygon([(x - 84 * s, y - 34 * s), (x, y - 74 * s), (x + 84 * s, y - 34 * s), (x, y + 6 * s)], fill=tape)
    d.polygon([(x - 84 * s, y - 34 * s), (x, y + 6 * s), (x, y + 84 * s), (x - 84 * s, y + 44 * s)], fill=face)
    d.polygon([(x + 84 * s, y - 34 * s), (x, y + 6 * s), (x, y + 84 * s), (x + 84 * s, y + 44 * s)], fill=side)


def _zoo(d, x, y, s):
    mane, face, dark = (222, 148, 52), (250, 206, 140), (54, 40, 34)
    d.ellipse([x - 92 * s, y - 92 * s, x + 92 * s, y + 92 * s], fill=mane)
    for angle in range(0, 360, 30):
        a = math.radians(angle)
        d.ellipse([x + 86 * s * math.cos(a) - 22 * s, y + 86 * s * math.sin(a) - 22 * s,
                   x + 86 * s * math.cos(a) + 22 * s, y + 86 * s * math.sin(a) + 22 * s], fill=mane)
    d.ellipse([x - 62 * s, y - 62 * s, x + 62 * s, y + 62 * s], fill=face)
    for side in (-1, 1):
        d.ellipse([x + side * 26 * s - 9 * s, y - 24 * s, x + side * 26 * s + 9 * s, y - 6 * s], fill=dark)
    d.polygon([(x - 14 * s, y + 12 * s), (x + 14 * s, y + 12 * s), (x, y + 28 * s)], fill=dark)
    d.arc([x - 30 * s, y + 18 * s, x, y + 46 * s], 0, 180, fill=dark, width=max(int(5 * s), 1))
    d.arc([x, y + 18 * s, x + 30 * s, y + 46 * s], 0, 180, fill=dark, width=max(int(5 * s), 1))


OBJECTS = {
    "apple": _apple, "ball": _ball, "cat": _cat_obj, "dog": _dog, "egg": _egg,
    "fish": _fish, "key": _key, "milk": _milk, "sun": _sun, "book": _book, "house": _house,
    "girl": _girl, "hand": _hand, "insect": _insect, "jam": _jam, "lamp": _lamp, "nose": _nose,
    "orange": _orange, "pen": _pen, "queen": _queen, "red": _red, "yellow": _yellow,
    "table": _table, "umbrella": _umbrella, "van": _van, "water": _water, "box": _box, "zoo": _zoo,
}


# Готовые картинки кладутся сюда файлами вида apple.png, и код их
# предпочитает своим рисункам. Так художник (или генератор) может заменить
# любой предмет, не трогая ни строчки кода.
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "objects")
# Ширина рисунка при scale = 1. Рисованные предметы занимают примерно 180
# точек при той же мере, поэтому и у файла размах такой же: иначе картинка из
# набора выходит вдвое крупнее нарисованной и кадр разъезжается.
ASSET_BOX = 95
_assets: dict[str, Image.Image] = {}


def asset(word):
    """Файл картинки для слова, если он положен. Иначе None."""
    key = word.lower().strip()
    if key in _assets:
        return _assets[key]
    found = None
    for suffix in (".png", ".webp"):
        path = os.path.join(ASSETS, key + suffix)
        if os.path.exists(path):
            found = Image.open(path).convert("RGBA")
            break
    _assets[key] = found
    return found


def draw_object(image, word, x, y, scale):
    """Предмет по английскому слову: сначала файл, потом рисунок кодом.

    Ничего нет — возвращаем False, и карточка остаётся текстовой. Молча
    подставлять чужую картинку нельзя: ребёнок запомнит слово по ней.
    """
    picture = asset(word)
    if picture is not None:
        box = max(int(ASSET_BOX * scale * 2), 1)
        ratio = min(box / picture.width, box / picture.height)
        size = (max(int(picture.width * ratio), 1), max(int(picture.height * ratio), 1))
        resized = picture.resize(size, Image.LANCZOS)
        image.paste(resized, (int(x - size[0] / 2), int(y - size[1] / 2)), resized)
        return True
    painter = OBJECTS.get(word.lower())
    if not painter:
        return False
    painter(ImageDraw.Draw(image), x, y, scale)
    return True


# ─────────────────────────────── фон
# Плоская тёмная заливка с дугами выглядела как служебный слайд. Сцена из
# мягких пятен с медленным движением даёт глубину и не отвлекает от слова.

# Палитра бренда: только синие тона. Жёлтый остаётся тексту и акцентам:
# в фоне он смешивается с синим и даёт грязный оливковый.
PALETTES = {
    "G1": [(38, 74, 168), (58, 108, 200), (92, 152, 232)],
    "G2": [(30, 56, 132), (44, 86, 166), (60, 110, 180)],
    "G3": [(22, 38, 92), (28, 52, 112), (40, 52, 96)],
}
BASE = {"G1": (16, 26, 66), "G2": (13, 21, 54), "G3": (11, 17, 42)}


def make_background(size, age, phase=0.0, blobs=5):
    """Слои мягких пятен. Медленно плывут, поэтому кадр не мёртвый."""
    w, h = size
    img = Image.new("RGB", (w, h), BASE[age])
    layer = Image.new("RGB", (w // 4, h // 4), BASE[age])
    draw = ImageDraw.Draw(layer)
    palette = PALETTES[age]
    for index in range(blobs):
        colour = palette[index % len(palette)]
        drift = math.sin(phase * 0.35 + index * 1.7)
        cx = (w // 4) * (0.18 + 0.19 * index) + drift * 14
        cy = (h // 4) * (0.32 + 0.16 * math.cos(phase * 0.28 + index)) + drift * 8
        radius = (w // 4) * (0.20 + 0.05 * ((index % 3) + 1))
        draw.ellipse([cx - radius, cy - radius * 0.8, cx + radius, cy + radius * 0.8], fill=colour)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=38))
    layer = layer.resize((w, h), Image.LANCZOS)
    return Image.blend(img, layer, 0.55)


def ease_out_back(t):
    """Появление с лёгким перелётом: предмет как будто прыгает в кадр."""
    t = max(0.0, min(1.0, t))
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


# ─────────────────────────────── фоны-сцены
#
# Раньше фон был мягкими пятнами, одинаковыми для всех выпусков: урок про
# буквы, про слова и про правило выглядели одним и тем же экраном. Комната
# задаёт выпуску место: буквы идут в классе, слова дома, правило у доски.
#
# Сцены рисуются кодом, а не лежат картинками, по двум причинам: облачная
# сборка тогда не тянет за собой мегабайты файлов, и фон подстраивается под
# цвет темы возраста, а не спорит с ним.
SCENE_INK = {
    "light": {"wall": (238, 240, 250), "far": (222, 227, 242), "near": (205, 213, 235),
              "warm": (250, 236, 205), "board": (196, 214, 205), "line": (180, 190, 214)},
    "bands": {"wall": (17, 25, 58), "far": (23, 33, 74), "near": (30, 44, 96),
              "warm": (46, 40, 82), "board": (28, 54, 60), "line": (40, 56, 112)},
}


def _window(d, x, y, w, h, tone):
    """Окно: рама и свет. Одно окно делает стену комнатой, а не заливкой."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=tone["far"])
    d.rounded_rectangle([x + 14, y + 14, x + w - 14, y + h - 14], radius=14, fill=tone["warm"])
    d.line([x + w / 2, y + 14, x + w / 2, y + h - 14], fill=tone["far"], width=10)
    d.line([x + 14, y + h / 2, x + w - 14, y + h / 2], fill=tone["far"], width=10)


def scene_background(name, size, age, theme):
    """Комната по имени фона. Незнакомое имя возвращает None: тогда рисуется
    обычный мягкий фон, и новый диалог не ломает сборку.

    Комната пишется в три слоя: стена со светом от окна, дальняя обстановка,
    ближние предметы у нижнего края. Слои разной светлоты дают глубину, без
    которой кадр читается как аппликация. Всё приглушено: место должно
    чувствоваться, но спорить с текстом ему нельзя.
    """
    if name not in ("class", "home", "board"):
        return None
    w, h = size
    light = theme.get("hero_x", 0) > 900
    tone = SCENE_INK["light" if light else "bands"]
    img = Image.new("RGB", (w, h), tone["wall"])
    d = ImageDraw.Draw(img)

    def warm_light(cx, cy, radius):
        """Пятно тёплого света: комната без него плоская, как чертёж."""
        glow = Image.new("RGB", (w, h), tone["wall"])
        gd = ImageDraw.Draw(glow)
        gd.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=tone["warm"])
        return Image.blend(img, glow.filter(ImageFilter.GaussianBlur(radius=120)), 0.5)

    if name == "class":
        # Класс: доска на стене, ряд парт, окно со светом, глобус и стопка книг.
        img = warm_light(w * 0.78, h * 0.3, w * 0.28)
        d = ImageDraw.Draw(img)
        d.rectangle([0, h * 0.70, w, h], fill=tone["near"])
        d.rectangle([0, h * 0.70, w, h * 0.72], fill=tone["far"])
        # доска
        d.rounded_rectangle([w * 0.05, h * 0.09, w * 0.53, h * 0.54], radius=20, fill=tone["far"])
        d.rounded_rectangle([w * 0.07, h * 0.11, w * 0.51, h * 0.52], radius=16, fill=tone["board"])
        d.rounded_rectangle([w * 0.09, h * 0.50, w * 0.49, h * 0.535], radius=8, fill=tone["far"])
        for index in range(3):
            y = h * (0.18 + index * 0.09)
            d.line([w * 0.11, y, w * (0.2 + index * 0.09), y], fill=tone["wall"], width=6)
        # окно
        _window(d, w * 0.63, h * 0.11, w * 0.26, h * 0.36, tone)
        d.rounded_rectangle([w * 0.60, h * 0.47, w * 0.92, h * 0.50], radius=6, fill=tone["far"])
        # парты двумя рядами, дальний ряд мельче: так появляется глубина
        for row, (scale, base) in enumerate(((0.72, 0.78), (1.0, 0.9))):
            width = w * 0.2 * scale
            for index in range(3):
                x = w * (0.08 + index * 0.3) + row * w * 0.04
                top = h * base
                d.rounded_rectangle([x, top, x + width, top + h * 0.035], radius=8, fill=tone["far"])
                d.rectangle([x + 14, top + h * 0.035, x + 26, top + h * 0.14], fill=tone["far"])
                d.rectangle([x + width - 26, top + h * 0.035, x + width - 14, top + h * 0.14], fill=tone["far"])
        # глобус на тумбе у окна
        d.rounded_rectangle([w * 0.86, h * 0.62, w * 0.95, h * 0.71], radius=10, fill=tone["far"])
        d.ellipse([w * 0.865, h * 0.55, w * 0.945, h * 0.63], fill=tone["board"])

    elif name == "home":
        # Дом: окно с занавеской и цветком, диван, лампа, ковёр, полка.
        img = warm_light(w * 0.2, h * 0.3, w * 0.26)
        d = ImageDraw.Draw(img)
        d.rectangle([0, h * 0.72, w, h], fill=tone["near"])
        _window(d, w * 0.07, h * 0.13, w * 0.24, h * 0.34, tone)
        d.rounded_rectangle([w * 0.05, h * 0.11, w * 0.33, h * 0.15], radius=10, fill=tone["far"])
        # цветок на подоконнике
        d.rounded_rectangle([w * 0.11, h * 0.44, w * 0.15, h * 0.49], radius=6, fill=tone["board"])
        d.ellipse([w * 0.10, h * 0.39, w * 0.16, h * 0.45], fill=tone["board"])
        # полка с книгами
        d.rounded_rectangle([w * 0.42, h * 0.24, w * 0.58, h * 0.26], radius=6, fill=tone["far"])
        for index in range(5):
            x = w * (0.43 + index * 0.028)
            d.rectangle([x, h * (0.17 + (index % 3) * 0.012), x + w * 0.018, h * 0.24], fill=tone["far"])
        # диван и подушка
        d.rounded_rectangle([w * 0.58, h * 0.58, w * 0.93, h * 0.78], radius=28, fill=tone["far"])
        d.rounded_rectangle([w * 0.61, h * 0.54, w * 0.90, h * 0.62], radius=22, fill=tone["near"])
        d.rounded_rectangle([w * 0.63, h * 0.50, w * 0.71, h * 0.60], radius=18, fill=tone["warm"])
        # торшер
        d.rectangle([w * 0.955, h * 0.42, w * 0.965, h * 0.78], fill=tone["far"])
        d.polygon([(w * 0.93, h * 0.42), (w * 0.99, h * 0.42), (w * 0.975, h * 0.33), (w * 0.945, h * 0.33)],
                  fill=tone["warm"])
        # ковёр
        d.ellipse([w * 0.28, h * 0.84, w * 0.78, h * 0.98], fill=tone["far"])
        d.ellipse([w * 0.33, h * 0.86, w * 0.73, h * 0.96], fill=tone["near"])

    else:
        # Доска: почти весь кадр это доска. Рамка, полка, мел и тряпка, чтобы
        # это была доска в классе, а не тёмный прямоугольник.
        img = warm_light(w * 0.5, h * 0.2, w * 0.5)
        d = ImageDraw.Draw(img)
        d.rectangle([0, h * 0.84, w, h], fill=tone["near"])
        d.rounded_rectangle([w * 0.03, h * 0.05, w * 0.97, h * 0.82], radius=26, fill=tone["far"])
        d.rounded_rectangle([w * 0.045, h * 0.065, w * 0.955, h * 0.805], radius=20, fill=tone["board"])
        # затёртые следы мела: доской пользуются
        for index in range(3):
            y = h * (0.12 + index * 0.24)
            d.line([w * 0.08, y, w * 0.26, y - h * 0.01], fill=tone["far"], width=8)
        d.rounded_rectangle([w * 0.03, h * 0.82, w * 0.97, h * 0.855], radius=10, fill=tone["far"])
        d.rounded_rectangle([w * 0.10, h * 0.828, w * 0.16, h * 0.845], radius=6, fill=tone["wall"])
        d.rounded_rectangle([w * 0.83, h * 0.822, w * 0.90, h * 0.85], radius=8, fill=tone["near"])

    img = img.filter(ImageFilter.GaussianBlur(radius=5))
    return Image.blend(img, Image.new("RGB", (w, h), theme["bg"]), 0.32)


# ─────────────────────────────── вторая партия предметов
#
# Слов на карточках 671, рисунков было 28. Остальные слова показывались голым
# текстом, а младший ребёнок запоминает слово по картинке. Здесь предметы,
# которые встречаются в выпусках для 7-9 лет: цвета, числа, школа, дом.

CLR = {
    "blue": ((36, 96, 214), (120, 168, 245)),
    "green": ((36, 158, 92), (128, 214, 168)),
    "black": ((42, 48, 62), (96, 104, 122)),
    "white": ((236, 238, 246), (255, 255, 255)),
    "brown": ((140, 92, 48), (196, 152, 104)),
    "grey": ((140, 148, 166), (188, 194, 208)),
    "pink": ((238, 116, 168), (252, 176, 208)),
    "purple": ((124, 76, 216), (176, 140, 246)),
    "orange_c": ((240, 148, 42), (250, 194, 118)),
}


def _swatch(name):
    main, light = CLR[name]
    return lambda d, x, y, s: _colour_blob(d, x, y, s, main, light)


def _rainbow(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    """Слово colour: не один цвет, а несколько дуг подряд."""
    bands = [(226, 62, 62), (240, 148, 42), (245, 206, 60), (36, 158, 92), (36, 96, 214)]
    for index, colour in enumerate(bands):
        r = s * (1.0 - index * 0.16)
        d.pieslice([x - r, y - r, x + r, y + r], 200, 340, fill=colour)
    d.pieslice([x - s * 0.2, y - s * 0.2, x + s * 0.2, y + s * 0.2], 200, 340, fill=(247, 248, 252))


def _dots(count):
    """Число: столько кружков, сколько названо. Цифра ребёнку ещё ничего не
    говорит, а пять кружков говорят сразу."""
    def draw(d, x, y, s, count=count):
        s = s * 100
        per_row = 5 if count > 4 else count
        rows = math.ceil(count / per_row)
        r = min(s * 0.18, s * 0.9 / per_row)
        gap = r * 2.5
        for index in range(count):
            row, column = divmod(index, per_row)
            cx = x + (column - (per_row - 1) / 2) * gap
            cy = y + (row - (rows - 1) / 2) * gap
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 176, 46))
            d.ellipse([cx - r * 0.42, cy - r * 0.52, cx - r * 0.02, cy - r * 0.12], fill=(255, 214, 140))
    return draw


def _chair(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.5, y - s * 0.9, x + s * 0.5, y - s * 0.1], radius=int(s * 0.14), fill=(196, 138, 74))
    d.rounded_rectangle([x - s * 0.6, y - s * 0.2, x + s * 0.6, y + s * 0.05], radius=int(s * 0.1), fill=(224, 166, 96))
    d.rectangle([x - s * 0.5, y + s * 0.05, x - s * 0.34, y + s * 0.9], fill=(196, 138, 74))
    d.rectangle([x + s * 0.34, y + s * 0.05, x + s * 0.5, y + s * 0.9], fill=(196, 138, 74))


def _bed(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s, y - s * 0.1, x + s, y + s * 0.5], radius=int(s * 0.12), fill=(120, 152, 226))
    d.rounded_rectangle([x - s, y - s * 0.7, x - s * 0.72, y + s * 0.1], radius=int(s * 0.12), fill=(86, 116, 190))
    d.rounded_rectangle([x - s * 0.86, y - s * 0.34, x - s * 0.34, y - s * 0.02], radius=int(s * 0.1), fill=(246, 248, 255))
    d.rectangle([x - s * 0.94, y + s * 0.5, x - s * 0.78, y + s * 0.8], fill=(86, 116, 190))
    d.rectangle([x + s * 0.78, y + s * 0.5, x + s * 0.94, y + s * 0.8], fill=(86, 116, 190))


def _door(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.6, y - s, x + s * 0.6, y + s], radius=int(s * 0.12), fill=(176, 122, 68))
    d.rounded_rectangle([x - s * 0.44, y - s * 0.84, x + s * 0.44, y + s * 0.84], radius=int(s * 0.1), fill=(206, 152, 92))
    d.ellipse([x + s * 0.2, y - s * 0.06, x + s * 0.34, y + s * 0.08], fill=(250, 214, 120))


def _window_obj(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.8, y - s * 0.7, x + s * 0.8, y + s * 0.7], radius=int(s * 0.12), fill=(150, 176, 226))
    d.rounded_rectangle([x - s * 0.68, y - s * 0.58, x + s * 0.68, y + s * 0.58], radius=int(s * 0.08), fill=(206, 232, 250))
    d.line([x, y - s * 0.58, x, y + s * 0.58], fill=(150, 176, 226), width=max(int(s * 0.09), 3))
    d.line([x - s * 0.68, y, x + s * 0.68, y], fill=(150, 176, 226), width=max(int(s * 0.09), 3))


def _cup(d, x, y, s):
    s = s * 100
    # Ручка рисуется до чашки, чтобы уходить за её край, а не пересекать её.
    d.ellipse([x + s * 0.22, y - s * 0.28, x + s * 0.78, y + s * 0.28], fill=(150, 162, 190))
    d.ellipse([x + s * 0.34, y - s * 0.16, x + s * 0.66, y + s * 0.16], fill=(247, 248, 252))
    d.rounded_rectangle([x - s * 0.55, y - s * 0.45, x + s * 0.35, y + s * 0.6], radius=int(s * 0.16),
                        fill=(246, 248, 255), outline=(150, 162, 190), width=max(int(s * 0.05), 2))
    d.rounded_rectangle([x - s * 0.46, y - s * 0.36, x + s * 0.26, y - s * 0.06], radius=int(s * 0.1),
                        fill=(150, 96, 54))
    d.ellipse([x - s * 0.55, y + s * 0.52, x + s * 0.35, y + s * 0.72], fill=(214, 222, 240))


def _plate(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.ellipse([x - s * 0.9, y - s * 0.5, x + s * 0.9, y + s * 0.5], fill=(176, 190, 220))
    d.ellipse([x - s * 0.78, y - s * 0.42, x + s * 0.78, y + s * 0.42], fill=(226, 232, 245))
    d.ellipse([x - s * 0.5, y - s * 0.26, x + s * 0.5, y + s * 0.26], fill=(250, 251, 255))


def _spoon(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.ellipse([x - s * 0.26, y - s * 0.9, x + s * 0.26, y - s * 0.3], fill=(198, 206, 224))
    d.rounded_rectangle([x - s * 0.08, y - s * 0.4, x + s * 0.08, y + s * 0.9], radius=int(s * 0.08), fill=(214, 220, 236))


def _fork(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    for offset in (-0.22, 0.0, 0.22):
        d.rounded_rectangle([x + s * offset - s * 0.05, y - s * 0.9, x + s * offset + s * 0.05, y - s * 0.4],
                            radius=int(s * 0.05), fill=(198, 206, 224))
    d.rounded_rectangle([x - s * 0.3, y - s * 0.46, x + s * 0.3, y - s * 0.3], radius=int(s * 0.08), fill=(198, 206, 224))
    d.rounded_rectangle([x - s * 0.08, y - s * 0.34, x + s * 0.08, y + s * 0.9], radius=int(s * 0.08), fill=(214, 220, 236))


def _knife(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.polygon([(x - s * 0.2, y - s * 0.9), (x + s * 0.14, y - s * 0.8), (x + s * 0.1, y + s * 0.1),
               (x - s * 0.16, y + s * 0.1)], fill=(206, 214, 232))
    d.rounded_rectangle([x - s * 0.16, y + s * 0.1, x + s * 0.1, y + s * 0.9], radius=int(s * 0.1), fill=(88, 96, 120))


def _bread(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.8, y - s * 0.45, x + s * 0.8, y + s * 0.5], radius=int(s * 0.4), fill=(214, 158, 84))
    d.rounded_rectangle([x - s * 0.66, y - s * 0.3, x + s * 0.66, y + s * 0.36], radius=int(s * 0.3), fill=(240, 200, 138))


def _pencil(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.polygon([(x, y - s * 0.95), (x + s * 0.22, y - s * 0.6), (x - s * 0.22, y - s * 0.6)], fill=(60, 66, 84))
    d.rectangle([x - s * 0.22, y - s * 0.6, x + s * 0.22, y + s * 0.7], fill=(250, 196, 60))
    d.rectangle([x - s * 0.22, y + s * 0.7, x + s * 0.22, y + s * 0.95], fill=(236, 128, 140))


def _ruler(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.24, y - s * 0.95, x + s * 0.24, y + s * 0.95], radius=int(s * 0.08), fill=(250, 214, 118))
    for index in range(6):
        yy = y - s * 0.8 + index * s * 0.32
        d.line([x - s * 0.24, yy, x - s * 0.02, yy], fill=(160, 116, 40), width=max(int(s * 0.04), 2))


def _rubber(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.6, y - s * 0.3, x + s * 0.6, y + s * 0.3], radius=int(s * 0.12), fill=(238, 148, 176))
    d.rounded_rectangle([x - s * 0.6, y - s * 0.3, x - s * 0.1, y + s * 0.3], radius=int(s * 0.12), fill=(250, 250, 252))


def _scissors(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.line([x - s * 0.4, y - s * 0.8, x + s * 0.3, y + s * 0.3], fill=(170, 180, 200), width=max(int(s * 0.14), 5))
    d.line([x + s * 0.4, y - s * 0.8, x - s * 0.3, y + s * 0.3], fill=(150, 160, 184), width=max(int(s * 0.14), 5))
    d.ellipse([x - s * 0.55, y + s * 0.3, x - s * 0.05, y + s * 0.8], outline=(226, 96, 96), width=max(int(s * 0.1), 4))
    d.ellipse([x + s * 0.05, y + s * 0.3, x + s * 0.55, y + s * 0.8], outline=(226, 96, 96), width=max(int(s * 0.1), 4))


def _bag_obj(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.7, y - s * 0.35, x + s * 0.7, y + s * 0.8], radius=int(s * 0.18), fill=(216, 72, 92))
    d.rounded_rectangle([x - s * 0.7, y + s * 0.05, x + s * 0.7, y + s * 0.3], radius=int(s * 0.08), fill=(178, 48, 68))
    d.arc([x - s * 0.4, y - s * 0.85, x + s * 0.4, y - s * 0.05], 180, 360, fill=(178, 48, 68), width=max(int(s * 0.12), 4))


def _board_obj(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.95, y - s * 0.7, x + s * 0.95, y + s * 0.6], radius=int(s * 0.1), fill=(72, 108, 96))
    d.rounded_rectangle([x - s * 0.85, y - s * 0.6, x + s * 0.85, y + s * 0.5], radius=int(s * 0.08), fill=(86, 126, 112))
    d.rounded_rectangle([x - s * 0.4, y + s * 0.6, x + s * 0.4, y + s * 0.72], radius=int(s * 0.06), fill=(196, 152, 96))


def _phone(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.42, y - s * 0.9, x + s * 0.42, y + s * 0.9], radius=int(s * 0.16), fill=(52, 60, 82))
    d.rounded_rectangle([x - s * 0.34, y - s * 0.76, x + s * 0.34, y + s * 0.72], radius=int(s * 0.1), fill=(150, 200, 244))
    d.rounded_rectangle([x - s * 0.12, y - s * 0.86, x + s * 0.12, y - s * 0.78], radius=int(s * 0.04), fill=(88, 96, 120))


def _laptop(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.rounded_rectangle([x - s * 0.7, y - s * 0.75, x + s * 0.7, y + s * 0.25], radius=int(s * 0.1), fill=(72, 82, 108))
    d.rounded_rectangle([x - s * 0.6, y - s * 0.65, x + s * 0.6, y + s * 0.15], radius=int(s * 0.06), fill=(150, 200, 244))
    d.rounded_rectangle([x - s * 0.95, y + s * 0.25, x + s * 0.95, y + s * 0.45], radius=int(s * 0.08), fill=(174, 184, 208))


def _clock(d, x, y, s):
    s = s * 100  # рисунок писался от единицы, приводим к общей мере
    d.ellipse([x - s * 0.9, y - s * 0.9, x + s * 0.9, y + s * 0.9], fill=(246, 248, 255))
    d.ellipse([x - s * 0.78, y - s * 0.78, x + s * 0.78, y + s * 0.78], fill=(226, 232, 245))
    d.line([x, y, x, y - s * 0.5], fill=(52, 60, 82), width=max(int(s * 0.1), 4))
    d.line([x, y, x + s * 0.36, y + s * 0.12], fill=(52, 60, 82), width=max(int(s * 0.1), 4))
    d.ellipse([x - s * 0.08, y - s * 0.08, x + s * 0.08, y + s * 0.08], fill=(226, 96, 96))


OBJECTS.update({
    "colour": _rainbow, "color": _rainbow,
    "blue": _swatch("blue"), "green": _swatch("green"), "black": _swatch("black"),
    "white": _swatch("white"), "brown": _swatch("brown"), "grey": _swatch("grey"),
    "gray": _swatch("grey"), "pink": _swatch("pink"), "purple": _swatch("purple"),
    "one": _dots(1), "two": _dots(2), "three": _dots(3), "four": _dots(4), "five": _dots(5),
    "six": _dots(6), "seven": _dots(7), "eight": _dots(8), "nine": _dots(9), "ten": _dots(10),
    "eleven": _dots(11), "twelve": _dots(12), "thirteen": _dots(13), "fourteen": _dots(14),
    "fifteen": _dots(15), "sixteen": _dots(16), "seventeen": _dots(17), "eighteen": _dots(18),
    "nineteen": _dots(19), "twenty": _dots(20),
    "chair": _chair, "bed": _bed, "door": _door, "window": _window_obj,
    "cup": _cup, "plate": _plate, "spoon": _spoon, "fork": _fork, "knife": _knife, "bread": _bread,
    "pencil": _pencil, "ruler": _ruler, "rubber": _rubber, "scissors": _scissors,
    "bag": _bag_obj, "schoolbag": _bag_obj, "backpack": _bag_obj, "board": _board_obj,
    "phone": _phone, "laptop": _laptop, "computer": _laptop, "watch": _clock, "clock": _clock,
    "time": _clock, "notebook": _book, "sofa": _bed,
})


# ─────────────────────────────── люди, животные, еда, дорога
#
# Люди и животные рисуются одной заготовкой с разными приметами: причёска,
# уши, хвост, цвет. Пятнадцать отдельных рисунков разъехались бы по стилю, а
# одна заготовка держит их семьёй.

SKIN = (247, 206, 172)


def _figure(hair, cloth, small=False, grey_hair=False, beard=False):
    """Человек: голова, причёска, плечи. Разница между мамой и папой в
    причёске и цвете одежды, а не в отдельном рисунке."""
    def draw(d, x, y, s):
        s = s * 100
        k = 0.72 if small else 1.0
        head = s * 0.34 * k
        top = y - s * 0.5 * k
        # плечи
        d.rounded_rectangle([x - s * 0.52 * k, top + head * 1.5, x + s * 0.52 * k, y + s * 0.9],
                            radius=int(s * 0.26 * k), fill=cloth)
        d.ellipse([x - head, top - head * 0.2, x + head, top + head * 1.8], fill=SKIN)
        # hair это форма причёски, а не цвет: цвет один на всех, седина отдельно.
        colour = (176, 182, 196) if grey_hair else (74, 56, 44)
        if hair == "long":
            d.ellipse([x - head * 1.15, top - head * 0.4, x + head * 1.15, top + head * 2.1], fill=colour)
            d.ellipse([x - head, top - head * 0.05, x + head, top + head * 1.85], fill=SKIN)
        else:
            d.chord([x - head, top - head * 0.35, x + head, top + head * 1.2], 180, 360, fill=colour)
        if beard:
            d.chord([x - head * 0.8, top + head * 0.5, x + head * 0.8, top + head * 1.9], 0, 180, fill=colour)
        eye = max(int(head * 0.12), 2)
        d.ellipse([x - head * 0.42 - eye, top + head * 0.72 - eye, x - head * 0.42 + eye, top + head * 0.72 + eye],
                  fill=(48, 54, 74))
        d.ellipse([x + head * 0.42 - eye, top + head * 0.72 - eye, x + head * 0.42 + eye, top + head * 0.72 + eye],
                  fill=(48, 54, 74))
        d.arc([x - head * 0.4, top + head * 0.9, x + head * 0.4, top + head * 1.4], 20, 160, fill=(196, 118, 106),
              width=max(int(head * 0.12), 2))
    return draw


def _animal(body, ear, tail="short", muzzle=None, long_neck=False, mark=None):
    """Животное: туловище, голова, уши и хвост. Уши и хвост и делают из одной
    заготовки то кошку, то зайца, то медведя."""
    def draw(d, x, y, s):
        s = s * 100
        light = tuple(min(part + 40, 255) for part in body)
        edge = tuple(max(part - 60, 0) for part in body)
        d.ellipse([x - s * 0.62, y - s * 0.18, x + s * 0.52, y + s * 0.62], fill=body, outline=edge,
                  width=max(int(s * 0.03), 2))
        if mark == "spots":
            d.ellipse([x - s * 0.44, y + s * 0.02, x - s * 0.16, y + s * 0.3], fill=edge)
            d.ellipse([x - s * 0.05, y + s * 0.22, x + s * 0.19, y + s * 0.46], fill=edge)
        elif mark == "wool":
            for angle in range(0, 360, 45):
                a = math.radians(angle)
                cx, cy = x - s * 0.05 + s * 0.3 * math.cos(a), y + s * 0.22 + s * 0.26 * math.sin(a)
                d.ellipse([cx - s * 0.16, cy - s * 0.16, cx + s * 0.16, cy + s * 0.16], fill=light,
                          outline=edge, width=max(int(s * 0.02), 1))
        head_y = y - s * (0.75 if long_neck else 0.45)
        if long_neck:
            d.rounded_rectangle([x + s * 0.16, head_y, x + s * 0.44, y + s * 0.1], radius=int(s * 0.14), fill=body)
        head_x = x + s * (0.3 if long_neck else 0.36)
        head = s * 0.3
        if ear == "round":
            for side in (-1, 1):
                d.ellipse([head_x + side * head * 0.7 - head * 0.34, head_y - head * 0.95,
                           head_x + side * head * 0.7 + head * 0.34, head_y - head * 0.27], fill=body)
        elif ear == "point":
            for side in (-1, 1):
                d.polygon([(head_x + side * head * 0.55, head_y - head * 0.5),
                           (head_x + side * head * 0.95, head_y - head * 1.25),
                           (head_x + side * head * 0.15, head_y - head * 0.9)], fill=body)
        elif ear == "long":
            for side in (-1, 1):
                d.ellipse([head_x + side * head * 0.4 - head * 0.2, head_y - head * 1.9,
                           head_x + side * head * 0.4 + head * 0.2, head_y - head * 0.4], fill=body)
        if mark == "mane":
            d.ellipse([head_x - head * 1.5, head_y - head * 1.5, head_x + head * 1.5, head_y + head * 1.5],
                      fill=(198, 128, 46))
        d.ellipse([head_x - head, head_y - head, head_x + head, head_y + head], fill=body, outline=edge,
                  width=max(int(s * 0.03), 2))
        if mark == "horns":
            for side in (-1, 1):
                d.ellipse([head_x + side * head * 0.9 - head * 0.16, head_y - head * 1.15,
                           head_x + side * head * 0.9 + head * 0.16, head_y - head * 0.75], fill=(214, 200, 176))
        if mark == "trunk":
            # Хобот и большое ухо: без них слон это просто серое животное.
            d.ellipse([head_x - head * 1.5, head_y - head * 0.9, head_x - head * 0.2, head_y + head * 0.9],
                      fill=light, outline=edge, width=max(int(s * 0.03), 2))
            d.rounded_rectangle([head_x + head * 0.55, head_y + head * 0.2, head_x + head * 0.95, head_y + head * 1.6],
                                radius=int(head * 0.2), fill=body, outline=edge, width=max(int(s * 0.03), 2))
        if muzzle:
            d.ellipse([head_x - head * 0.1, head_y + head * 0.1, head_x + head * 0.85, head_y + head * 0.75],
                      fill=muzzle)
        d.ellipse([head_x + head * 0.05, head_y - head * 0.3, head_x + head * 0.25, head_y - head * 0.05],
                  fill=(40, 46, 64))
        d.ellipse([head_x + head * 0.55, head_y - head * 0.3, head_x + head * 0.75, head_y - head * 0.05],
                  fill=(40, 46, 64))
        d.ellipse([head_x + head * 0.62, head_y + head * 0.18, head_x + head * 0.92, head_y + head * 0.44],
                  fill=(60, 46, 52))
        if tail == "short":
            d.ellipse([x - s * 0.78, y + s * 0.05, x - s * 0.5, y + s * 0.33], fill=light)
        elif tail == "long":
            d.arc([x - s * 1.0, y - s * 0.5, x - s * 0.3, y + s * 0.4], 20, 250, fill=body,
                  width=max(int(s * 0.12), 4))
        for offset in (-0.38, 0.06, 0.3):
            d.rounded_rectangle([x + s * offset, y + s * 0.45, x + s * (offset + 0.16), y + s * 0.85],
                                radius=int(s * 0.07), fill=body)
    return draw


def _bird(d, x, y, s):
    s = s * 100
    d.ellipse([x - s * 0.5, y - s * 0.3, x + s * 0.45, y + s * 0.45], fill=(84, 158, 226))
    d.ellipse([x + s * 0.2, y - s * 0.62, x + s * 0.72, y - s * 0.1], fill=(84, 158, 226))
    d.polygon([(x + s * 0.66, y - s * 0.42), (x + s * 0.96, y - s * 0.3), (x + s * 0.66, y - s * 0.2)],
              fill=(246, 176, 60))
    d.ellipse([x + s * 0.5, y - s * 0.5, x + s * 0.6, y - s * 0.4], fill=(30, 38, 60))
    d.ellipse([x - s * 0.3, y - s * 0.12, x + s * 0.24, y + s * 0.3], fill=(140, 198, 246))
    d.polygon([(x - s * 0.5, y + s * 0.1), (x - s * 0.95, y + s * 0.3), (x - s * 0.46, y + s * 0.42)],
              fill=(60, 128, 200))
    for offset in (-0.1, 0.16):
        d.line([x + s * offset, y + s * 0.42, x + s * offset, y + s * 0.72], fill=(246, 176, 60),
               width=max(int(s * 0.06), 2))


def _fish_obj(d, x, y, s):
    s = s * 100
    d.ellipse([x - s * 0.6, y - s * 0.4, x + s * 0.5, y + s * 0.4], fill=(64, 172, 214))
    d.polygon([(x + s * 0.4, y), (x + s * 0.92, y - s * 0.4), (x + s * 0.92, y + s * 0.4)], fill=(44, 140, 186))
    d.ellipse([x - s * 0.44, y - s * 0.16, x - s * 0.28, y], fill=(28, 36, 58))


def _snake(d, x, y, s):
    s = s * 100
    d.arc([x - s * 0.8, y - s * 0.5, x + s * 0.4, y + s * 0.4], 160, 20, fill=(86, 176, 106),
          width=max(int(s * 0.22), 6))
    d.arc([x - s * 0.3, y - s * 0.1, x + s * 0.9, y + s * 0.8], 180, 340, fill=(86, 176, 106),
          width=max(int(s * 0.22), 6))
    d.ellipse([x - s * 0.95, y - s * 0.62, x - s * 0.55, y - s * 0.22], fill=(106, 196, 126))
    d.ellipse([x - s * 0.86, y - s * 0.54, x - s * 0.76, y - s * 0.44], fill=(30, 40, 60))


def _tree(d, x, y, s):
    s = s * 100
    d.rectangle([x - s * 0.12, y, x + s * 0.12, y + s * 0.8], fill=(146, 100, 58))
    d.ellipse([x - s * 0.66, y - s * 0.9, x + s * 0.66, y + s * 0.16], fill=(64, 168, 104))
    d.ellipse([x - s * 0.4, y - s * 1.1, x + s * 0.34, y - s * 0.34], fill=(92, 194, 128))


def _cloud(d, x, y, s):
    s = s * 100
    d.ellipse([x - s * 0.7, y - s * 0.25, x - s * 0.1, y + s * 0.35], fill=(226, 234, 248))
    d.ellipse([x - s * 0.3, y - s * 0.5, x + s * 0.35, y + s * 0.3], fill=(238, 244, 254))
    d.ellipse([x + s * 0.05, y - s * 0.2, x + s * 0.7, y + s * 0.35], fill=(226, 234, 248))
    d.rounded_rectangle([x - s * 0.7, y + s * 0.05, x + s * 0.7, y + s * 0.35], radius=int(s * 0.15),
                        fill=(232, 240, 250))


def _snow(d, x, y, s):
    s = s * 100
    for angle in range(0, 180, 30):
        a = math.radians(angle)
        d.line([x - s * 0.7 * math.cos(a), y - s * 0.7 * math.sin(a),
                x + s * 0.7 * math.cos(a), y + s * 0.7 * math.sin(a)],
               fill=(150, 196, 240), width=max(int(s * 0.09), 3))
    d.ellipse([x - s * 0.16, y - s * 0.16, x + s * 0.16, y + s * 0.16], fill=(206, 230, 250))


def _car(d, x, y, s):
    s = s * 100
    d.rounded_rectangle([x - s * 0.85, y - s * 0.1, x + s * 0.85, y + s * 0.42], radius=int(s * 0.18),
                        fill=(226, 72, 84))
    d.rounded_rectangle([x - s * 0.5, y - s * 0.55, x + s * 0.45, y - s * 0.02], radius=int(s * 0.16),
                        fill=(240, 110, 118))
    d.rounded_rectangle([x - s * 0.42, y - s * 0.46, x - s * 0.04, y - s * 0.1], radius=int(s * 0.08),
                        fill=(206, 232, 250))
    d.rounded_rectangle([x + s * 0.04, y - s * 0.46, x + s * 0.38, y - s * 0.1], radius=int(s * 0.08),
                        fill=(206, 232, 250))
    for side in (-0.48, 0.48):
        d.ellipse([x + s * side - s * 0.2, y + s * 0.28, x + s * side + s * 0.2, y + s * 0.68], fill=(52, 58, 78))
        d.ellipse([x + s * side - s * 0.08, y + s * 0.4, x + s * side + s * 0.08, y + s * 0.56], fill=(180, 188, 208))


def _bus(d, x, y, s):
    s = s * 100
    d.rounded_rectangle([x - s * 0.9, y - s * 0.6, x + s * 0.9, y + s * 0.45], radius=int(s * 0.16),
                        fill=(250, 186, 60))
    for index in range(3):
        left = x - s * 0.75 + index * s * 0.5
        d.rounded_rectangle([left, y - s * 0.45, left + s * 0.38, y - s * 0.05], radius=int(s * 0.07),
                            fill=(206, 232, 250))
    for side in (-0.5, 0.5):
        d.ellipse([x + s * side - s * 0.2, y + s * 0.3, x + s * side + s * 0.2, y + s * 0.7], fill=(52, 58, 78))


def _plane(d, x, y, s):
    s = s * 100
    body = (226, 232, 245)
    wing = (110, 158, 220)
    d.polygon([(x - s * 0.1, y - s * 0.08), (x + s * 0.5, y - s * 0.62), (x + s * 0.66, y - s * 0.5),
               (x + s * 0.34, y + s * 0.02)], fill=wing)
    d.polygon([(x - s * 0.1, y + s * 0.08), (x + s * 0.5, y + s * 0.62), (x + s * 0.66, y + s * 0.5),
               (x + s * 0.34, y - s * 0.02)], fill=(88, 134, 198))
    d.rounded_rectangle([x - s * 0.9, y - s * 0.16, x + s * 0.7, y + s * 0.16], radius=int(s * 0.16), fill=body)
    d.polygon([(x + s * 0.6, y - s * 0.16), (x + s * 0.98, y), (x + s * 0.6, y + s * 0.16)], fill=(196, 206, 228))
    d.polygon([(x - s * 0.86, y - s * 0.14), (x - s * 0.62, y - s * 0.56), (x - s * 0.46, y - s * 0.14)], fill=wing)
    d.ellipse([x + s * 0.24, y - s * 0.09, x + s * 0.42, y + s * 0.09], fill=(150, 200, 244))
    d.ellipse([x - s * 0.02, y - s * 0.09, x + s * 0.16, y + s * 0.09], fill=(150, 200, 244))


def _bike(d, x, y, s):
    s = s * 100
    for side in (-0.5, 0.5):
        d.ellipse([x + s * side - s * 0.36, y - s * 0.36, x + s * side + s * 0.36, y + s * 0.36],
                  outline=(52, 58, 78), width=max(int(s * 0.09), 3))
    d.line([x - s * 0.5, y, x - s * 0.1, y - s * 0.42], fill=(226, 72, 84), width=max(int(s * 0.08), 3))
    d.line([x - s * 0.1, y - s * 0.42, x + s * 0.5, y], fill=(226, 72, 84), width=max(int(s * 0.08), 3))
    d.line([x - s * 0.5, y, x + s * 0.2, y], fill=(226, 72, 84), width=max(int(s * 0.08), 3))
    d.rounded_rectangle([x - s * 0.26, y - s * 0.56, x + s * 0.04, y - s * 0.44], radius=int(s * 0.05),
                        fill=(52, 58, 78))


OBJECTS.update({
    "man": _figure("short", (72, 108, 190), beard=True),
    "woman": _figure("long", (216, 92, 140)),
    "boy": _figure("short", (86, 168, 226), small=True),
    "child": _figure("short", (246, 176, 60), small=True),
    "children": _figure("long", (140, 196, 120), small=True),
    "kid": _figure("short", (246, 176, 60), small=True),
    "baby": _figure("short", (250, 206, 226), small=True),
    "person": _figure("short", (110, 122, 170)),
    "people": _figure("short", (110, 122, 170)),
    "friend": _figure("short", (86, 168, 226)),
    "mother": _figure("long", (216, 92, 140)),
    "mom": _figure("long", (216, 92, 140)),
    "father": _figure("short", (72, 108, 190), beard=True),
    "dad": _figure("short", (72, 108, 190), beard=True),
    "sister": _figure("long", (240, 140, 176), small=True),
    "brother": _figure("short", (96, 158, 214), small=True),
    "son": _figure("short", (96, 158, 214), small=True),
    "daughter": _figure("long", (240, 140, 176), small=True),
    "grandmother": _figure("long", (168, 140, 196), grey_hair=True),
    "grandfather": _figure("short", (120, 130, 160), grey_hair=True, beard=True),
    "teacher": _figure("long", (86, 132, 200)),
    "student": _figure("short", (246, 176, 60), small=True),
    "doctor": _figure("short", (238, 242, 250)),
    "nurse": _figure("long", (238, 242, 250)),
    "husband": _figure("short", (72, 108, 190), beard=True),
    "wife": _figure("long", (216, 92, 140)),

    "horse": _animal((166, 116, 66), "point", tail="long", long_neck=True),
    "cow": _animal((238, 240, 248), "round", muzzle=(246, 186, 196), mark="spots"),
    "sheep": _animal((240, 242, 250), "long", muzzle=(226, 214, 214), mark="wool"),
    "goat": _animal((214, 214, 222), "point", muzzle=(240, 236, 236), mark="horns"),
    "chicken": _bird, "bird": _bird,
    "mouse": _animal((176, 182, 200), "round", tail="long"),
    "rabbit": _animal((242, 244, 250), "long", muzzle=(250, 214, 224)),
    "bear": _animal((140, 96, 62), "round", muzzle=(206, 168, 122)),
    "wolf": _animal((132, 140, 160), "point", tail="long", muzzle=(196, 202, 216)),
    "fox": _animal((236, 138, 62), "point", tail="long", muzzle=(250, 246, 242)),
    "lion": _animal((234, 176, 76), "round", tail="long", muzzle=(250, 224, 168), mark="mane"),
    "elephant": _animal((150, 162, 186), "round", mark="trunk"),
    "monkey": _animal((150, 108, 70), "round", tail="long", muzzle=(226, 186, 146)),
    "snake": _snake, "frog": _animal((104, 186, 108), "round", muzzle=(160, 214, 150)),
    "animal": _animal((166, 116, 66), "round", muzzle=(214, 178, 140)),
    "fish": _fish_obj,

    "tree": _tree, "cloud": _cloud, "snow": _snow, "winter": _snow, "sky": _cloud,
    "car": _car, "bus": _bus, "plane": _plane, "bike": _bike, "train": _bus,
})


# ─────────────────────────────── действия, тело, еда, места
#
# Действие показать труднее предмета: нужна поза. Заготовка одна, разница в
# положении рук и ног, потому что «бежит» и «прыгает» ребёнок узнаёт по силуэту.

def _pose(arms, legs, extra=None, cloth=(86, 132, 226)):
    def draw(d, x, y, s):
        s = s * 100
        head = s * 0.2
        top = y - s * 0.62
        d.ellipse([x - head, top - head, x + head, top + head], fill=SKIN)
        d.chord([x - head, top - head * 1.35, x + head, top + head * 0.7], 180, 360, fill=(74, 56, 44))
        d.rounded_rectangle([x - s * 0.2, top + head, x + s * 0.2, y + s * 0.28], radius=int(s * 0.12), fill=cloth)
        width = max(int(s * 0.11), 4)
        for (dx, dy) in arms:
            d.line([x, top + head * 1.6, x + s * dx, top + head * 1.6 + s * dy], fill=SKIN, width=width)
        for (dx, dy) in legs:
            d.line([x, y + s * 0.26, x + s * dx, y + s * 0.26 + s * dy], fill=(60, 76, 128), width=width)
        if extra:
            extra(d, x, y, s)
    return draw


def _book_in_hands(d, x, y, s):
    d.rounded_rectangle([x - s * 0.34, y - s * 0.28, x + s * 0.34, y + s * 0.06], radius=int(s * 0.05),
                        fill=(226, 92, 92))
    d.line([x, y - s * 0.28, x, y + s * 0.06], fill=(250, 250, 252), width=max(int(s * 0.04), 2))


def _note(d, x, y, s):
    d.ellipse([x + s * 0.3, y - s * 0.62, x + s * 0.46, y - s * 0.46], fill=(96, 132, 214))
    d.line([x + s * 0.46, y - s * 0.54, x + s * 0.46, y - s * 0.9], fill=(96, 132, 214), width=max(int(s * 0.05), 2))


def _z(d, x, y, s):
    for index, step in enumerate((0.0, 0.16, 0.3)):
        size = s * (0.14 - index * 0.03)
        cx, cy = x + s * (0.34 + step), y - s * (0.75 + step)
        d.line([cx - size, cy - size, cx + size, cy - size], fill=(140, 158, 200), width=max(int(s * 0.04), 2))
        d.line([cx + size, cy - size, cx - size, cy + size], fill=(140, 158, 200), width=max(int(s * 0.04), 2))
        d.line([cx - size, cy + size, cx + size, cy + size], fill=(140, 158, 200), width=max(int(s * 0.04), 2))


def _waves(d, x, y, s):
    for index in range(3):
        yy = y + s * (0.3 + index * 0.16)
        d.arc([x - s * 0.9, yy - s * 0.12, x - s * 0.1, yy + s * 0.12], 180, 360, fill=(96, 176, 226),
              width=max(int(s * 0.06), 2))
        d.arc([x - s * 0.1, yy - s * 0.12, x + s * 0.7, yy + s * 0.12], 0, 180, fill=(96, 176, 226),
              width=max(int(s * 0.06), 2))


def _part(shape):
    """Часть тела: крупно и отдельно, как в букваре."""
    def draw(d, x, y, s):
        s = s * 100
        if shape == "head":
            d.ellipse([x - s * 0.6, y - s * 0.7, x + s * 0.6, y + s * 0.7], fill=SKIN)
            d.chord([x - s * 0.6, y - s * 0.95, x + s * 0.6, y + s * 0.15], 180, 360, fill=(74, 56, 44))
            d.ellipse([x - s * 0.3, y - s * 0.1, x - s * 0.16, y + s * 0.04], fill=(48, 54, 74))
            d.ellipse([x + s * 0.16, y - s * 0.1, x + s * 0.3, y + s * 0.04], fill=(48, 54, 74))
            d.arc([x - s * 0.28, y + s * 0.14, x + s * 0.28, y + s * 0.5], 20, 160, fill=(196, 118, 106),
                  width=max(int(s * 0.07), 3))
        elif shape == "eye":
            d.ellipse([x - s * 0.8, y - s * 0.42, x + s * 0.8, y + s * 0.42], fill=(250, 250, 252),
                      outline=(150, 162, 190), width=max(int(s * 0.05), 2))
            d.ellipse([x - s * 0.28, y - s * 0.32, x + s * 0.28, y + s * 0.32], fill=(74, 138, 200))
            d.ellipse([x - s * 0.12, y - s * 0.16, x + s * 0.12, y + s * 0.16], fill=(30, 36, 56))
        elif shape == "ear":
            d.ellipse([x - s * 0.45, y - s * 0.7, x + s * 0.45, y + s * 0.7], fill=SKIN)
            d.arc([x - s * 0.2, y - s * 0.4, x + s * 0.3, y + s * 0.35], 40, 300, fill=(214, 160, 128),
                  width=max(int(s * 0.09), 3))
        elif shape == "mouth":
            d.ellipse([x - s * 0.7, y - s * 0.4, x + s * 0.7, y + s * 0.4], fill=(206, 88, 96))
            d.chord([x - s * 0.7, y - s * 0.4, x + s * 0.7, y + s * 0.4], 0, 180, fill=(178, 60, 74))
            d.rounded_rectangle([x - s * 0.5, y - s * 0.12, x + s * 0.5, y + s * 0.06], radius=int(s * 0.06),
                                fill=(250, 250, 252))
        elif shape == "tooth":
            d.rounded_rectangle([x - s * 0.42, y - s * 0.6, x + s * 0.42, y + s * 0.2], radius=int(s * 0.18),
                                fill=(250, 250, 252), outline=(190, 200, 220), width=max(int(s * 0.04), 2))
            # Корни того же светлого цвета, что и коронка, но с обводкой: без
            # неё зуб на белом фоне пропадал целиком.
            for side in (-1, 1):
                d.polygon([(x + side * s * 0.42, y + s * 0.1), (x + side * s * 0.1, y + s * 0.72),
                           (x + side * s * 0.02, y + s * 0.1)], fill=(250, 250, 252),
                          outline=(190, 200, 220))
        elif shape == "heart":
            d.ellipse([x - s * 0.6, y - s * 0.6, x + s * 0.05, y + s * 0.1], fill=(226, 72, 92))
            d.ellipse([x - s * 0.05, y - s * 0.6, x + s * 0.6, y + s * 0.1], fill=(226, 72, 92))
            d.polygon([(x - s * 0.58, y - s * 0.16), (x + s * 0.58, y - s * 0.16), (x, y + s * 0.75)],
                      fill=(226, 72, 92))
        elif shape == "foot":
            d.ellipse([x - s * 0.5, y - s * 0.5, x + s * 0.3, y + s * 0.6], fill=SKIN)
            for index in range(4):
                cx = x + s * (0.16 + index * 0.14)
                d.ellipse([cx - s * 0.1, y - s * 0.45 + index * s * 0.16, cx + s * 0.1,
                           y - s * 0.25 + index * s * 0.16], fill=SKIN)
    return draw


def _place(kind):
    """Место: несколько домов, а не один. Город от села отличается их числом."""
    def draw(d, x, y, s):
        s = s * 100
        wall = (150, 176, 226)
        roof = (86, 116, 190)
        if kind == "city":
            heights = (1.1, 1.5, 0.9, 1.3)
        elif kind == "town":
            heights = (0.8, 1.0, 0.7)
        else:
            heights = (0.9,)
        step = s * 1.5 / max(len(heights), 1)
        left = x - step * (len(heights) - 1) / 2
        for index, height in enumerate(heights):
            cx = left + index * step
            d.rounded_rectangle([cx - step * 0.34, y + s * 0.6 - s * height, cx + step * 0.34, y + s * 0.6],
                                radius=int(s * 0.05), fill=wall)
            if kind == "village":
                d.polygon([(cx - step * 0.46, y + s * 0.6 - s * height),
                           (cx, y + s * 0.6 - s * height - s * 0.4),
                           (cx + step * 0.46, y + s * 0.6 - s * height)], fill=roof)
            for row in range(int(height * 2)):
                yy = y + s * 0.45 - row * s * 0.32
                if yy > y + s * 0.6 - s * height + s * 0.1:
                    d.rectangle([cx - step * 0.16, yy - s * 0.16, cx + step * 0.16, yy], fill=(250, 232, 178))
        if kind == "village":
            d.ellipse([x + s * 0.6, y + s * 0.2, x + s * 1.1, y + s * 0.7], fill=(92, 178, 118))
        d.rounded_rectangle([x - s * 1.0, y + s * 0.6, x + s * 1.0, y + s * 0.74], radius=int(s * 0.06),
                            fill=(198, 206, 224))
    return draw


def _shirt(d, x, y, s):
    s = s * 100
    d.polygon([(x - s * 0.7, y - s * 0.3), (x - s * 0.35, y - s * 0.62), (x + s * 0.35, y - s * 0.62),
               (x + s * 0.7, y - s * 0.3), (x + s * 0.45, y - s * 0.05), (x + s * 0.45, y + s * 0.7),
               (x - s * 0.45, y + s * 0.7), (x - s * 0.45, y - s * 0.05)], fill=(86, 150, 226))
    d.polygon([(x - s * 0.16, y - s * 0.62), (x, y - s * 0.3), (x + s * 0.16, y - s * 0.62)], fill=(226, 236, 250))


def _shoe(d, x, y, s):
    s = s * 100
    d.rounded_rectangle([x - s * 0.7, y + s * 0.1, x + s * 0.7, y + s * 0.45], radius=int(s * 0.14),
                        fill=(52, 60, 82))
    d.polygon([(x - s * 0.6, y + s * 0.12), (x - s * 0.3, y - s * 0.5), (x + s * 0.2, y - s * 0.5),
               (x + s * 0.5, y + s * 0.12)], fill=(226, 72, 84))
    d.line([x - s * 0.3, y - s * 0.3, x + s * 0.24, y - s * 0.3], fill=(250, 250, 252), width=max(int(s * 0.06), 2))


def _money_obj(d, x, y, s):
    s = s * 100
    for index in range(2):
        off = index * s * 0.12
        d.rounded_rectangle([x - s * 0.8 + off, y - s * 0.4 + off, x + s * 0.6 + off, y + s * 0.3 + off],
                            radius=int(s * 0.08), fill=(112, 190, 140), outline=(72, 150, 104),
                            width=max(int(s * 0.03), 2))
    d.ellipse([x - s * 0.24, y - s * 0.16, x + s * 0.16, y + s * 0.24], fill=(240, 250, 244))


def _ticket(d, x, y, s):
    s = s * 100
    d.rounded_rectangle([x - s * 0.85, y - s * 0.4, x + s * 0.85, y + s * 0.4], radius=int(s * 0.1),
                        fill=(250, 206, 118))
    d.ellipse([x - s * 0.1, y - s * 0.5, x + s * 0.1, y - s * 0.3], fill=(247, 248, 252))
    d.ellipse([x - s * 0.1, y + s * 0.3, x + s * 0.1, y + s * 0.5], fill=(247, 248, 252))
    for index in range(3):
        d.line([x - s * 0.7, y - s * 0.16 + index * s * 0.16, x - s * 0.2, y - s * 0.16 + index * s * 0.16],
               fill=(190, 140, 60), width=max(int(s * 0.04), 2))


def _tv(d, x, y, s):
    s = s * 100
    d.rounded_rectangle([x - s * 0.9, y - s * 0.6, x + s * 0.9, y + s * 0.45], radius=int(s * 0.1),
                        fill=(52, 60, 82))
    d.rounded_rectangle([x - s * 0.8, y - s * 0.5, x + s * 0.8, y + s * 0.35], radius=int(s * 0.06),
                        fill=(150, 200, 244))
    d.rounded_rectangle([x - s * 0.2, y + s * 0.45, x + s * 0.2, y + s * 0.6], radius=int(s * 0.05),
                        fill=(88, 96, 120))


def _paper(d, x, y, s):
    s = s * 100
    d.rounded_rectangle([x - s * 0.55, y - s * 0.75, x + s * 0.55, y + s * 0.75], radius=int(s * 0.06),
                        fill=(250, 250, 252), outline=(190, 200, 220), width=max(int(s * 0.04), 2))
    for index in range(4):
        yy = y - s * 0.45 + index * s * 0.3
        d.line([x - s * 0.36, yy, x + s * 0.36, yy], fill=(196, 206, 226), width=max(int(s * 0.05), 2))


def _rain(d, x, y, s):
    s = s * 100
    d.ellipse([x - s * 0.7, y - s * 0.55, x - s * 0.1, y + s * 0.05], fill=(196, 210, 232))
    d.ellipse([x - s * 0.3, y - s * 0.8, x + s * 0.35, y], fill=(214, 226, 244))
    d.ellipse([x + s * 0.05, y - s * 0.5, x + s * 0.7, y + s * 0.05], fill=(196, 210, 232))
    for index in range(4):
        cx = x - s * 0.45 + index * s * 0.3
        d.line([cx, y + s * 0.2, cx - s * 0.1, y + s * 0.6], fill=(96, 160, 226), width=max(int(s * 0.06), 2))


def _star(d, x, y, s):
    s = s * 100
    points = []
    for index in range(10):
        angle = math.radians(-90 + index * 36)
        radius = s * (0.8 if index % 2 == 0 else 0.34)
        points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))
    d.polygon(points, fill=(250, 206, 60))


OBJECTS.update({
    "run": _pose([(-0.4, 0.1), (0.4, -0.1)], [(-0.35, 0.3), (0.35, 0.24)]),
    "walk": _pose([(-0.25, 0.25), (0.25, 0.2)], [(-0.2, 0.4), (0.22, 0.38)]),
    "jump": _pose([(-0.35, -0.35), (0.35, -0.35)], [(-0.3, 0.28), (0.3, 0.28)]),
    "swim": _pose([(-0.45, -0.1), (0.45, 0.05)], [(-0.3, 0.2), (0.35, 0.16)], extra=_waves),
    "dance": _pose([(-0.4, -0.3), (0.35, 0.25)], [(-0.3, 0.36), (0.34, 0.2)], cloth=(226, 92, 148)),
    "sing": _pose([(-0.2, 0.3), (0.3, -0.3)], [(-0.16, 0.42), (0.16, 0.42)], extra=_note),
    "play": _pose([(-0.35, -0.2), (0.35, -0.2)], [(-0.24, 0.4), (0.24, 0.4)], cloth=(246, 176, 60)),
    "read": _pose([(-0.28, 0.2), (0.28, 0.2)], [(-0.2, 0.42), (0.2, 0.42)], extra=_book_in_hands),
    "write": _pose([(-0.2, 0.3), (0.34, 0.16)], [(-0.2, 0.42), (0.2, 0.42)]),
    "draw": _pose([(-0.2, 0.3), (0.36, 0.1)], [(-0.2, 0.42), (0.2, 0.42)], cloth=(140, 196, 120)),
    "sleep": _pose([(-0.3, 0.16), (0.3, 0.16)], [(-0.2, 0.4), (0.2, 0.4)], extra=_z, cloth=(140, 158, 216)),
    "eat": _pose([(-0.24, 0.1), (0.2, -0.2)], [(-0.2, 0.42), (0.2, 0.42)]),
    "drink": _pose([(-0.24, 0.2), (0.16, -0.3)], [(-0.2, 0.42), (0.2, 0.42)]),
    "help": _pose([(-0.42, -0.1), (0.42, -0.1)], [(-0.24, 0.4), (0.24, 0.4)], cloth=(96, 186, 150)),
    "wash": _pose([(-0.26, 0.24), (0.26, 0.24)], [(-0.2, 0.42), (0.2, 0.42)], cloth=(120, 190, 226)),
    "work": _pose([(-0.3, 0.2), (0.3, 0.2)], [(-0.2, 0.42), (0.2, 0.42)], cloth=(110, 122, 170)),

    "head": _part("head"), "face": _part("head"), "eye": _part("eye"), "ear": _part("ear"),
    "mouth": _part("mouth"), "tooth": _part("tooth"), "heart": _part("heart"), "foot": _part("foot"),

    "city": _place("city"), "town": _place("town"), "village": _place("village"),
    "home": _house, "room": _window_obj, "building": _place("town"),

    "shirt": _shirt, "clothes": _shirt, "jacket": _shirt, "shoes": _shoe, "shoe": _shoe,
    "money": _money_obj, "card": _ticket, "ticket": _ticket, "tv": _tv, "paper": _paper,
    "rain": _rain, "rainy": _rain, "star": _star, "sunny": _sun, "weather": _cloud,
})

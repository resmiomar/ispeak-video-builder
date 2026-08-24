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
# Ширина рисунка при scale = 1. Совпадает с размахом рисованных предметов,
# поэтому подмена файлом не меняет вёрстку карточки.
ASSET_BOX = 220
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

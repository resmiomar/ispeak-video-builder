#!/usr/bin/env python3
"""
Ведущие видеовыпусков: мама и сын.

Имена персонажей живут в тексте выпуска, а файлы картинок называются по роли
(`mom-`, `son-`): имя может смениться ещё раз, а роль нет.

Персонаж берётся из готовых картинок, если они положены в assets/mascot, и
рисуется кодом, если картинок нет. Второе это запасной вариант: выпуск должен
собираться даже до того, как художник нарисовал героя.

Имена файлов: <поза>-<closed|open>.png, например wave-open.png. Два состояния
рта нужны, потому что персонаж говорит: рот открывается по громкости звука.
Готовая картинка с одним ртом висела бы открытой всю минуту.

Дальше про запасного персонажа, рисованного кодом. Он временный и стоит в
кадре, пока не пришли картинки настоящего Чипа.

Почему не кот. Кот в первой версии был безымянной рыжей заготовкой: такой
персонаж есть у половины детских курсов, он ничего не говорит о продукте и
не запоминается. Ирби это детёныш снежного барса, символ узнаваемый в
Казахстане и в Средней Азии, то есть ровно там, где наша аудитория, и при
этом не занятый другими школьными приложениями.

Почему нарисован кодом, а не картинкой. Персонаж должен открывать рот в такт
голосу и менять позу в каждой сцене. Готовыми картинками это означало бы
сотни файлов на каждую комбинацию; здесь одна функция и кэш.

Сглаживание. Pillow рисует фигуры без сглаживания, и на краях появляется
лестница, особенно заметная на крупных дугах морды. Поэтому персонаж
рисуется вдвое крупнее на прозрачном слое и уменьшается фильтром LANCZOS,
а готовый слой кэшируется: в кадре меняется только рот, остальное совпадает.
"""
import json
import math
import os
from PIL import Image, ImageDraw

# Нарицательный размер персонажа при масштабе 1.0.
BOX_W, BOX_H = 440, 560
SS = 2  # во столько раз крупнее рисуем ради сглаживания

FUR = (240, 245, 253)
FUR_SHADE = (206, 217, 238)
FUR_DEEP = (176, 190, 216)
BELLY = (255, 255, 255)
SPOT = (92, 102, 138)
INK = (38, 33, 62)
NOSE = (240, 150, 170)
EAR_IN = (246, 198, 206)
IRIS = (74, 178, 214)
IRIS_DEEP = (44, 132, 176)
TAIL = (206, 216, 236)
TAIL_RING = (150, 164, 198)
SCARF = (79, 70, 229)
SCARF_DEEP = (58, 50, 190)
BLUSH = (250, 190, 196)

POSES = ("sit", "wave", "point", "think", "talk", "cheer")
FACES = ("neutral", "happy", "thinking", "proud")


def _spots(draw, points, size, colour=SPOT):
    """Розетки барса: кольцо с пятном внутри, размеры чуть разные.

    Ровные одинаковые точки читаются как горошек на ткани, поэтому каждая
    следующая розетка немного меньше и смещена.
    """
    for index, (x, y) in enumerate(points):
        r = size * (1.0 if index % 3 == 0 else 0.82 if index % 3 == 1 else 0.66)
        draw.ellipse([x - r, y - r * 0.82, x + r, y + r * 0.82],
                     outline=colour, width=max(int(r * 0.34), 2))
        draw.ellipse([x - r * 0.24, y - r * 0.2, x + r * 0.24, y + r * 0.2], fill=colour)


def _bezier(p0, p1, p2, p3, steps=26):
    """Кубическая кривая точками: Pillow не умеет кривые, только ломаные."""
    out = []
    for index in range(steps + 1):
        t = index / steps
        u = 1 - t
        x = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
        y = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
        out.append((x, y))
    return out


def _tail(draw, phase):
    """Хвост барса длиннее тела и загибается кверху.

    Рисуется не одной линией, а цепочкой кругов с убывающим радиусом: линия
    постоянной толщины выглядела как труба, а хвост должен сужаться к концу.
    """
    swing = math.sin(phase * 1.5) * 20
    path = _bezier((144, 470), (40, 486), (-12, 372 + swing * 0.5), (54, 250 + swing))
    total = len(path) - 1
    for index, (x, y) in enumerate(path):
        r = 30 - 13 * (index / total)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=TAIL)
    for t in (0.34, 0.58, 0.80):
        index = int(total * t)
        x, y = path[index]
        nx, ny = path[min(index + 2, total)]
        dx, dy = nx - x, ny - y
        length = max(math.hypot(dx, dy), 0.001)
        px, py = -dy / length, dx / length
        r = 30 - 13 * t
        draw.line([(x - px * r, y - py * r), (x + px * r, y + py * r)], fill=TAIL_RING, width=13)
    tip = path[-1]
    draw.ellipse([tip[0] - 20, tip[1] - 20, tip[0] + 20, tip[1] + 20], fill=FUR)


def _arm(draw, side, pose):
    """Лапа. Правая (side=1) меняется от позы, левая почти всегда у тела."""
    base_x = 220 + side * 96
    if side == 1 and pose == "wave":
        draw.line([(base_x, 380), (base_x + 52, 300), (base_x + 40, 236)],
                  fill=FUR, width=42, joint="curve")
        draw.ellipse([base_x + 12, 202, base_x + 76, 266], fill=FUR, outline=FUR_SHADE, width=3)
        return
    if side == 1 and pose == "point":
        # Лапа короткая, с подушечками: длинная «палка» читалась как кость.
        draw.line([(base_x - 12, 386), (base_x + 26, 356), (base_x + 52, 342)],
                  fill=FUR, width=44, joint="curve")
        draw.ellipse([base_x + 30, 312, base_x + 88, 370], fill=FUR, outline=FUR_SHADE, width=3)
        for dx, dy in ((50, 324), (68, 330), (78, 346)):
            draw.ellipse([base_x + dx - 9, dy - 9, base_x + dx + 9, dy + 9], fill=EAR_IN)
        return
    if side == 1 and pose == "think":
        draw.line([(base_x, 386), (base_x - 6, 320), (base_x - 34, 282)],
                  fill=FUR, width=40, joint="curve")
        draw.ellipse([base_x - 62, 254, base_x - 6, 310], fill=FUR, outline=FUR_SHADE, width=3)
        return
    if pose == "cheer":
        draw.line([(base_x, 380), (base_x + side * 46, 296), (base_x + side * 44, 224)],
                  fill=FUR, width=42, joint="curve")
        draw.ellipse([base_x + side * 44 - 32, 192, base_x + side * 44 + 32, 256], fill=FUR, outline=FUR_SHADE, width=3)
        return
    draw.ellipse([base_x - 30, 344, base_x + 30, 452], fill=FUR, outline=FUR_SHADE, width=3)
    draw.ellipse([base_x - 26, 408, base_x + 26, 456], fill=BELLY)


def _body(draw, pose, phase):
    _tail(draw, phase)
    # Задние лапы видны из-под тела, иначе персонаж «висит в воздухе».
    draw.ellipse([112, 430, 216, 504], fill=FUR_SHADE)
    draw.ellipse([224, 430, 328, 504], fill=FUR_SHADE)
    draw.rounded_rectangle([112, 296, 328, 492], radius=104, fill=FUR, outline=FUR_SHADE, width=3)
    draw.ellipse([158, 348, 282, 484], fill=BELLY)
    _spots(draw, [(138, 336), (306, 350), (130, 402), (312, 416)], 15)
    _arm(draw, -1, pose)
    _arm(draw, 1, pose)
    # Шарф цвета бренда: единственное цветное пятно на персонаже, поэтому
    # взгляд идёт от него к лицу, а не к лапам.
    draw.rounded_rectangle([146, 286, 294, 330], radius=22, fill=SCARF)
    draw.polygon([(262, 320), (306, 344), (286, 386), (250, 344)], fill=SCARF_DEEP)


def _ears(draw):
    """Уши маленькие и круглые: острые треугольники читаются как кот."""
    for side in (-1, 1):
        cx = 220 + side * 74
        draw.ellipse([cx - 44, 84, cx + 44, 176], fill=FUR)
        draw.ellipse([cx - 26, 104, cx + 26, 164], fill=EAR_IN)
        draw.ellipse([cx - 44, 84, cx + 44, 176], outline=FUR_SHADE, width=3)


def _eyes(draw, face):
    for side in (-1, 1):
        cx, cy = 220 + side * 52, 214
        if face == "happy":
            # Довольные глаза это дуги: сглаживание дуг хуже, поэтому дуга
            # рисуется толстой линией по точкам, а не методом arc.
            pts = [(cx - 30 + i * 6, cy + 10 - int(14 * math.sin(math.pi * i / 10))) for i in range(11)]
            draw.line(pts, fill=INK, width=9, joint="curve")
            continue
        draw.ellipse([cx - 32, cy - 34, cx + 32, cy + 34], fill=(255, 255, 255))
        look = 6 if face == "thinking" else 0
        draw.ellipse([cx - 22 + look, cy - 24, cx + 22 + look, cy + 24], fill=IRIS)
        draw.ellipse([cx - 12 + look, cy - 14, cx + 12 + look, cy + 18], fill=IRIS_DEEP)
        draw.ellipse([cx - 11 + look, cy - 12, cx + 11 + look, cy + 14], fill=INK)
        draw.ellipse([cx - 9 + look, cy - 20, cx + 3 + look, cy - 8], fill=(255, 255, 255))
        draw.ellipse([cx + 4 + look, cy + 4, cx + 12 + look, cy + 12], fill=(255, 255, 255))
    if face == "thinking":
        draw.line([(150, 158), (206, 170)], fill=INK, width=8)
        draw.line([(234, 168), (290, 150)], fill=INK, width=8)
    if face == "proud":
        for x, y, r in ((110, 150, 12), (330, 168, 9), (96, 226, 8)):
            draw.line([(x - r, y), (x + r, y)], fill=(255, 214, 102), width=5)
            draw.line([(x, y - r), (x, y + r)], fill=(255, 214, 102), width=5)


def _muzzle(draw, mouth, face):
    draw.ellipse([168, 246, 232, 300], fill=BELLY)
    draw.ellipse([208, 246, 272, 300], fill=BELLY)
    draw.ellipse([182, 272, 212, 292], fill=BLUSH)
    draw.ellipse([228, 272, 258, 292], fill=BLUSH)
    draw.polygon([(206, 254), (234, 254), (220, 270)], fill=NOSE)
    open_h = 6 + mouth * 34
    if mouth > 0.12:
        draw.ellipse([220 - 20 - mouth * 8, 274, 220 + 20 + mouth * 8, 274 + open_h], fill=(120, 52, 66))
        draw.ellipse([220 - 12, 274 + open_h * 0.45, 220 + 12, 274 + open_h], fill=(214, 106, 122))
    else:
        pts = [(220 - 18 + i * 4, 278 + int(6 * math.sin(math.pi * i / 9))) for i in range(10)]
        draw.line(pts, fill=INK, width=6, joint="curve")
    if face == "happy" or face == "proud":
        for side in (-1, 1):
            cx = 220 + side * 96
            draw.ellipse([cx - 22, 246, cx + 22, 280], fill=BLUSH)


def _head(draw, face, mouth):
    _ears(draw)
    draw.ellipse([104, 108, 336, 320], fill=FUR)
    draw.ellipse([104, 108, 336, 320], outline=FUR_SHADE, width=3)
    _spots(draw, [(152, 158), (288, 158), (124, 212), (316, 212), (186, 132), (254, 132)], 12)
    # Чёлка: три пучка шерсти, чтобы макушка не была голым кругом.
    for x in (188, 220, 252):
        draw.polygon([(x - 16, 126), (x, 96), (x + 16, 126)], fill=FUR)
    _eyes(draw, face)
    _muzzle(draw, mouth, face)


PHASE_STEPS = 8
_cache: dict[tuple, Image.Image] = {}


def mascot_layer(pose, face, mouth, scale, phase, who="son"):
    """Готовый прозрачный слой с персонажем. Кэш по огрублённым параметрам."""
    # Фаза огрубляется до восьми положений за цикл: непрерывное значение
    # означало бы промах кэша на каждом кадре, то есть полную перерисовку
    # персонажа двадцать пять раз в секунду.
    step = int((phase * 1.6 % (2 * math.pi)) / (2 * math.pi) * PHASE_STEPS)
    key = (who, pose, face, round(mouth, 1), round(scale, 2), step)
    cached = _cache.get(key)
    if cached is not None:
        return cached
    img = Image.new("RGBA", (BOX_W * SS, BOX_H * SS), (0, 0, 0, 0))
    scaled = ImageDraw.Draw(img)

    class Scaled:
        """Обёртка: те же вызовы, но координаты умножаются на SS."""

        def __getattr__(self, name):
            method = getattr(scaled, name)

            def call(xy, *args, **kwargs):
                if isinstance(xy, (list, tuple)) and xy and isinstance(xy[0], (int, float)):
                    xy = [v * SS for v in xy]
                elif isinstance(xy, (list, tuple)):
                    xy = [(px * SS, py * SS) for px, py in xy]
                for word in ("width", "radius"):
                    if word in kwargs and kwargs[word]:
                        kwargs[word] = max(int(kwargs[word] * SS), 1)
                return method(xy, *args, **kwargs)

            return call

    canvas = Scaled()
    # Запасной рисунок мамы отличается цветом шарфа: пока не пришли настоящие
    # картинки, зритель должен видеть двух разных героев, а не одного дважды.
    global SCARF, SCARF_DEEP
    keep = (SCARF, SCARF_DEEP)
    if who == "mom":
        SCARF, SCARF_DEEP = (226, 68, 122), (186, 40, 92)
    _body(canvas, pose, phase)
    _head(canvas, face, mouth)
    SCARF, SCARF_DEEP = keep
    if len(_cache) > 400:
        _cache.clear()
    out = img.resize((max(int(BOX_W * scale), 1), max(int(BOX_H * scale), 1)), Image.LANCZOS)
    _cache[key] = out
    return out


# ─────────────────────────────── персонаж картинками
PHOTOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mascot")
# Рот считается открытым выше этого порога громкости. Ниже порога дыхание и
# паузы, и от них рот дёргался бы без причины.
MOUTH_OPEN = 0.22
_photos: dict[str, Image.Image | None] = {}


def photo(pose, mouth, who="son"):
    """Кадр персонажа под позу и состояние рта. Нет файла — None.

    Позы подставляются с запасом: нет «cheer-open» — берём «cheer-closed», нет
    и его — «sit». Иначе одна недостающая картинка ломала бы весь выпуск.
    """
    state = "open" if mouth >= MOUTH_OPEN else "closed"
    # У каждого персонажа свой набор: chip-sit-open.png, mom-point-closed.png.
    # Старые файлы без имени героя тоже принимаются, чтобы уже присланные
    # картинки Чипа не пришлось переименовывать.
    # Роль ищется под своим именем и под старым «chip-»: уже присланные
    # картинки переименовывать не придётся.
    prefixes = [f"{who}-"] + (["chip-"] if who == "son" else [])
    names = []
    for prefix in prefixes:
        names += [f"{prefix}{pose}-{state}", f"{prefix}{pose}-closed", f"{prefix}sit-{state}", f"{prefix}sit-closed"]
    # Одна картинка на персонажа: mom.png и son.png. Рот к ней дорисовывается
    # кодом, поэтому художнику хватает одной позы с закрытым ртом вместо
    # четырёх состояний. Разговор от этого не страдает: открывается только рот.
    names += [who]
    names += [f"{pose}-{state}", f"{pose}-closed", f"sit-{state}", "sit-closed"]
    for name in names:
        if name in _photos:
            if _photos[name] is not None:
                return _photos[name]
            continue
        path = os.path.join(PHOTOS, f"{name}.png")
        _photos[name] = Image.open(path).convert("RGBA") if os.path.exists(path) else None
        if _photos[name] is not None:
            return _photos[name]
    return None




# ─────────────────────────────── рот поверх готовой картинки
#
# Художник рисует персонажа один раз, с закрытым ртом. Открытый рот во время
# речи дорисовывается кодом: так на каждого героя нужна одна картинка вместо
# четырёх, и любую из них можно заменить, не трогая остальные.
#
# Где именно рот, задаётся долями ширины и высоты картинки в mouth.json рядом
# с ней. Значения по умолчанию подобраны под персонажа, сидящего лицом к нам,
# и правятся одним числом после первого же кадра.
MOUTH_SPOT = {"x": 0.5, "y": 0.42, "w": 0.10, "h": 0.075}
_mouths: dict[str, Image.Image] = {}


def mouth_spot(who):
    path = os.path.join(PHOTOS, "mouth.json")
    if not os.path.exists(path):
        return MOUTH_SPOT
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
        return {**MOUTH_SPOT, **data.get(who, {})}
    except Exception:
        # Кривой файл не должен ронять сборку: рот просто останется на месте
        # по умолчанию, и это видно на первом же кадре.
        return MOUTH_SPOT


def with_mouth(picture, who, mouth):
    """Копия картинки с открытым ртом. Закрытый рот оставляет её как есть."""
    if mouth < MOUTH_OPEN:
        return picture
    key = f"{who}:{round(mouth, 1)}:{picture.width}"
    ready = _mouths.get(key)
    if ready is not None:
        return ready
    spot = mouth_spot(who)
    layer = picture.copy()
    draw = ImageDraw.Draw(layer)
    cx, cy = picture.width * spot["x"], picture.height * spot["y"]
    half_w = picture.width * spot["w"] / 2
    half_h = picture.height * spot["h"] / 2 * (0.5 + mouth)
    draw.ellipse([cx - half_w, cy - half_h, cx + half_w, cy + half_h], fill=(120, 52, 60))
    draw.ellipse([cx - half_w * 0.55, cy + half_h * 0.05, cx + half_w * 0.55, cy + half_h * 0.85],
                 fill=(226, 118, 132))
    _mouths[key] = layer
    return layer


def paste_mascot(image, cx, bottom, scale, *, pose="sit", face="neutral", mouth=0.0, phase=0.0, who="son"):
    """Ставит персонажа так, чтобы низ лап лежал на заданной линии."""
    if scale <= 0:
        return
    picture = photo(pose, mouth, who)
    if picture is not None:
        picture = with_mouth(picture, who, mouth)
        # Высота та же, что у рисованного запасного персонажа, поэтому замена
        # картинками не меняет вёрстку кадра.
        height = max(int(BOX_H * scale), 1)
        width = max(int(picture.width * height / picture.height), 1)
        layer = picture.resize((width, height), Image.LANCZOS)
        bob = int(math.sin(phase * 2.2) * 7 * scale)
        image.paste(layer, (int(cx - width / 2), int(bottom - height + bob)), layer)
        return
    layer = mascot_layer(pose, face, mouth, scale, phase, who)
    # Покачивание остаётся плавным: оно двигает готовый слой, а не рисует его.
    bob = int(math.sin(phase * 2.2) * 7 * scale)
    # paste с маской, а не alpha_composite: кадр приходит в RGB.
    image.paste(layer, (int(cx - layer.width / 2), int(bottom - layer.height + bob)), layer)

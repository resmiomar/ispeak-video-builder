#!/usr/bin/env python3
"""
Рендер видеовыпусков по плану из scripts/video/plan.json.

Питон ничего не решает про содержание: что сказать и что показать посчитал
TypeScript, у которого есть доступ к ТЗ. Здесь только голос, кадры и сборка.

Три возрастных режима отличаются не только текстом (это в плане), но и видом:
у младших крупнее шрифт, медленнее речь и есть герои, у старших их нет и
кадр плотнее. Один темп на все возрасты неверен на обоих концах.

Запуск: scripts/video/.venv/bin/python scripts/video/render.py [id ...]
"""
import asyncio, hashlib, json, math, os, subprocess, sys, wave
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from art import draw_object, make_background, ease_out_back
from mascot import paste_mascot

W, H, FPS = 1920, 1080, 25
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
OUT = os.path.join(HERE, "out")
# Фирменный шрифт бренда. Лежит в проекте, а не в системе: сборка не должна
# зависеть от того, что установлено на конкретном маке. Montserrat переменный,
# поэтому начертание выбирается по имени, а не отдельным файлом.
FONT = os.path.join(HERE, "assets", "fonts", "Montserrat.ttf")
FALLBACK_FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def brand_font(size, weight="SemiBold"):
    """Шрифт нужного кегля и начертания, с запасным вариантом."""
    try:
        face = ImageFont.truetype(FONT, size)  # переменный файл
        face.set_variation_by_name(weight)
        return face
    except OSError:
        return ImageFont.truetype(FALLBACK_FONT, size)

# Палитра бренда: тёмно-синий и жёлтый, как на фирменном листе персонажа.
# Раньше кадр был фиолетово-мятным и с брендом не совпадал.
INK, CARD = (12, 18, 44), (22, 34, 79)
WHITE, MUTED = (255, 255, 255), (168, 180, 214)
INDIGO, RED, GREEN = (255, 198, 41), (255, 108, 108), (255, 198, 41)
NAVY, SKY = (27, 42, 99), (74, 144, 217)

# Голоса.
#
# По-английски младшим и средним говорит Ana: это детский голос, и он нравится
# детям больше взрослого диктора. Взрослый Ava звучит правильнее, но как
# радиоведущий, и ребёнку с ним скучно.
#
# У старших наоборот: подростку детский голос мешает, там говорит Emma.
VOICE = {
    "ru": "ru-RU-SvetlanaNeural",
    "kk": "kk-KZ-AigulNeural",
    "uz": "uz-UZ-MadinaNeural",
    "en": "en-US-AnaNeural",
}
VOICE_SENIOR = {**VOICE, "en": "en-US-EmmaMultilingualNeural"}

# Подстройка голоса мамы: тон выше и темп чуть медленнее. Ровный дикторский
# голос по умолчанию звучит строго, а с этой поправкой по-домашнему. Английский
# у Чипа не трогаем: детский голос и так на своём месте.
NATIVE_TUNE = {"pitch": "+12Hz", "rate": "-4%"}

# Вид и темп по возрасту.
#
# Речь идёт в обычном темпе на всех возрастах. Замедление на четверть, которое
# стояло здесь раньше, делало голос механическим: синтез при -25% тянет гласные
# и рвёт интонацию. Младшим нужна не медленная речь, а пауза между фразами и
# повтор, поэтому темп обычный, а разделяют фразы тишиной.
STYLE = {
    "G1": {"big": 300, "word": 150, "rate": "+0%", "gap": 0.40, "pause": 0.5, "hero": 1.30},
    "G2": {"big": 240, "word": 120, "rate": "+0%", "gap": 0.28, "pause": 0.4, "hero": 1.05},
    "G3": {"big": 200, "word": 104, "rate": "+0%", "gap": 0.18, "pause": 0.3, "hero": 0.0},
}

os.makedirs(WORK, exist_ok=True)
os.makedirs(OUT, exist_ok=True)



# ─────────────────────────────── темы оформления
#
# Два вида кадра вместо одного. Светлый для младших: белый экран дружелюбнее
# тёмного и совпадает с фирменным листом персонажа. Полосы для средних и
# старших: жёлтая плашка с картинкой сверху, синяя с текстом снизу, кадр
# читается с любого расстояния и работает обоими цветами бренда.
THEMES = {
    "light": {
        "bg": (247, 248, 252),
        "bg2": (236, 240, 250),
        "warm": (255, 243, 205),
        "panel": (255, 255, 255),
        "ink": (18, 26, 60),
        "word": (198, 128, 0),
        "muted": (110, 122, 155),
        "accent": (255, 198, 41),
        "hero_x": 1800,
        "mom_dx": -230,
        "hero_scale": 0.62,
        "mom_scale": 0.95,
        "text_x": 740,
        "text_w": 560,
        "art_x": 360,
    },
    "bands": {
        "bg": (18, 26, 60),
        "bg2": (12, 18, 44),
        "warm": (255, 198, 41),
        "panel": (255, 198, 41),
        "ink": (255, 255, 255),
        "word": (255, 198, 41),
        "muted": (170, 185, 220),
        "accent": (255, 198, 41),
        "hero_x": 150,
        "mom_dx": 215,
        "hero_scale": 0.52,
        "mom_scale": 0.72,
        "text_x": 620,
        "text_w": 1140,
        "art_x": 1120,
    },
}
THEME_BY_AGE = {"G1": "light", "G2": "bands", "G3": "bands"}


def theme_of(age):
    return THEMES[THEME_BY_AGE.get(age, "bands")]


# Готовые фоны кладутся сюда файлами <имя>.png, 16:9. Нет файла — рисуется
# свой фон цветами темы.
BACKGROUNDS = os.path.join(HERE, "assets", "backgrounds")
_bg_photos: dict[str, Image.Image | None] = {}


def background_photo(name):
    if not name:
        return None
    if name in _bg_photos:
        return _bg_photos[name]
    path = os.path.join(BACKGROUNDS, f"{name}.png")
    picture = None
    if os.path.exists(path):
        picture = Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)
    _bg_photos[name] = picture
    return picture


# ─────────────────────────────── кадры
# Фон пересчитывается не каждый кадр, а раз в полсекунды: пятна плывут
# медленно, разницы не видно, а времени сборки уходит в двенадцать раз меньше.
BG_STEP = 0.5
_bg_cache: dict[tuple[str, int], Image.Image] = {}


def background(age, phase, photo=None):
    """Фон кадра: готовая картинка, если положена, иначе свой мягкий фон.

    Поверх готовой картинки кладётся дымка цветом темы: без неё белый текст на
    пёстрой фотографии не читается, а читаемость слова здесь важнее красоты
    фона.
    """
    theme = theme_of(age)
    key = (age, photo or "", int(phase / BG_STEP))
    cached = _bg_cache.get(key)
    if cached is not None:
        return cached

    picture = background_photo(photo)
    if picture is not None:
        img = picture.copy()
        haze = Image.new("RGB", (W, H), theme["bg"])
        img = Image.blend(img, haze, 0.55)
    else:
        img = make_background((W, H), age, phase)
        if THEME_BY_AGE.get(age) == "light":
            # Светлая тема: мягкие пятна на белом, а не тёмный градиент.
            img = Image.new("RGB", (W, H), theme["bg"])
            draw = ImageDraw.Draw(img)
            draw.ellipse([-260, -320, 720, 640], fill=theme["bg2"])
            draw.ellipse([1380, 660, 2260, 1420], fill=theme["warm"])

    draw = ImageDraw.Draw(img)
    draw.text((80, 60), "iSpeak", font=brand_font(38, "Bold"), fill=theme["ink"])
    _bg_cache.clear()
    _bg_cache[key] = img
    return img


def fit(draw, text, size, max_width):
    while size > 28:
        font = brand_font(size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 6
    return brand_font(size)


def wrap_lines(draw, text, font, max_width):
    """Разбивка текста по ширине: Pillow сам не переносит строки."""
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) > max_width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    return lines


def centred(draw, text, font, cx, y, fill, stroke=0, stroke_fill=None):
    """Строка по центру заданной точки."""
    draw.text((cx - draw.textlength(text, font=font) / 2, y), text, font=font, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill or fill)


def render_card(card, style, has_cat, age, phase, reveal=1.0, back=None):
    """Кадр карточки в теме своего возраста.

    Светлая тема (младшие): картинка слева, крупный текст справа, персонаж в
    правом нижнем углу. Полосы (средние и старшие): жёлтая плашка с картинкой
    сверху, синяя с текстом снизу, персонаж слева.

    Кегль текста в обеих темах крупнее прежнего: слово на экране должно
    читаться с телефона на вытянутой руке, и именно оно, а не фон, главное.
    """
    theme = theme_of(age)
    light = THEME_BY_AGE.get(age) == "light"
    img = background(age, phase, card.get("background") or back).copy()
    draw = ImageDraw.Draw(img)
    kind = card["kind"]

    ink, muted, word_colour, accent = theme["ink"], theme["muted"], theme["word"], theme["accent"]
    text_x = theme["text_x"]
    # Ширина текста ограничена зоной персонажа: раньше длинное слово заезжало
    # прямо на кота, и читалось ни то ни другое.
    text_width = theme["text_w"]
    art_x, art_y = (theme["art_x"], 430) if light else (theme["art_x"], 300)

    if kind in ("title", "outro"):
        title_font = fit(draw, card["title"], int(style["big"] * 0.62), text_width if light else W - 700)
        if light:
            draw.text((text_x, 330), card["title"], font=title_font, fill=ink)
            sub_font = fit(draw, card["sub"], 56, text_width)
            draw.text((text_x, 330 + title_font.size * 1.25), card["sub"], font=sub_font, fill=muted)
            draw.rounded_rectangle([text_x, 330 + title_font.size * 1.25 + sub_font.size + 40,
                                    text_x + 220, 330 + title_font.size * 1.25 + sub_font.size + 54],
                                   radius=7, fill=accent)
        else:
            draw.rounded_rectangle([-60, -60, W + 60, 470], radius=80, fill=theme["panel"])
            centred(draw, card["title"], fit(draw, card["title"], int(style["big"] * 0.5), W - 700),
                    W / 2 + 110, 170, theme["bg"])
            sub_font = fit(draw, card["sub"], 56, W - 800)
            centred(draw, card["sub"], sub_font, W / 2 + 110, 620, muted)
        return img

    if kind in ("letter", "word"):
        symbol = card.get("symbol")
        scale = (2.2 if light else 2.4) * ease_out_back(reveal)
        if light:
            drew = draw_object(img, card["word"], art_x, 500, scale)
            draw = ImageDraw.Draw(img)
            y = 230
            if symbol:
                big = brand_font(int(style["big"] * 0.66), "Bold")
                draw.text((text_x, y), symbol, font=big, fill=ink)
                # Рядом с буквой её название русскими буквами: «эй». Значок
                # /æ/ семилетке ничего не говорит, название говорит.
                if card.get("name"):
                    name_font = brand_font(58, "Medium")
                    draw.text((text_x + draw.textlength(symbol, font=big) + 34, y + big.size * 0.42),
                              card["name"], font=name_font, fill=muted)
                y += big.size * 1.05
                if card.get("sound"):
                    chip = brand_font(42, "Medium")
                    cw = draw.textlength(card["sound"], font=chip)
                    draw.rounded_rectangle([text_x, y, text_x + cw + 48, y + 64], radius=32, fill=theme["bg2"])
                    draw.text((text_x + 24, y + 8), card["sound"], font=chip, fill=muted)
                    y += 88
            word_font = fit(draw, card["word"], int(style["word"] * 1.05), text_width)
            draw.text((text_x, y), card["word"], font=word_font, fill=word_colour)
            y += word_font.size * 1.02
            # Как читается слово русскими буквами. Звук без пары в русском
            # остаётся значком, иначе запись научит ошибке «синк» вместо think.
            if card.get("read"):
                read_font = fit(draw, card["read"], 64, text_width)
                draw.text((text_x, y), card["read"], font=read_font, fill=ink)
                y += read_font.size * 1.05
            tr_font = fit(draw, card["translation"], 58, text_width)
            draw.text((text_x, y), card["translation"], font=tr_font, fill=muted)
            if card.get("example"):
                ex_font = fit(draw, card["example"], 48, text_width)
                draw.text((text_x, y + tr_font.size + 34), card["example"], font=ex_font, fill=muted)
            return img

        draw.rounded_rectangle([-60, -60, W + 60, 560], radius=80, fill=theme["panel"])
        draw_object(img, card["word"], art_x, 250, scale)
        draw = ImageDraw.Draw(img)
        y = 620
        if symbol:
            big = brand_font(int(style["big"] * 0.58), "Bold")
            centred(draw, symbol, big, W / 2 + 110, y, ink)
            y += big.size * 1.05
            if card.get("sound"):
                chip = brand_font(44, "Medium")
                cw = draw.textlength(card["sound"], font=chip)
                draw.rounded_rectangle([W / 2 + 110 - cw / 2 - 26, y, W / 2 + 110 + cw / 2 + 26, y + 64],
                                       radius=32, fill=(30, 44, 96))
                draw.text((W / 2 + 110 - cw / 2, y + 8), card["sound"], font=chip, fill=muted)
                y += 84
        centre_x = W / 2 + 110
        word_font = fit(draw, card["word"], int(style["word"] * 0.95), text_width)
        centred(draw, card["word"], word_font, centre_x, y, word_colour)
        y += word_font.size * 1.05
        tr_font = fit(draw, card["translation"], 58, text_width)
        centred(draw, card["translation"], tr_font, centre_x, y, muted)
        if card.get("example") and y + tr_font.size + 70 < H - 40:
            ex_font = fit(draw, card["example"], 46, text_width)
            centred(draw, card["example"], ex_font, centre_x, y + tr_font.size + 30, muted)
        return img

    if kind == "pair":
        wrong_bg = (255, 233, 233) if light else (48, 26, 44)
        right_bg = (228, 248, 238) if light else (20, 48, 40)
        red, green = (206, 58, 58), (26, 150, 100) if light else (74, 222, 155)
        box_left, box_width = (text_x - 40, text_width + 80) if light else (text_x, W - text_x - 160)
        draw.rounded_rectangle([box_left, 250, box_left + box_width, 500], radius=32, fill=wrong_bg)
        draw.text((box_left + 50, 285), "не так", font=brand_font(38, "Bold"), fill=red)
        wf = fit(draw, card["wrong"], 78, box_width - 110)
        draw.text((box_left + 50, 350), card["wrong"], font=wf, fill=red)
        draw.rounded_rectangle([box_left, 560, box_left + box_width, 810], radius=32, fill=right_bg)
        draw.text((box_left + 50, 595), "верно", font=brand_font(38, "Bold"), fill=green)
        rf = fit(draw, card["right"], 78, box_width - 110)
        draw.text((box_left + 50, 660), card["right"], font=rf, fill=green)
        # Переводится только правильная фраза: перевод неправильной поставил бы
        # её в один ряд с образцом.
        sub = (card.get("sub") or "").strip()
        if sub:
            sub_font = fit(draw, sub, 48, box_width - 110)
            draw.text((box_left + 50, 850), sub, font=sub_font, fill=muted)
        return img

    if kind == "table":
        # Таблица формы: то, чего не хватало в объяснении правила. Ребёнок
        # должен увидеть все четыре строки разом, иначе «откуда взялось does»
        # остаётся без ответа.
        rows = card["rows"][:6]
        # Таблица начинается правее героев: нижние строки иначе уходят им за спину.
        box_left = max(text_x, 560)
        box_width = W - box_left - 120
        note = (card.get("note") or "").strip()
        top = 210
        if note:
            note_font = fit(draw, note, 44, box_width)
            draw.text((box_left, 170), note, font=note_font, fill=muted)
            top = 170 + note_font.size + 34
        columns = max(len(row) for row in rows)
        column_width = box_width / columns
        size = 58 if columns <= 3 else 44
        row_height = min(int((940 - top) / max(len(rows), 1)), 110)
        for index, row in enumerate(rows):
            y = top + index * row_height
            if index == 0:
                draw.rounded_rectangle([box_left - 16, y - 8, box_left + box_width + 16, y + row_height - 12],
                                       radius=14, fill=theme["bg2"] if light else (30, 44, 96))
            for column, cell in enumerate(row[:columns]):
                bold = index == 0 or column == 0
                cell_font = fit(draw, cell, size, column_width - 24)
                colour = ink if bold else word_colour if column > 0 and index > 0 else muted
                draw.text((box_left + column * column_width, y), cell, font=cell_font, fill=colour)
        return img

    if kind == "line":
        # Одна короткая мысль крупно. Кегль подбирается под длину, но снизу
        # ограничен: мелкий текст на экране телефона не читается.
        # На светлой теме герои стоят справа, поэтому фраза занимает левую
        # половину целиком: узкая колонка ломала предложение на три строки.
        box_left = 200 if light else text_x
        box_width = 1060 if light else W - text_x - 160
        note = (card.get("note") or "").strip()
        top = 240
        if note:
            note_font = fit(draw, note, 42, box_width)
            draw.text((box_left, 190), note, font=note_font, fill=muted)
            top = 190 + note_font.size + 46
        # Перевод стоит под английской фразой всегда, когда он есть: ребёнок
        # не должен догадываться о смысле по картинке, иначе он повторяет звук,
        # не понимая слов.
        sub = (card.get("sub") or "").strip()
        limit = 820 if sub else 960
        for size in range(int(style["word"] * 1.1), 44, -4):
            probe = brand_font(size, "Bold")
            lines = wrap_lines(draw, card["text"], probe, box_width)
            if top + len(lines) * (probe.size + 16) <= limit:
                break
        block = len(lines) * (probe.size + 16)
        y = max(top, int((H - block) / 2)) if not sub else max(top, int((H - block) / 2) - 80)
        for line in lines:
            draw.text((box_left, y), line, font=probe, fill=ink)
            y += probe.size + 16
        if sub:
            sub_font = fit(draw, sub, 52, box_width)
            sub_lines = wrap_lines(draw, sub, sub_font, box_width)
            y += 26
            for line in sub_lines:
                draw.text((box_left, y), line, font=sub_font, fill=muted)
                y += sub_font.size + 10
        return img

    return img


# ─────────────────────────────── звук
async def speak(utterance, path, style, senior):
    """Синтез с кэшем по содержанию и паузой в конце фразы.

    Пауза добавляется к каждой фразе, а не только к сцене: без неё реплики
    склеиваются в скороговорку, и ребёнок не успевает повторить. Это честнее
    замедления голоса, от которого речь становится механической.
    """
    voices = VOICE_SENIOR if senior else VOICE
    voice = voices[utterance["lang"]]
    native = utterance["lang"] != "en"
    # Повтор «за мной» произносится чуть медленнее обычного, но не тянуче.
    rate = "-10%" if utterance.get("slow") else (NATIVE_TUNE["rate"] if native else style["rate"])
    pitch = NATIVE_TUNE["pitch"] if native else "+0Hz"
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    raw = f"{path}.raw.mp3"
    # Движок отказывает случайно, когда запросы идут часто: та же фраза через
    # минуту озвучивается с первого раза. Это ограничение частоты, а не
    # проблема текста, поэтому попыток пять и пауза растёт до полуминуты.
    for attempt in range(5):
        try:
            # Ограничение по времени обязательно: движок иногда принимает
            # запрос и замолкает навсегда, и без таймаута сборка встаёт.
            await asyncio.wait_for(
                edge_tts.Communicate(utterance["text"], voice, rate=rate, pitch=pitch).save(raw),
                timeout=45,
            )
            break
        except Exception as error:
            if attempt == 4:
                raise RuntimeError(f"не озвучилось: «{utterance['text'][:60]}» ({error})") from error
            await asyncio.sleep(3 * (attempt + 1))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw,
                    "-af", f"apad=pad_dur={style['gap']}", "-q:a", "4", path], check=True)
    os.remove(raw)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", path],
                         capture_output=True, text=True, check=True)
    return float(json.loads(out.stdout)["format"]["duration"])


def envelope(mp3, frames):
    raw = mp3 + ".wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", "16000", raw], check=True)
    with wave.open(raw) as handle:
        data = handle.readframes(handle.getnframes())
    os.remove(raw)
    samples = memoryview(data).cast("h")
    per = max(int(16000 / FPS), 1)
    levels = []
    for index in range(frames):
        chunk = samples[index * per:(index + 1) * per]
        levels.append(0.0 if not len(chunk) else min(1.0, max(abs(v) for v in chunk) / 32768 * 2.2))
    return levels


async def build(video):
    vid = video["id"]
    style = STYLE[video["age"]]
    senior = video["age"] == "G3"
    folder = os.path.join(WORK, vid)
    os.makedirs(folder, exist_ok=True)

    segments = []
    # Кто говорит в каждом куске сцены: мама объясняет на родном языке, сын
    # произносит английское. Нужно, чтобы рот открывался у того, кто говорит,
    # а не у обоих сразу.
    speakers = []
    for si, scene in enumerate(video["scenes"]):
        parts = []
        voices_here = []
        for ui, utterance in enumerate(scene["say"]):
            # В хеш входят голос, темп и пауза: смена любой из этих настроек
            # обязана дать новый файл, иначе выпуск соберётся из старого звука.
            voice = (VOICE_SENIOR if senior else VOICE)[utterance["lang"]]
            stamp = hashlib.sha1(
                f"{utterance['text']}|{voice}|{utterance.get('slow')}|{style['rate']}|{style['gap']}"
                f"|{NATIVE_TUNE['pitch']}|{NATIVE_TUNE['rate']}".encode()
            ).hexdigest()[:8]
            piece = os.path.join(folder, f"s{si:02d}_{ui}_{stamp}.mp3")
            await speak(utterance, piece, style, senior)
            parts.append(piece)
            voices_here.append(("son" if utterance["lang"] == "en" else "mom", piece))
        # Сцена может держать паузу после речи: ребёнку дают несколько секунд
        # ответить вслух, и в это время кадр стоит. Без явной паузы урок
        # превращается в лекцию, которую слушают, а не в занятие.
        hold = float(scene.get("hold", 0) or 0)
        if hold > 0:
            silence = os.path.join(folder, f"h{si:02d}.mp3")
            if not os.path.exists(silence):
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
                                "-i", "anullsrc=r=24000:cl=mono", "-t", str(hold),
                                "-q:a", "9", silence], check=True)
            parts.append(silence)
            voices_here.append(("none", silence))
        listing = os.path.join(folder, f"l{si:02d}.txt")
        with open(listing, "w", encoding="utf-8") as handle:
            for piece in parts:
                handle.write(f"file '{os.path.basename(piece)}'\n")
        joined = os.path.join(folder, f"seg{si:02d}.mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                        "-i", os.path.basename(listing), "-af", f"apad=pad_dur={style['pause']}",
                        "-q:a", "4", os.path.basename(joined)], cwd=folder, check=True)
        segments.append(joined)
        speakers.append(voices_here)

    # Кадры уходят в ffmpeg потоком, а не ложатся на диск: у минутного
    # выпуска это три тысячи файлов по два мегабайта, и запись занимала
    # больше времени, чем сама отрисовка.
    with open(os.path.join(folder, "audio.txt"), "w", encoding="utf-8") as handle:
        for segment in segments:
            handle.write(f"file '{os.path.basename(segment)}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", "audio.txt", "-c", "copy", "voice.mp3"], cwd=folder, check=True)

    out = os.path.join(OUT, f"{vid}.mp4")
    pipe = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
         "-i", os.path.join(folder, "voice.mp3"),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "veryfast",
         "-c:a", "aac", "-b:a", "160k", "-shortest", out],
        stdin=subprocess.PIPE)

    frame = 0
    for si, (scene, segment) in enumerate(zip(video["scenes"], segments)):
        count = max(int(round(duration(segment) * FPS)), 1)
        levels = envelope(segment, count)
        # Раскладка кадров по говорящему: длительности кусков известны, значит
        # известно, на каких кадрах звучит мама, а на каких сын.
        who = ["none"] * count
        cursor = 0
        for name, piece in speakers[si]:
            length = max(int(round(duration(piece) * FPS)), 1)
            for index in range(cursor, min(cursor + length, count)):
                who[index] = name
            cursor += length
        # Появление занимает полсекунды: эти кадры рисуются каждый, дальше
        # карточка не меняется и переиспользуется.
        reveal_frames = min(int(FPS * 0.5), count)
        settled = None
        for step in range(count):
            phase = frame / FPS
            if step < reveal_frames:
                img = render_card(scene["card"], style, video["cat"], video["age"], phase,
                                  reveal=(step + 1) / reveal_frames, back=video.get("background"))
            else:
                if settled is None:
                    settled = render_card(scene["card"], style, video["cat"], video["age"], phase,
                                          back=video.get("background"))
                img = settled.copy()
            if video["cat"]:
                # Сын подпрыгивает, когда предмет появляется в кадре.
                bounce = 0 if step >= reveal_frames else -26 * (1 - (step + 1) / reveal_frames)
                hero_theme = theme_of(video["age"])
                talking = who[step]
                base = style["hero"] * hero_theme.get("hero_scale", 1.0)
                # Мама крупнее и стоит дальше от текста, сын меньше и ближе к
                # зрителю: он тот, с кем ребёнок себя связывает.
                paste_mascot(img, hero_theme["hero_x"] + hero_theme["mom_dx"], 1060 + bounce,
                             style["hero"] * hero_theme["mom_scale"],
                             pose="sit" if talking != "mom" else scene.get("pose", "sit"),
                             face=scene.get("face", "neutral"),
                             mouth=levels[step] if talking == "mom" else 0.0, phase=phase, who="mom")
                paste_mascot(img, hero_theme["hero_x"], 1060 + bounce, base,
                             pose=scene.get("pose", "sit") if talking == "son" else "sit",
                             face="happy" if talking == "son" else scene.get("face", "neutral"),
                             mouth=levels[step] if talking == "son" else 0.0, phase=phase + 0.7, who="son")
            pipe.stdin.write(img.tobytes())
            frame += 1
        print(f"  {vid}: сцена {si + 1}/{len(video['scenes'])}", flush=True)

    pipe.stdin.close()
    if pipe.wait() != 0:
        raise RuntimeError(f"ffmpeg не собрал {vid}")

    return {"id": vid, "возраст": video["age"], "язык": video["lang"],
            "секунд": round(frame / FPS, 1), "файл": out}


async def voice_only(video):
    """Только озвучка, без кадров.

    Длительность сцены задаёт звук, а не картинка, поэтому голос можно записать
    заранее и потом менять персонажей и фон сколько угодно: тайминг не сдвинется.
    Фразы кэшируются по тексту и голосу, значит настоящая сборка потом пройдёт
    без единого обращения в сеть.
    """
    style = STYLE[video["age"]]
    senior = video["age"] == "G3"
    folder = os.path.join(WORK, video["id"])
    os.makedirs(folder, exist_ok=True)
    jobs = []
    for si, scene in enumerate(video["scenes"]):
        for ui, utterance in enumerate(scene["say"]):
            voice = (VOICE_SENIOR if senior else VOICE)[utterance["lang"]]
            stamp = hashlib.sha1(
                f"{utterance['text']}|{voice}|{utterance.get('slow')}|{style['rate']}|{style['gap']}"
                f"|{NATIVE_TUNE['pitch']}|{NATIVE_TUNE['rate']}".encode()
            ).hexdigest()[:8]
            jobs.append((utterance, os.path.join(folder, f"s{si:02d}_{ui}_{stamp}.mp3")))

    # Синтез идёт по нескольку фраз разом: сеть ждёт дольше, чем считает
    # машина, и последовательный проход тратит часы на ожидание ответа. Больше
    # пяти одновременно движок начинает отбивать запросы.
    gate = asyncio.Semaphore(3)

    async def one(utterance, path):
        async with gate:
            await speak(utterance, path, style, senior)

    await asyncio.gather(*(one(utterance, path) for utterance, path in jobs))
    return {"id": video["id"], "фраз": len(jobs)}


async def main():
    plan = json.load(open(os.path.join(HERE, "plan.json"), encoding="utf-8"))
    wanted = [value for value in sys.argv[1:] if not value.startswith("--")]
    audio_only = "--audio-only" in sys.argv
    if wanted:
        plan = [video for video in plan if video["id"] in wanted]
    # Сборка идёт по одному языку за раз: озвучка трёх языков подряд упирается
    # в ограничение частоты синтеза, да и смотреть их всё равно будут порознь.
    language = next((value.split("=", 1)[1] for value in sys.argv[1:] if value.startswith("--lang=")), None)
    if language:
        plan = [video for video in plan if video["lang"] == language]
    # Доля сборки для облака: десять машин берут каждая свой десяток выпусков.
    # Деление по остатку, а не подряд: длинные уроки правил тогда расходятся по
    # разным машинам и никто не ждёт одну перегруженную.
    shard = next((value.split("=", 1)[1] for value in sys.argv[1:] if value.startswith("--shard=")), None)
    if shard:
        index, total = (int(part) for part in shard.split("/"))
        plan = [video for number, video in enumerate(plan) if number % total == index]
    if audio_only:
        done = 0
        for video in plan:
            result = await voice_only(video)
            done += 1
            print(f"  {done}/{len(plan)} {result['id']}: {result['фраз']} фраз", flush=True)
        print(json.dumps({"озвучено выпусков": done}, ensure_ascii=False))
        return
    results = []
    for video in plan:
        results.append(await build(video))
    print(json.dumps(results, ensure_ascii=False, indent=2))


# Запуск только как скрипт: иначе любой импорт модуля (например, для проверки
# вёрстки одного кадра) запускал бы полный прогон всех роликов.
if __name__ == "__main__":
    asyncio.run(main())

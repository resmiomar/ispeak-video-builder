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
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import edge_tts
from art import draw_object, make_background, ease_out_back, scene_background
from mascot import paste_mascot, has_photo

W, H, FPS = 1920, 1080, 25
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")
OUT = os.path.join(HERE, "out")
# Фирменный шрифт бренда. Лежит в проекте, а не в системе: сборка не должна
# зависеть от того, что установлено на конкретном маке. Montserrat переменный,
# поэтому начертание выбирается по имени, а не отдельным файлом.
FONT = os.path.join(HERE, "assets", "fonts", "Montserrat.ttf")
FALLBACK_FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


# Шрифт: Nunito, круглый и с кириллицей. Montserrat остаётся запасным.
# Круглые формы взяты из образцов дизайна: детский плакат на белом листе
# читается именно за счёт мягких букв, строгая геометрия делает его взрослым.
ROUND_FONT = os.path.join(HERE, "assets", "fonts", "Nunito.ttf")


def brand_font(size, weight="SemiBold"):
    """Шрифт нужного кегля и начертания, с запасным вариантом."""
    # Начертания у Nunito те же по именам, поэтому подмена шрифта не требует
    # правок в разметке кадров.
    for path in (ROUND_FONT, FONT):
        try:
            face = ImageFont.truetype(path, size)
            face.set_variation_by_name(weight)
            return face
        except OSError:
            continue
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



# ─────────────────────────────── оформление
#
# Утверждённый вид: белый лист, картинка в круге слева, буква и слово справа,
# персонажи рядом со словом, а внизу лента со служебными строками.
#
# Лента одна и та же во всех выпусках, и в этом её смысл: ребёнок знает, что
# перевод всегда в правом нижнем углу, и не ищет его глазами заново на каждом
# кадре. Цвет тоже не декоративный: английское синее, перевод зелёный,
# ошибочное красное.
BLUE = (31, 118, 224)
NAVY = (16, 42, 110)
RED = (228, 30, 45)
GREEN = (60, 168, 80)
GREY = (110, 118, 134)
LABEL = (152, 163, 183)
PEACH = (255, 233, 214)
SKY = (223, 238, 255)
BAND_BG = (245, 248, 254)
BAND_LINE = (222, 230, 244)
WHITE_BG = (255, 255, 255)

THEMES = {
    "G1": {"word": 150, "big": 200, "hero": 0.84, "sentence": 128, "band": 78},
    "G2": {"word": 132, "big": 180, "hero": 0.74, "sentence": 116, "band": 70},
    "G3": {"word": 116, "big": 160, "hero": 0.0, "sentence": 104, "band": 64},
}
THEME_BY_AGE = {"G1": "light", "G2": "light", "G3": "light"}

MARGIN = 150            # поля листа
# Позы, при которых герой сидит: молчащий сосед тогда тоже садится, иначе один
# стоит над другим и кадр выглядит случайным.
SIT_POSES = {"sit", "sit-talk", "sit-point", "sit-hand", "sit-think", "sit-cheer", "sit-sad"}

# Поза выбирается по виду кадра, а не по одному правилу на весь выпуск:
# приветствие стоя, правило у доски, слово с показом, разбор ошибки сидя.
POSE_BY_KIND = {"title": "wave", "outro": "thumb", "table": "board",
                "pair": "sit-sad", "line": "sit-talk", "word": "point", "letter": "point"}
# Настроение сцены перебивает вид кадра: вопрос это раздумье, верный ответ радость.
POSE_BY_MOOD = {"think": "sit-think", "cheer": "sit-cheer", "wave": "wave", "talk": "sit-talk"}
BAND_TOP = 800          # верх ленты
CIRCLE = (130, 70, 760, 700)   # круг под картинку
TEXT_X = 900            # левый край текстовой колонки


def theme_of(age):
    return THEMES.get(age, THEMES["G2"])


def hero_theme_has(age):
    """У старших персонажей нет: подростку мультяшные коты мешают."""
    return theme_of(age)["hero"] > 0


# ─────────────────────────────── лист и лента
BACKGROUNDS = os.path.join(HERE, "assets", "backgrounds")
_page_cache: dict[str, Image.Image] = {}
_rooms: dict[str, Image.Image | None] = {}


def background_photo(name):
    """Комната по имени фона. Нет файла - вернётся None, и кадр останется
    белым: новый диалог не должен ронять сборку из-за недостающей картинки."""
    if not name:
        return None
    if name in _rooms:
        return _rooms[name]
    path = os.path.join(BACKGROUNDS, f"{name}.png")
    room = None
    if os.path.exists(path):
        room = Image.open(path).convert("RGB")
        if room.size != (W, H):
            room = room.resize((W, H), Image.LANCZOS)
    _rooms[name] = room
    return room


def blank_page(age, back=None):
    """Лист выпуска: комната на фоне, поверх светлая дымка, снизу лента.

    Дымка обязательна. Без неё тёмный текст ложится на мебель и полки, и кадр
    приходится читать, а не смотреть. С ней комната остаётся узнаваемой, но
    уходит на второй план, как и должна.
    """
    key = f"{age}:{back or ''}"
    ready = _page_cache.get(key)
    if ready is not None:
        return ready
    img = Image.new("RGB", (W, H), WHITE_BG)
    room = background_photo(back)
    if room is not None:
        img = Image.blend(room, Image.new("RGB", (W, H), WHITE_BG), 0.62)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, BAND_TOP, W, H], fill=BAND_BG)
    draw.line([0, BAND_TOP, W, BAND_TOP], fill=(226, 234, 248), width=3)
    _page_cache[key] = img
    return img


def draw_band(draw, age, columns):
    """Служебная строка внизу: ярлык мелким серым, значение крупным цветным.

    Пустых колонок не бывает: если читать нечего, колонка просто не рисуется,
    и оставшиеся занимают всю ширину. Иначе лента выглядела бы поломанной.
    """
    columns = [item for item in columns if item and item[1]]
    if not columns:
        return
    size = theme_of(age)["band"]
    step = (W - 2 * MARGIN) / len(columns)
    for index, (label, value, colour) in enumerate(columns):
        x = MARGIN + index * step
        draw.text((x, BAND_TOP + 40), label, font=brand_font(28, "ExtraBold"), fill=LABEL)
        value_font = fit(draw, value, size, step - 90)
        draw.text((x, BAND_TOP + 88), value, font=value_font, fill=colour)
        if index:
            draw.line([x - 55, BAND_TOP + 40, x - 55, H - 55], fill=BAND_LINE, width=3)


def fit(draw, text, size, max_width, weight="ExtraBold"):
    # Начертание по умолчанию жирное: в образце дизайна текст плотный, тонкие
    # буквы на белом листе теряются.
    while size > 28:
        font = brand_font(size, weight)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 6
    return brand_font(size, weight)


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


AGE_LABEL = {"G1": "7-9 лет", "G2": "10-13 лет", "G3": "14-17 лет"}


def mark(draw, age):
    """Марка продукта и возраст в углу кадра.

    Ролик расходится по чужим лентам и должен называть себя сам: без подписи
    он ничей. Возраст стоит рядом, потому что первый вопрос родителя не «что
    это», а «моему ли ребёнку это показывать».
    """
    draw.text((MARGIN, 50), "iSpeak", font=brand_font(42, "ExtraBold"), fill=BLUE)
    label = AGE_LABEL.get(age, "")
    if not label:
        return
    font = brand_font(30, "ExtraBold")
    width = draw.textlength(label, font=font)
    draw.rounded_rectangle([MARGIN + 160, 50, MARGIN + 200 + width, 96], radius=23, fill=SKY)
    draw.text((MARGIN + 180, 57), label, font=font, fill=NAVY)


def render_card(card, style, has_cat, age, phase, reveal=1.0, back=None, progress=None, head=None):
    """Кадр утверждённого вида.

    Верх кадра держит главное: картинку, букву, слово или предложение. Низ
    держит служебное: как читается, что значит. Разделение постоянное, поэтому
    ребёнок каждый раз знает, куда смотреть, и не перечитывает кадр целиком.
    """
    theme = theme_of(age)
    img = blank_page(age, card.get("background") or back).copy()
    draw = ImageDraw.Draw(img)
    kind = card["kind"]
    right = W - MARGIN
    # Правый край текста: там, где начинаются персонажи.
    text_right = (1380 if hero_theme_has(age) else right)

    if kind in ("title", "outro"):
        # Ширина названия ограничена зоной героев: «Буквы A, B, C, D, E»
        # раньше уезжало прямо на маму и обрывалось.
        title_w = text_right - MARGIN - 90
        title_font = fit(draw, card["title"], theme["big"] + 40, title_w)
        lines_ = wrap_lines(draw, card["title"], title_font, title_w)
        block = len(lines_) * (title_font.size + 22)
        y = (BAND_TOP - block) / 2
        for line in lines_:
            centred(draw, line, title_font, MARGIN + title_w / 2, y, NAVY)
            y += title_font.size + 22
        if card.get("sub"):
            centred(draw, card["sub"], brand_font(theme["band"], "ExtraBold"),
                    MARGIN + title_w / 2, BAND_TOP + 88, BLUE)
        mark(draw, age)
        return img

    mark(draw, age)

    if kind in ("letter", "word"):
        scale = 2.2 * ease_out_back(reveal)
        cx = (CIRCLE[0] + CIRCLE[2]) / 2
        cy = (CIRCLE[1] + CIRCLE[3]) / 2
        draw.ellipse(CIRCLE, fill=PEACH)
        drew = draw_object(img, card["word"], cx, cy, scale)
        draw = ImageDraw.Draw(img)
        if not drew:
            # Картинки нет: в круге стоит первая буква слова, а не пустота.
            centred(draw, card["word"][:1].upper(), brand_font(280, "ExtraBold"), cx, cy - 160, (255, 214, 184))

        width = text_right - TEXT_X
        if card.get("symbol"):
            symbol_font = fit(draw, card["symbol"], theme["big"], width)
            draw.text((TEXT_X, 130), card["symbol"], font=symbol_font, fill=BLUE)
            word_font = fit(draw, card["word"], theme["word"], width)
            draw.text((TEXT_X, 420), card["word"], font=word_font, fill=NAVY)
        else:
            word_font = fit(draw, card["word"], theme["word"] + 40, width)
            draw.text((TEXT_X, 250), card["word"], font=word_font, fill=NAVY)
            if card.get("example"):
                ex_font = fit(draw, card["example"], 54, width)
                draw.text((TEXT_X, 470), card["example"], font=ex_font, fill=GREY)

        draw_band(draw, age, [
            ("БУКВА", card.get("name", ""), BLUE),
            ("СЛОВО", card["word"], NAVY),
            ("ЧИТАЕТСЯ", card.get("read", ""), GREY),
            ("ПЕРЕВОД", card.get("translation", ""), GREEN),
        ])
        return img

    if kind == "pair":
        width = text_right - MARGIN
        block_h = 200
        y = 150
        draw.rounded_rectangle([MARGIN, y, MARGIN + width, y + block_h], radius=34, fill=(255, 238, 238))
        draw.text((MARGIN + 44, y + 26), "не так", font=brand_font(36, "ExtraBold"), fill=RED)
        wf = fit(draw, card["wrong"], 80, width - 100)
        draw.text((MARGIN + 44, y + 80), card["wrong"], font=wf, fill=RED)
        y += block_h + 60
        draw.rounded_rectangle([MARGIN, y, MARGIN + width, y + block_h], radius=34, fill=(232, 250, 236))
        draw.text((MARGIN + 44, y + 26), "верно", font=brand_font(36, "ExtraBold"), fill=GREEN)
        rf = fit(draw, card["right"], 80, width - 100)
        draw.text((MARGIN + 44, y + 80), card["right"], font=rf, fill=GREEN)
        draw_band(draw, age, [("ПЕРЕВОД", card.get("sub", ""), GREEN)])
        return img

    if kind == "table":
        rows = card["rows"][:6]
        columns = max(len(row) for row in rows)
        note = (card.get("note") or head or "").strip()
        top = 60
        if note:
            note_font = fit(draw, note, 54, W - 2 * MARGIN)
            centred(draw, note, note_font, W / 2, top, NAVY)
            top += note_font.size + 34
        table_w = text_right - MARGIN
        column_w = table_w / columns
        head_h = 92
        row_h = min(int((BAND_TOP - top - 60 - head_h) / max(len(rows) - 1, 1)), 112)
        size = min((fit(draw, cell, 52, column_w - 60).size for row in rows for cell in row if cell), default=52)
        total_h = head_h + row_h * (len(rows) - 1)
        draw.rounded_rectangle([MARGIN, top, MARGIN + table_w, top + total_h], radius=26,
                               fill=WHITE_BG, outline=BLUE, width=5)
        draw.rounded_rectangle([MARGIN, top, MARGIN + table_w, top + head_h + 26], radius=26, fill=BLUE)
        draw.rectangle([MARGIN, top + head_h - 6, MARGIN + table_w, top + head_h], fill=BLUE)
        for index, row in enumerate(rows):
            y = top + (0 if index == 0 else head_h + (index - 1) * row_h)
            height = head_h if index == 0 else row_h
            if index > 1:
                draw.line([MARGIN + 6, y, MARGIN + table_w - 6, y], fill=BLUE, width=3)
            for column, cell in enumerate(row[:columns]):
                if not cell:
                    continue
                colour = WHITE_BG if index == 0 else (NAVY if column == 0 else BLUE)
                font = brand_font(size, "ExtraBold")
                if index == 0:
                    centred(draw, cell, font, MARGIN + column_w * (column + 0.5), y + (height - size) / 2, colour)
                else:
                    draw.text((MARGIN + column * column_w + 40, y + (height - size) / 2), cell, font=font, fill=colour)
        for column in range(1, columns):
            x = MARGIN + column * column_w
            draw.line([x, top + 6, x, top + total_h - 6], fill=BLUE, width=3)
        return img

    if kind == "line":
        sub = (card.get("sub") or "").strip()
        note = (card.get("note") or "").strip()
        width = text_right - MARGIN
        y = 150
        if note and note != card["text"]:
            note_font = fit(draw, note, 46, width)
            draw.text((MARGIN, y), note, font=note_font, fill=LABEL)
            y += note_font.size + 34
        for size in range(theme["sentence"], 40, -4):
            probe = brand_font(size, "ExtraBold")
            lines_ = wrap_lines(draw, card["text"], probe, width)
            if y + len(lines_) * (probe.size + 18) <= BAND_TOP - 60:
                break
        for line in lines_:
            draw.text((MARGIN, y), line, font=probe, fill=NAVY)
            y += probe.size + 18
        draw_band(draw, age, [("ПЕРЕВОД", sub, GREEN)])
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
            # Полоса прогресса считает сцены: ребёнок видит, сколько осталось.
            progress = (si + 1, len(video["scenes"]))
            if step < reveal_frames:
                img = render_card(scene["card"], style, video["cat"], video["age"], phase,
                                  reveal=(step + 1) / reveal_frames, back=video.get("background"),
                                  progress=progress, head=video.get("title"))
            else:
                if settled is None:
                    settled = render_card(scene["card"], style, video["cat"], video["age"], phase,
                                          back=video.get("background"), progress=progress,
                                          head=video.get("title"))
                img = settled.copy()
            if video["cat"] and hero_theme_has(video["age"]):
                # Сын подпрыгивает, когда предмет появляется в кадре.
                bounce = 0 if step >= reveal_frames else -26 * (1 - (step + 1) / reveal_frames)
                hero_theme = theme_of(video["age"])
                talking = who[step]
                # Пока прислан один персонаж, в кадре стоит он один и крупнее:
                # смешивать живого героя с нарисованным запасным нельзя, это
                # видно сразу.
                alone = has_photo("son") and not has_photo("mom")
                if alone:
                    paste_mascot(img, 1660, BAND_TOP + 10 + bounce, hero_theme["hero"] * 1.5,
                                 pose=scene.get("pose", "sit"),
                                 face="happy" if talking == "son" else scene.get("face", "neutral"),
                                 mouth=levels[step] if talking != "none" else 0.0,
                                 phase=phase, who="son")
                else:
                    # Поза берётся из сцены: приветствие стоя, показ у доски
                    # стоя, объяснение и повтор сидя. Урок, где герои весь час
                    # сидят, скучнее самого материала.
                    wanted = POSE_BY_MOOD.get(scene.get("pose", ""),
                                              POSE_BY_KIND.get(scene["card"]["kind"], "sit-talk"))
                    mom_pose = wanted if talking == "mom" else ("sit" if wanted in SIT_POSES else "listen")
                    son_pose = wanted if talking == "son" else ("sit" if wanted in SIT_POSES else "listen")
                    paste_mascot(img, 1500, BAND_TOP + 14 + bounce, hero_theme["hero"] * 1.5,
                                 pose=mom_pose, face=scene.get("face", "neutral"),
                                 mouth=levels[step] if talking == "mom" else 0.0, phase=phase, who="mom")
                    paste_mascot(img, 1770, BAND_TOP + 14 + bounce, hero_theme["hero"] * 1.02,
                                 pose=son_pose,
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

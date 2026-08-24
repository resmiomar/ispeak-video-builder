#!/usr/bin/env python3
"""
Картинки к словам из открытого набора Noto Emoji.

Зачем. Рисовать кодом каждый из 671 предмета невозможно: на это ушли бы
недели, и стиль всё равно разъехался бы. Noto Emoji это открытый набор
Google под лицензией Apache 2.0: тысячи предметов, один стиль, прозрачный
фон, разрешено использовать в коммерческом продукте с указанием источника
(см. NOTICES.md).

Файл кладётся как assets/objects/<английское слово>.png, а конвейер уже
умеет предпочитать файл своему рисунку. Значит подмена не требует правок в
коде и любую картинку потом можно заменить на свою.

Что НЕ берём из набора:
  - цвета: у emoji нет серого и розового кружка, ряд получился бы неполным;
  - числа: 5️⃣ это цифра, а ребёнку на этой ступени нужны пять кружков,
    иначе он учит начертание, а не количество.

    python scripts/video/fetch-art.py          # докачать недостающее
    python scripts/video/fetch-art.py --force  # перекачать всё
"""
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "objects")
SOURCE = "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/png/512/emoji_u{code}.png"

# Слово курса → код картинки в наборе. Код взят по смыслу, а не по созвучию:
# «bank» это здание банка, а не берег реки.
EMOJI = {
    # люди и семья
    "man": "1f468", "woman": "1f469", "boy": "1f466", "girl": "1f467", "child": "1f9d2",
    "children": "1f46b", "kid": "1f9d2", "baby": "1f476", "people": "1f465", "person": "1f9d1",
    "friend": "1f46d", "family": "1f46a", "mother": "1f469", "father": "1f468",
    "mom": "1f469", "dad": "1f468", "parents": "1f46a", "brother": "1f466", "sister": "1f467",
    "son": "1f466", "daughter": "1f467", "grandmother": "1f475", "grandfather": "1f474",
    "husband": "1f935", "wife": "1f470", "teacher": "1f469_200d_1f3eb", "student": "1f9d1_200d_1f393",
    "doctor": "1f469_200d_2695", "nurse": "1f469_200d_2695", "driver": "1f699", "worker": "1f477",
    "boss": "1f9d1_200d_1f4bc", "neighbour": "1f3e1", "guest": "1f44b", "stranger": "1f6b6",
    "guy": "1f468", "name": "1f4dd", "age": "1f382",

    # дом и вещи
    "house": "1f3e0", "home": "1f3e1", "room": "1f6cb", "kitchen": "1f373", "bathroom": "1f6c1",
    "bedroom": "1f6cf", "door": "1f6aa", "window": "1fa9f", "wall": "1f9f1", "floor": "1f9f9",
    "table": "1f9fe", "chair": "1fa91", "bed": "1f6cf", "sofa": "1f6cb", "light": "1f4a1",
    "key": "1f511", "phone": "1f4f1", "computer": "1f5a5", "laptop": "1f4bb", "tv": "1f4fa",
    "camera": "1f4f7", "car": "1f697", "bus": "1f68c", "train": "1f686", "plane": "2708",
    "bike": "1f6b2", "bag": "1f45c", "box": "1f4e6", "book": "1f4d5", "paper": "1f4c4",
    "pen": "1f58a", "pencil": "270f", "money": "1f4b5", "card": "1f4b3", "ticket": "1f3ab",
    "clothes": "1f455", "shirt": "1f455", "shoes": "1f45f", "jacket": "1f9e5", "watch": "231a",
    "glasses": "1f453", "fridge": "1f9ca", "lamp": "1f4a1", "clock": "1f550", "mirror": "1fa9e",

    # еда
    "food": "1f37d", "water": "1f4a7", "tea": "1f375", "coffee": "2615", "bread": "1f35e",
    "milk": "1f95b", "egg": "1f95a", "meat": "1f356", "fish": "1f41f", "rice": "1f35a",
    "fruit": "1f34e", "apple": "1f34e", "vegetable": "1f955", "sugar": "1f36c", "salt": "1f9c2",
    "plate": "1f37d", "cup": "1f375", "knife": "1f52a", "fork": "1f374", "spoon": "1f944",
    "soup": "1f372", "cake": "1f370", "orange": "1f34a", "banana": "1f34c", "juice": "1f9c3",
    "dinner": "1f37d", "breakfast": "1f373", "lunch": "1f371",

    # школа и работа
    "school": "1f3eb", "lesson": "1f4d6", "class": "1f9d1_200d_1f3eb", "homework": "1f4dd",
    "test": "1f4dd", "exam": "1f4dd", "mark": "1f4af", "grade": "1f4ca", "subject": "1f4da",
    "notebook": "1f4d3", "question": "2753", "answer": "1f4ac", "mistake": "274c",
    "example": "1f4cc", "rule": "1f4cf", "word": "1f524", "sentence": "1f4c3", "story": "1f4d6",
    "page": "1f4c4", "project": "1f4c1", "job": "1f4bc", "work": "1f4bc", "company": "1f3e2",
    "meeting": "1f91d", "plan": "1f5d3", "idea": "1f4a1", "problem": "26a0", "solution": "2705",
    "result": "1f4ca", "reason": "1f914", "way": "1f6e3", "level": "1f4c8", "skill": "1f6e0",
    "practice": "1f501", "break": "23f8", "ruler": "1f4cf", "rubber": "1f9fd",
    "sharpener": "1f4d0", "glue": "1f9f4", "scissors": "2702", "board": "1f4cb", "desk": "1fa91",
    "chalk": "1f58d", "schoolbag": "1f392", "backpack": "1f392", "timetable": "1f5d3",
    "playground": "1f3de", "uniform": "1f45a", "pencil case": "1f4d0",

    # тело и здоровье
    "head": "1f9d1", "face": "1f642", "eye": "1f441", "ear": "1f442", "nose": "1f443",
    "mouth": "1f444", "tooth": "1f9b7", "hair": "1f9d1_200d_1f9b0", "hand": "270b",
    "arm": "1f4aa", "leg": "1f9b5", "foot": "1f9b6", "back": "1f9d1", "heart": "2764",
    "stomach": "1f9d1", "health": "1f34f", "medicine": "1f48a", "pain": "1f915", "cold": "1f912",
    "fever": "1f321", "tired": "1f629", "hungry": "1f924", "thirsty": "1f4a7", "sleepy": "1f634",
    "happy": "1f603", "sad": "1f622", "angry": "1f621", "afraid": "1f628", "scared": "1f631",
    "worried": "1f61f", "nervous": "1f630", "excited": "1f929", "bored": "1f971",
    "surprised": "1f632", "glad": "1f60a", "sorry": "1f647", "fine": "1f44c", "sick": "1f912",

    # животные и природа
    "animal": "1f43e", "bird": "1f426", "horse": "1f434", "cow": "1f42e", "sheep": "1f411",
    "goat": "1f410", "chicken": "1f414", "mouse": "1f42d", "rabbit": "1f430", "bear": "1f43b",
    "wolf": "1f43a", "fox": "1f98a", "lion": "1f981", "elephant": "1f418", "monkey": "1f412",
    "snake": "1f40d", "frog": "1f438", "cat": "1f431", "dog": "1f436", "insect": "1f41e",
    "tree": "1f333", "flower": "1f337", "grass": "1f33f", "sun": "2600", "moon": "1f319",
    "star": "2b50", "sky": "1f324", "cloud": "2601", "rain": "1f327", "snow": "2744",
    "wind": "1f4a8", "river": "1f30a", "sea": "1f30a", "lake": "1f3de", "mountain": "26f0",
    "forest": "1f332", "beach": "1f3d6", "garden": "1f33b", "world": "1f30d", "nature": "1f33f",

    # места
    "city": "1f3d9", "town": "1f3d8", "village": "1f3e1", "country": "1f5fa", "street": "1f6e3",
    "road": "1f6e3", "place": "1f4cd", "university": "1f393", "office": "1f3e2", "shop": "1f6cd",
    "store": "1f3ec", "market": "1f6d2", "restaurant": "1f37d", "cafe": "2615", "hotel": "1f3e8",
    "hospital": "1f3e5", "bank": "1f3e6", "station": "1f689", "airport": "1f6eb", "park": "1f333",
    "building": "1f3e2", "abroad": "2708", "border": "1f6c2", "center": "1f3af",

    # действия
    "run": "1f3c3", "walk": "1f6b6", "jump": "1f938", "swim": "1f3ca", "read": "1f4d6",
    "write": "270d", "draw": "1f3a8", "sing": "1f3a4", "dance": "1f483", "play": "26bd",
    "sleep": "1f634", "eat": "1f374", "drink": "1f379", "close": "1f512", "help": "1f91d",
    "wash": "1f9fc", "cook": "1f373", "look": "1f440", "listen": "1f442", "speak": "1f5e3",
    "buy": "1f6d2", "pay": "1f4b3", "call": "1f4de", "wait": "23f3", "start": "25b6",
    "finish": "1f3c1", "win": "1f3c6", "lose": "1f4c9", "travel": "1f9f3", "study": "1f4da",
    "think": "1f914", "smile": "1f60a", "cry": "1f622", "give": "1f381", "take": "1f91a",

    # время
    "time": "23f0", "day": "2600", "week": "1f4c5", "month": "1f5d3", "year": "1f4c6",
    "hour": "1f552", "minute": "23f1", "second": "23f1", "morning": "1f305", "afternoon": "1f31e",
    "evening": "1f306", "night": "1f303", "today": "1f4c5", "tomorrow": "27a1", "yesterday": "2b05",
    "weekend": "1f3d6", "birthday": "1f382", "holiday": "1f3d6", "spring": "1f338",
    "summer": "1f3d6", "autumn": "1f342", "winter": "2744", "season": "1f341", "weather": "1f324",

    # спорт, техника, деньги, общество
    "football": "26bd", "sport": "1f3c5", "team": "1f465", "match": "1f3df", "score": "1f522",
    "coach": "1f3c5", "training": "1f3cb", "exercise": "1f938", "energy": "26a1", "rest": "1f6cc",
    "device": "1f4f1", "screen": "1f5a5", "app": "1f4f2", "download": "2b07", "password": "1f511",
    "account": "1f464", "network": "1f310", "browser": "1f310", "battery": "1f50b",
    "software": "1f4bd", "link": "1f517", "profile": "1f464", "robot": "1f916",
    "science": "1f52c", "experiment": "1f9ea", "theory": "1f4d0", "discovery": "1f50e",
    "invention": "1f4a1", "data": "1f4ca", "salary": "1f4b0", "income": "1f4b9",
    "price": "1f3f7", "bill": "1f9fe", "receipt": "1f9fe", "discount": "1f3f7",
    "interview": "1f4bc", "contract": "1f4dc", "law": "2696", "government": "1f3db",
    "election": "1f5f3", "vote": "1f5f3", "citizen": "1f9d1", "volunteer": "1f64b",
    "charity": "1f49d", "crime": "1f6a8", "court": "2696", "journalist": "1f4f0",
    "opinion": "1f4ac", "protest": "1f4e2", "freedom": "1f54a", "justice": "2696",
    "environment": "1f30f", "pollution": "1f3ed", "waste": "1f5d1", "recycle": "267b",
    "plastic": "1f9f4", "climate": "1f321", "flood": "1f30a", "drought": "1f3dc",
    "passport": "1f6c2", "visa": "1f4b3", "luggage": "1f9f3", "flight": "2708",
    "journey": "1f9ed", "trip": "1f9f3", "guide": "1f5fa", "souvenir": "1f381",
    "tourist": "1f4f8", "map": "1f5fa", "seat": "1f4ba", "gate": "1f6aa",
}


def main():
    os.makedirs(OUT, exist_ok=True)
    force = "--force" in sys.argv
    got, skipped, failed = 0, 0, []
    for word, code in EMOJI.items():
        path = os.path.join(OUT, f"{word.replace(' ', '-')}.png")
        if os.path.exists(path) and not force:
            skipped += 1
            continue
        try:
            with urllib.request.urlopen(SOURCE.format(code=code), timeout=30) as answer:
                data = answer.read()
            with open(path, "wb") as file:
                file.write(data)
            got += 1
        except Exception as error:
            failed.append(f"{word} ({code}): {error}")
        # Пауза, чтобы не долбить чужой сервер сотней запросов в секунду.
        time.sleep(0.05)
    print(f"скачано: {got}, уже было: {skipped}, не вышло: {len(failed)}")
    for line in failed[:20]:
        print("  ", line)


if __name__ == "__main__":
    main()

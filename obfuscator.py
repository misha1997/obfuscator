"""
Модуль обфускации текста для TikTok
"""

import random
import re

ZWSP = "\u200B"
ZWNJ = "\u200C"

DIACRITICS = ["́", "̂", "̃", "̄", "̆", "̇", "̈"]

LETTER_REPLACEMENTS = {
    "а": ["а", "α", "a"], "е": ["е", "є", "ё", "e", "ε"],
    "о": ["о", "ο", "o", "օ"], "с": ["с", "ϲ", "c", "ꜱ"],
    "р": ["р", "p", "ρ"], "к": ["к", "k", "κ"],
    "и": ["и", "і", "i"], "у": ["у", "y", "υ"],
    "х": ["х", "x", "χ"], "б": ["б", "b", "ь"],
}

# Список корней, которые часто вызывают бан (можно расширять)
# Максимально расширенный список триггерных корней
TRIGGER_ROOTS = [
    # === Основной мат ===
    "еб", "е6", "ебл", "ебал", "ебан", "ебат", "еба", "ёб", "йоб",
    "бля", "бляд", "блят", "блять", "блядина",
    "пизд", "пиз", "пезд", "пёзд",
    "хуй", "хyй", "хую", "хуе", "хул", "хер",
    "муд", "мyд", "мудо", "муде",
    "залуп", "залупа",
    "сук", "сука", "суки", "сукa",
    "шлю", "шлюх", "шлюшка",
    "твар", "тварь",
    "говн", "гавн",
    "нах", "нахуй", "нахyй", "на хуй",
    "пошел", "пошёл", "пошелна", "пошел в",

    # === Дополнительные варианты ===
    "кацап", "москал", "москaл", "мocкал",
    "баная", "баный", "банaя",
    "иди", "идинах", "иди на",
    "завал", "завали",
    "отъеб", "отъеби", "отъебис",
    "заеб", "заеби", "заебал", "заёб",
    "выеб", "выеби", "выёб",
    "приеб", "приеби",
    "доеб", "доеби",
    "уеб", "уёб", "уеби",
    "поех", "поехал", "поеб",

    # === Более редкие, но часто фильтруемые ===
    "жоп", "жопа", "жопa",
    "пидор", "пидора", "пидр", "педик",
    "гандон", "гондон",
    "елд", "хер", "хрен", "член",
    "сперм", "конча", "кончил",
    "трах", "траха", "трахал",
    "fuck", "fck", "fuk", "shit", "bitch", "asshole",

    # === Политические / национальные (часто фильтруются) ===
    "укр", "укроп", "хохол", "хохл", "свино",
    "рашка", "раш", "ватн", "ватник",
    "орк", "орки", "москали", "кацапы",
]

# Убираем дубли и сортируем для удобства
TRIGGER_ROOTS = sorted(list(set(TRIGGER_ROOTS)))

VALID_MODES = ("tiktok", "strange", "max")


def generate_obfuscated_variants(word: str) -> list:
    variants = []
    lower = word.lower()
    
    v1 = "".join(random.choice(LETTER_REPLACEMENTS.get(c, [c])) for c in lower)
    variants.append(v1)
    
    v2 = lower.replace("е", "e").replace("а", "a").replace("о", "o") \
             .replace("б", "6").replace("и", "i").replace("у", "y")
    variants.append(v2)
    
    v3 = "".join(random.choice(LETTER_REPLACEMENTS.get(c, [c])) if random.random() > 0.4 else c for c in lower)
    variants.append(v3)
    
    return list(set(variants))


def obfuscate(text: str, mode: str = "tiktok", intensity: int = 75) -> str:
    """Основная функция обфускации"""
    if not text:
        return ""

    if mode not in VALID_MODES:
        mode = "tiktok"
    
    intensity = max(0, min(100, intensity)) / 100.0
    result = text

    # Обработка триггерных корней
    for root in TRIGGER_ROOTS:
        pattern = re.compile(re.escape(root), re.IGNORECASE)
        result = pattern.sub(lambda m: random.choice(generate_obfuscated_variants(m.group(0))), result)

    # Посимвольная обфускация
    chars = []
    for char in result:
        if random.random() > intensity:
            chars.append(char)
            continue

        lower = char.lower()
        new_char = random.choice(LETTER_REPLACEMENTS.get(lower, [lower]))

        if mode == "tiktok":
            if random.random() > 0.58: new_char += random.choice(DIACRITICS)
            if random.random() > 0.72: new_char += ZWSP
        elif mode == "strange":
            if random.random() > 0.35: new_char += "".join(random.choices(DIACRITICS, k=random.randint(1, 2)))
            if random.random() > 0.5: new_char += ZWSP
        elif mode == "max":
            new_char += "".join(random.choices(DIACRITICS, k=random.randint(1, 3)))
            if random.random() > 0.4: new_char += ZWSP
            if random.random() > 0.65: new_char += ZWNJ

        if char.isupper() and new_char:
            new_char = new_char[0].upper() + new_char[1:]

        chars.append(new_char)

    final = "".join(chars)

    if mode in ("strange", "max"):
        final = re.sub(r'(\w{4,})', lambda m: m.group(1)[:3] + ZWSP + m.group(1)[3:], final)

    return final
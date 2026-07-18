import random
import re

ZWSP = "\u200B"
ZWNJ = "\u200C"

DIACRITICS = ["́", "̂", "̃", "̄", "̆", "̇", "̈"]

# Базовые замены букв
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

def generate_obfuscated_variants(word: str) -> list:
    """Автоматически генерирует несколько вариантов обфускации слова"""
    variants = []
    lower = word.lower()
    
    # Вариант 1: замена букв
    variant1 = ""
    for char in lower:
        if char in LETTER_REPLACEMENTS:
            variant1 += random.choice(LETTER_REPLACEMENTS[char])
        else:
            variant1 += char
    variants.append(variant1)
    
    # Вариант 2: латиница + цифры
    variant2 = lower.replace("е", "e").replace("а", "a").replace("о", "o")
    variant2 = variant2.replace("б", "6").replace("и", "i")
    variants.append(variant2)
    
    # Вариант 3: смешанный
    variant3 = ""
    for char in lower:
        if random.random() > 0.5 and char in LETTER_REPLACEMENTS:
            variant3 += random.choice(LETTER_REPLACEMENTS[char])
        else:
            variant3 += char
    variants.append(variant3)
    
    return list(set(variants))  # убираем дубли


def obfuscate_universal(text: str, mode: str = "tiktok", intensity: float = 0.78) -> str:
    """
    Универсальная обфускация с автоматической обработкой чувствительных слов.
    """
    if not text:
        return text

    result = text

    # === Этап 1: Обработка чувствительных корней ===
    for root in TRIGGER_ROOTS:
        # Ищем корень (регистронезависимо)
        pattern = re.compile(re.escape(root), re.IGNORECASE)
        
        def replace_root(match):
            original = match.group(0)
            variants = generate_obfuscated_variants(original)
            return random.choice(variants)
        
        result = pattern.sub(replace_root, result)

    # === Этап 2: Посимвольная обфускация ===
    chars = []
    for char in result:
        if random.random() > intensity:
            chars.append(char)
            continue

        lower = char.lower()
        new_char = random.choice(LETTER_REPLACEMENTS.get(lower, [lower]))

        # Режимы
        if mode == "tiktok":
            if random.random() > 0.6: 
                new_char = new_char + random.choice(DIACRITICS)
            if random.random() > 0.75: 
                new_char += ZWSP

        elif mode == "strange":
            if random.random() > 0.4:
                new_char = new_char + "".join(random.choices(DIACRITICS, k=random.randint(1,2)))
            if random.random() > 0.55: 
                new_char += ZWSP

        elif mode == "max":
            new_char = new_char + "".join(random.choices(DIACRITICS, k=random.randint(1,3)))
            if random.random() > 0.4: 
                new_char += ZWSP
            if random.random() > 0.7: 
                new_char += ZWNJ

        if char.isupper() and new_char:
            new_char = new_char[0].upper() + new_char[1:]

        chars.append(new_char)

    final = "".join(chars)

    # Разбиваем длинные слова
    if mode in ("strange", "max"):
        final = re.sub(r'(\w{4,})', lambda m: m.group(1)[:2] + ZWSP + m.group(1)[2:], final)

    return final


# ===================== ТЕСТ =====================
if __name__ == "__main__":
    test = "Завали ебало кацапня ебаная. Иди стой в очереди за бенз, сука!"
    
    print("TikTok Safe:")
    print(obfuscate_universal(test, "tiktok", 0.78))
    print("\nStrange:")
    print(obfuscate_universal(test, "strange", 0.78))
    print("\nMax:")
    print(obfuscate_universal(test, "max", 0.85))
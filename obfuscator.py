"""Логика обфускации текста — порт из index.html.

Гомоглифы (латиница -> кириллица-двойники) + zero-width space + диакритики.
Доступные режимы: "tiktok", "strange", "max".
"""

import random
import re

# Невидимые символы задаём через escape, чтобы не зависеть от кодировки файла.
ZWSP = "​"  # zero-width space
DIACRITICS = [
    "́",  # combining acute
    "̂",  # combining circumflex
    "̃",  # combining tilde
    "̄",  # combining macron
    "̆",  # combining breve
    "̇",  # combining dot above
    "̈",  # combining diaeresis
]

# Латиница -> кириллица-гомоглиф. Кириллические буквы-двойники отображаются на себя
# (чтобы к ним тоже можно было приклеить диакритику).
REPLACEMENTS = {
    "а": "а",  # а -> а
    "е": "е",  # е -> е
    "о": "о",  # о -> о
    "с": "с",  # с -> с
    "р": "р",  # р -> р
    "к": "к",  # к -> к
    "x": "х",       # x -> х
    "y": "у",       # y -> у
    "p": "р",       # p -> р
    "c": "с",       # c -> с
    "o": "о",       # o -> о
    "a": "а",       # a -> а
}

VALID_MODES = ("tiktok", "strange", "max")


def _add_diacritic(char: str) -> str:
    return char + random.choice(DIACRITICS)


def obfuscate(text: str, mode: str = "tiktok", intensity: int = 75) -> str:
    """Преобразует текст. intensity — 0..100, режим — один из VALID_MODES."""
    if not text:
        return ""

    if mode not in VALID_MODES:
        mode = "tiktok"
    intensity = max(0, min(100, intensity)) / 100

    result_chars = []

    for char in text:
        if random.random() > intensity:
            result_chars.append(char)
            continue

        new_char = char.lower()
        if new_char in REPLACEMENTS:
            new_char = REPLACEMENTS[new_char]

        if mode in ("tiktok", "max"):
            if random.random() > 0.5:
                new_char = _add_diacritic(new_char)
            if random.random() > 0.65:
                new_char += ZWSP

        if mode == "max":
            if random.random() > 0.75:
                new_char = _add_diacritic(new_char)

        # Восстанавливаем регистр, только если оригинал был ВЕРХНИМ и результат
        # ровно один символ (без прицепленных диакритик/zwsp).
        if char == char.upper() and len(new_char) == 1:
            new_char = new_char.upper()

        result_chars.append(new_char)

    result = "".join(result_chars)

    # Пробелы заменяем на пробел + zero-width (для всех режимов, кроме natural).
    result = re.sub(r"\s+", " " + ZWSP, result)

    return result


if __name__ == "__main__":
    sample = "Привет друзья! Сегодня я покажу крутой способ 2026"
    print(obfuscate(sample, mode="tiktok", intensity=75))
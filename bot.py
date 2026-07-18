"""Telegram-бот: обфускатор текста (тот же движок, что и на сайте).

Управление — через inline-кнопки главного меню. Просто пришлите любой
текст — бот вернёт обфусцированную версию.

Главное меню (кнопки под сообщением):
    🎛 Режим       — выбор режима (tiktok / strange / max)
    🎚 Интенсивность — кнопки ±5 / ±25 (диапазон 40–95)
    ⚙️ Настройки    — текущие параметры
    ❓ Справка      — помощь
"""

import asyncio
import html
import logging
import os
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    CopyTextButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from obfuscator import obfuscate, VALID_MODES

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bypass-bot")

TOKEN = os.environ.get("BOT_TOKEN", "")

MODE_LABELS = {"tiktok": "TikTok Safe", "strange": "Странный", "max": "Максимальный"}

WELCOME = (
    "🛡 <b>TikTok Bypass Bot</b>\n\n"
    "Пришлите любой текст — верну обфусцированную версию "
    "(гомоглифы + zero-width + диакритики).\n\n"
    "Выберите действие 👇"
)


@dataclass
class Settings:
    mode: str = "tiktok"
    intensity: int = 75


# Хранилище настроек пользователей в памяти (перезапуск бота сбрасывает).
user_settings: dict[int, Settings] = {}


def get_settings(user_id: int) -> Settings:
    return user_settings.setdefault(user_id, Settings())


# ---------- Клавиатуры ----------


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎛 Режим", callback_data="menu:mode")
    kb.button(text="🎚 Интенсивность", callback_data="menu:intensity")
    kb.button(text="⚙️ Настройки", callback_data="menu:settings")
    kb.button(text="❓ Справка", callback_data="menu:help")
    kb.adjust(2, 2)
    return kb.as_markup()


def mode_keyboard(current: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for mode in VALID_MODES:
        marker = "✅ " if mode == current else ""
        kb.button(text=f"{marker}{MODE_LABELS[mode]}", callback_data=f"mode:{mode}")
    kb.button(text="← Назад", callback_data="menu:main")
    kb.adjust(3, 1)
    return kb.as_markup()


def intensity_keyboard(value: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="−25", callback_data="int:-25")
    kb.button(text="−5", callback_data="int:-5")
    kb.button(text=f"Сейчас: {value}%", callback_data="int:noop")
    kb.button(text="+5", callback_data="int:+5")
    kb.button(text="+25", callback_data="int:+25")
    kb.button(text="← Назад", callback_data="menu:main")
    kb.adjust(2, 1, 2, 1)
    return kb.as_markup()


def back_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="← В меню", callback_data="menu:main")
    return kb.as_markup()


# ---------- Тексты экранов ----------


def settings_text(s: Settings) -> str:
    return (
        "⚙️ <b>Настройки</b>\n\n"
        f"Режим: <b>{MODE_LABELS[s.mode]}</b>\n"
        f"Интенсивность: <b>{s.intensity}%</b>"
    )


HELP_TEXT = (
    "❓ <b>Как пользоваться</b>\n\n"
    "1. Просто пришлите текст — получите результат.\n"
    "2. <b>🎛 Режим</b>:\n"
    "   • <b>TikTok Safe</b> — гомоглифы + диакритики + zwsp\n"
    "   • <b>Странный</b> — только гомоглифы\n"
    "   • <b>Максимальный</b> — максимальное искажение\n"
    "3. <b>🎚 Интенсивность</b> — кнопки ±5 / ±25 (40–95).\n"
    "4. <b>⚙️ Настройки</b> — текущие параметры.\n\n"
    "Пришлите текст, чтобы получить обфусцированную версию."
)


INTENSITY_HEADER = "🎚 <b>Интенсивность обфускации</b>\n\nКнопками меняйте значение (40–95):"


# ---------- Хендлеры команд ----------


async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME, reply_markup=main_menu())


# ---------- Хендлеры кнопок ----------


async def menu_main(cb: CallbackQuery) -> None:
    await cb.message.edit_text(WELCOME, reply_markup=main_menu())
    await cb.answer()


async def menu_mode(cb: CallbackQuery) -> None:
    s = get_settings(cb.from_user.id)
    await cb.message.edit_text(
        "🎛 <b>Режим обфускации</b>\n\nВыберите режим:", reply_markup=mode_keyboard(s.mode)
    )
    await cb.answer()


async def menu_intensity(cb: CallbackQuery) -> None:
    s = get_settings(cb.from_user.id)
    await cb.message.edit_text(INTENSITY_HEADER, reply_markup=intensity_keyboard(s.intensity))
    await cb.answer()


async def menu_settings(cb: CallbackQuery) -> None:
    s = get_settings(cb.from_user.id)
    await cb.message.edit_text(settings_text(s), reply_markup=back_keyboard())
    await cb.answer()


async def menu_help(cb: CallbackQuery) -> None:
    await cb.message.edit_text(HELP_TEXT, reply_markup=back_keyboard())
    await cb.answer()


async def mode_callback(cb: CallbackQuery) -> None:
    mode = cb.data.split(":", 1)[1]
    if mode not in VALID_MODES:
        await cb.answer("Неизвестный режим")
        return
    s = get_settings(cb.from_user.id)
    s.mode = mode
    await cb.message.edit_reply_markup(reply_markup=mode_keyboard(mode))
    await cb.answer(f"Режим: {MODE_LABELS[mode]}")


async def intensity_callback(cb: CallbackQuery) -> None:
    payload = cb.data.split(":", 1)[1]
    if payload == "noop":
        await cb.answer()
        return
    try:
        delta = int(payload)
    except ValueError:
        await cb.answer()
        return
    s = get_settings(cb.from_user.id)
    s.intensity = max(40, min(95, s.intensity + delta))
    await cb.message.edit_reply_markup(reply_markup=intensity_keyboard(s.intensity))
    await cb.answer(f"Интенсивность: {s.intensity}%")


# ---------- Хендлер текста ----------


async def handle_text(message: Message) -> None:
    s = get_settings(message.from_user.id)
    text = message.text or ""
    if not text:
        return
    result = obfuscate(text, mode=s.mode, intensity=s.intensity)
    limit = 4000
    if len(result) > limit:
        result = result[:limit] + "…"

    # Моноширинный блок: легко выделить и скопировать, невидимые символы
    # (zwsp, диакритики) сохраняются. Экранируем на случай <, &, > в тексте.
    rendered = f"<pre>{html.escape(result)}</pre>"

    # Кнопка «Скопировать» копирует точный результат в буфер. Лимит Bot API —
    # 256 символов, поэтому добавляем кнопку только для коротких результатов.
    reply_markup = None
    if 1 <= len(result) <= 256:
        kb = InlineKeyboardBuilder()
        kb.button(text="📋 Скопировать", copy_text=CopyTextButton(text=result))
        reply_markup = kb.as_markup()

    await message.answer(rendered, reply_markup=reply_markup)


# ---------- Сборка ----------


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.message.register(cmd_start, Command("start"))
    dp.callback_query.register(menu_main, F.data == "menu:main")
    dp.callback_query.register(menu_mode, F.data == "menu:mode")
    dp.callback_query.register(menu_intensity, F.data == "menu:intensity")
    dp.callback_query.register(menu_settings, F.data == "menu:settings")
    dp.callback_query.register(menu_help, F.data == "menu:help")
    dp.callback_query.register(mode_callback, F.data.startswith("mode:"))
    dp.callback_query.register(intensity_callback, F.data.startswith("int:"))
    dp.message.register(handle_text, F.text)
    return dp


async def main() -> None:
    if not TOKEN:
        raise SystemExit(
            "Не задан BOT_TOKEN. Создайте бота у @BotFather и запустите:\n"
            "  set BOT_TOKEN=123:abc        (cmd)\n"
            "  $env:BOT_TOKEN='123:abc'    (PowerShell)\n"
            "  export BOT_TOKEN=123:abc     (bash)"
        )
    bot = Bot(
        TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()
    log.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
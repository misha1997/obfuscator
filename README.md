# TikTok Bypass — сайт + Telegram-бот на Python

Обфускатор текста: гомоглифы (латиница → кириллица-двойники), zero-width space и
комбинируемые диакритики. Та же логика работает в `index.html` (на JS), в
веб-сервере и в Telegram-боте (общий модуль `obfuscator.py`).

## Структура

```
bot/
├── index.html       # сайт (клиентская обфускация на JS)
├── obfuscator.py    # общий движок обфускации (Python)
├── app.py           # Flask-сервер: раздаёт сайт + JSON-API
├── bot.py           # Telegram-бот (aiogram 3.x)
├── requirements.txt
└── .env.example
```

## Установка (через venv)

```bash
python -m venv venv

# Windows (Git Bash / cmd)
venv\Scripts\activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

После активации venv команды `python` и `pip` будут указывать на окружение проекта.
Деактивация: `deactivate`.

## Веб-сайт

```bash
python app.py
```

Откройте http://127.0.0.1:5000 — там интерфейс из `index.html`.

JSON-API (серверная обфускация):

```bash
curl -X POST http://127.0.0.1:5000/api/obfuscate \
  -H "Content-Type: application/json" \
  -d '{"text":"Привет 2026","mode":"tiktok","intensity":75}'
```

Параметры: `mode` — `tiktok` | `strange` | `max`; `intensity` — 40–95.

## Telegram-бот

1. Создайте бота у [@BotFather](https://t.me/BotFather) и скопируйте токен.
2. Задайте переменную окружения:

   **cmd:**     `set BOT_TOKEN=123:abc`
   **PowerShell:** `$env:BOT_TOKEN='123:abc'`
   **bash:**    `export BOT_TOKEN=123:abc`

3. Запустите:

   ```bash
   python bot.py
   ```

Команды бота:
- `/start` — приветствие
- `/help` — справка
- `/mode` — выбрать режим (кнопки)
- `/intensity 80` — интенсивность 40–95
- `/settings` — текущие настройки
- Любой текст → обфусцированный результат.
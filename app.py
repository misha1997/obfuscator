"""Веб-сервер для сайта TikTok Bypass.

- Раздаёт index.html (там вся клиентская обфускация на JS).
- Отдаёт JSON-API /api/obfuscate для тех, кто хочет серверную обработку.

Запуск:
    python app.py
По умолчанию слушает http://127.0.0.1:5000
"""

import os
from flask import Flask, request, jsonify, send_from_directory

from obfuscator import obfuscate, VALID_MODES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/obfuscate", methods=["POST"])
def api_obfuscate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    mode = data.get("mode", "tiktok")
    intensity = data.get("intensity", 75)

    if not isinstance(text, str):
        return jsonify({"error": "text must be a string"}), 400
    if not isinstance(intensity, (int, float)):
        return jsonify({"error": "intensity must be a number"}), 400
    if mode not in VALID_MODES:
        return jsonify({"error": f"mode must be one of {VALID_MODES}"}), 400

    result = obfuscate(text, mode=mode, intensity=int(intensity))
    return jsonify({"result": result, "mode": mode, "intensity": int(intensity)})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    app.run(host=host, port=port, debug=False)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Сервер для локальной разработки. Без localtunnel.
Запуск: python run.py
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def print_info(msg):
    print(f"[INFO] {msg}")

def print_ok(msg):
    print(f"[OK] {msg}")

def print_debug(msg):
    print(f"[DEBUG] {msg}")

def main():
    print_info("=" * 60)
    print_info("Запуск FastAPI сервера (локально, без localtunnel)")
    print_info("=" * 60)
    
    # Устанавливаем API_URL для фронтенда (локальный)
    api_url = "http://localhost:8000"
    env_path = Path(__file__).parent / ".." / ".env"
    if env_path.exists():
        content = env_path.read_text(encoding='utf-8')
        if "API_URL=" in content:
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("API_URL="):
                    lines[i] = f"API_URL={api_url}"
            env_path.write_text("\n".join(lines), encoding='utf-8')
            print_ok(f"API_URL сохранён в .env: {api_url}")
    
    # Обновляем main.js
    main_js_path = Path(__file__).parent / ".." / "frontend" / "main.js"
    if main_js_path.exists():
        content = main_js_path.read_text(encoding='utf-8')
        # Просто заменяем API_URL в коде
        import re
        content = re.sub(
            r"const API_URL = window\.API_URL \|\| '[^']*'",
            f"const API_URL = window.API_URL || '{api_url}'",
            content
        )
        main_js_path.write_text(content, encoding='utf-8')
        print_ok(f"main.js обновлён: API_URL = {api_url}")
    
    print_info("")
    print_info("Запуск Uvicorn сервера...")
    print_info(f"Сервер будет доступен по адресу: {api_url}")
    print_info("Нажмите CTRL+C для остановки")
    print_info("=" * 60)
    print_info("")
    
    # Запускаем Uvicorn напрямую
    cmd = [
        sys.executable,
        "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print_info("Сервер остановлен")
        sys.exit(0)
    except Exception as e:
        print_debug(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

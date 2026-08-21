import uvicorn
import subprocess
import time
import re
import os
import threading
import sys

def get_localtunnel_url(port=8000, timeout=30):
    """
    Запускает localtunnel и возвращает публичный URL.
    Использует npx для запуска, т.к. это самый простой способ.
    """
    print("🚀 Запуск localtunnel...")
    try:
        # Проверяем, установлен ли Node.js/npx
        subprocess.run(["npx", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ npx не найден. Установите Node.js или используйте ручной URL.")
        return None, None

    # Запускаем localtunnel
    process = subprocess.Popen(
        ["npx", "localtunnel", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    
    url = None
    start_time = time.time()
    
    # Читаем вывод в реальном времени
    while time.time() - start_time < timeout:
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        print(f"[localtunnel] {line.strip()}")
        if "your url is:" in line:
            match = re.search(r"https://[^\s]+", line)
            if match:
                url = match.group(0)
                print(f"✅ Туннель открыт: {url}")
                break
        if "error" in line.lower():
            print(f"❌ Ошибка localtunnel: {line}")
            break
    
    return url, process

def update_env_file(url):
    """Обновляет или создаёт .env файл с API_URL"""
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    env_path = os.path.abspath(env_path)
    
    # Читаем существующий .env
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    
    # Обновляем или добавляем API_URL
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith("API_URL="):
            new_lines.append(f"API_URL={url}\n")
            updated = True
        else:
            new_lines.append(line)
    
    if not updated:
        new_lines.append(f"API_URL={url}\n")
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print(f"✅ .env обновлён: API_URL={url}")

def update_frontend_config(url):
    """Обновляет frontend/app.js для использования API_URL"""
    frontend_paths = [
        os.path.join(os.path.dirname(__file__), "..", "frontend", "app.js"),
        os.path.join(os.path.dirname(__file__), "..", "docs", "frontend", "app.js")
    ]
    
    for path in frontend_paths:
        if not os.path.exists(path):
            continue
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Если в файле есть объявление API_BASE, заменяем его
        if "const API_BASE =" in content:
            # Заменяем на чтение из переменной окружения
            new_content = re.sub(
                r"const API_BASE = .*?;",
                f"const API_BASE = window.API_URL || '{url}';",
                content
            )
            
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ Обновлён {os.path.basename(path)} с URL: {url}")

def start_uvicorn():
    """Запускает FastAPI сервер"""
    print("🚀 Запуск FastAPI сервера...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    # Сначала запускаем localtunnel в отдельном потоке
    tunnel_url = None
    tunnel_process = None
    
    # Проверяем, не передан ли URL через аргумент командной строки
    if len(sys.argv) > 1 and sys.argv[1].startswith("--url="):
        tunnel_url = sys.argv[1].split("=")[1]
        print(f"📌 Используется переданный URL: {tunnel_url}")
    else:
        # Запускаем localtunnel
        tunnel_url, tunnel_process = get_localtunnel_url(8000)
        if tunnel_url:
            update_env_file(tunnel_url)
            update_frontend_config(tunnel_url)
        else:
            print("⚠️ Не удалось получить URL localtunnel. Используйте localhost.")
    
    # Запускаем сервер
    try:
        start_uvicorn()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
        if tunnel_process:
            tunnel_process.terminate()

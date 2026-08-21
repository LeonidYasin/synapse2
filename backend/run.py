import uvicorn
import subprocess
import time
import re
import os
import sys

def get_localtunnel_url(port=8000, timeout=30):
    """
    Запускает localtunnel и возвращает публичный URL.
    Использует npx для запуска.
    """
    print("[INFO] Запуск localtunnel...")
    try:
        subprocess.run(["npx", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[WARN] npx не найден. Установите Node.js или используйте ручной URL.")
        print("[INFO] Для ручного ввода: python run.py --url=https://your-url.loca.lt")
        return None

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
    
    while time.time() - start_time < timeout:
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        if "your url is:" in line:
            match = re.search(r"https://[^\s]+", line)
            if match:
                url = match.group(0)
                print(f"[OK] Туннель открыт: {url}")
                break
        if "error" in line.lower():
            print(f"[ERROR] Ошибка localtunnel: {line}")
            break
    
    if url:
        # Сохраняем URL в переменную окружения
        os.environ["API_URL"] = url
        print(f"[OK] API_URL установлен: {url}")
        
        # Также сохраняем в файл .env
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"API_URL={url}\n")
        print(f"[OK] URL сохранён в {env_path}")
    else:
        print("[WARN] Не удалось получить URL localtunnel. Используйте localhost.")
    
    return url

def start_uvicorn():
    """Запускает FastAPI сервер"""
    print("[INFO] Запуск FastAPI сервера...")
    print("[INFO] Открой в браузере: http://localhost:8000/")
    api_url = os.getenv("API_URL", "не задан")
    print(f"[INFO] Публичный адрес: {api_url}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    # Проверяем, не передан ли URL через аргумент командной строки
    if len(sys.argv) > 1 and sys.argv[1].startswith("--url="):
        url = sys.argv[1].split("=")[1]
        os.environ["API_URL"] = url
        print(f"[INFO] Используется переданный URL: {url}")
    else:
        # Запускаем localtunnel
        get_localtunnel_url(8000)
    
    # Запускаем сервер
    try:
        start_uvicorn()
    except KeyboardInterrupt:
        print("\n[INFO] Остановка сервера...")

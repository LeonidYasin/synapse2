import uvicorn
import subprocess
import time
import re
import os
import sys
import shutil

def find_npx():
    # Пробуем shutil.which
    for cmd in ["npx", "npx.cmd"]:
        path = shutil.which(cmd)
        if path:
            return path
    # Windows: ищем в стандартных папках
    if sys.platform == "win32":
        paths = [
            os.path.expanduser("~\\AppData\\Roaming\\npm\\npx.cmd"),
            os.path.expanduser("~\\AppData\\Roaming\\npm\\npx"),
            "C:\\Program Files\\nodejs\\npx.cmd",
            "C:\\Program Files\\nodejs\\npx",
            "C:\\Program Files (x86)\\nodejs\\npx.cmd",
        ]
        for p in paths:
            if os.path.exists(p):
                return p
    return None

print("[INFO] Запуск run.py")
print(f"[DEBUG] Аргументы: {sys.argv}")

if len(sys.argv) > 1 and sys.argv[1].startswith("--url="):
    url = sys.argv[1].split("=")[1]
    os.environ["API_URL"] = url
    print(f"[INFO] Используется переданный URL: {url}")
else:
    print("[INFO] Запуск localtunnel...")
    npx_cmd = find_npx()
    if not npx_cmd:
        print("[WARN] npx не найден. Установите Node.js или передайте URL вручную.")
        print("[INFO] python run.py --url=https://your-url.loca.lt")
    else:
        print(f"[DEBUG] Используется npx: {npx_cmd}")
        try:
            subprocess.run([npx_cmd, "--version"], capture_output=True, check=True)
        except Exception as e:
            print(f"[ERROR] npx не работает: {e}")
            sys.exit(1)
        process = subprocess.Popen(
            [npx_cmd, "localtunnel", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        url = None
        start_time = time.time()
        print("[INFO] Ожидание URL от localtunnel (максимум 30 секунд)...")
        while time.time() - start_time < 30:
            line = process.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            line = line.strip()
            print(f"[DEBUG] {line}")
            if "your url is:" in line:
                match = re.search(r"https://[^\s]+", line)
                if match:
                    url = match.group(0)
                    print(f"[OK] Туннель открыт: {url}")
                    os.environ["API_URL"] = url
                    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.write(f"API_URL={url}\n")
                    print(f"[OK] URL сохранён в {env_path}")
                    break
            if "error" in line.lower():
                print(f"[ERROR] Ошибка localtunnel: {line}")
                break
        if not url:
            print("[WARN] Не удалось получить URL localtunnel.")
            print("[INFO] Запустите localtunnel вручную: npx localtunnel --port 8000")
            print("[INFO] И передайте URL: python run.py --url=https://your-url.loca.lt")

print("[INFO] Запуск FastAPI сервера...")
print("[INFO] Открой в браузере: http://localhost:8000/")
api_url = os.getenv("API_URL", "не задан")
print(f"[INFO] Публичный адрес: {api_url}")
print("[INFO] Нажмите CTRL+C для остановки")
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

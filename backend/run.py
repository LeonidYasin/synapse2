import uvicorn
import subprocess
import time
import re
import os
import sys


def get_localtunnel_url(port=8000, timeout=30):
    print("🚀 Запуск localtunnel...")
    try:
        subprocess.run(["npx", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ npx не найден. Установите Node.js или используйте ручной URL.")
        print("💡 Для ручного ввода: python run.py --url=https://your-url.loca.lt")
        return None

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
                print(f"✅ Туннель открыт: {url}")
                break
        if "error" in line.lower():
            print(f"❌ Ошибка localtunnel: {line}")
            break
    
    if url:
        os.environ["API_URL"] = url
        print(f"✅ API_URL установлен: {url}")
        
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"API_URL={url}\n")
        print(f"✅ URL сохранён в {env_path}")
    else:
        print("⚠️ Не удалось получить URL localtunnel. Используйте localhost.")
    
    return url


def start_uvicorn():
    print("🚀 Запуск FastAPI сервера...")
    print("📌 Открой в браузере: http://localhost:8000/")
    print("📌 Если localtunnel запущен, публичный адрес: ", os.getenv("API_URL", "не задан"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].startswith("--url="):
        url = sys.argv[1].split("=")[1]
        os.environ["API_URL"] = url
        print(f"📌 Используется переданный URL: {url}")
    else:
        get_localtunnel_url(8000)
    
    try:
        start_uvicorn()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")

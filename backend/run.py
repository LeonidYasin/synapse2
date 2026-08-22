import uvicorn
import subprocess
import time
import re
import os
import sys
import shutil

def find_npx():
    """Находит путь к npx в системе."""
    # 1. Проверяем через shutil.which
    npx_path = shutil.which("npx")
    if npx_path:
        return npx_path
    
    # 2. Для Windows: пробуем через where
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["where", "npx"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                paths = result.stdout.strip().split('\n')
                if paths:
                    return paths[0]
        except Exception:
            pass
        
        # 3. Проверяем стандартные пути
        possible_paths = [
            os.path.expanduser("~\\AppData\\Roaming\\npm\\npx.cmd"),
            os.path.expanduser("~\\AppData\\Roaming\\npm\\npx"),
            "C:\\Program Files\\nodejs\\npx.cmd",
            "C:\\Program Files\\nodejs\\npx",
            "C:\\Program Files (x86)\\nodejs\\npx.cmd",
            "C:\\Program Files (x86)\\nodejs\\npx",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    
    # 4. Для Linux/Mac: пробуем через which
    try:
        result = subprocess.run(
            ["which", "npx"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            path = result.stdout.strip()
            if path:
                return path
    except Exception:
        pass
    
    return None

def get_localtunnel_url(port=8000, timeout=30):
    print("[INFO] Запуск localtunnel...")
    npx_cmd = find_npx()
    if not npx_cmd:
        print("[WARN] npx не найден. Установите Node.js или используйте ручной URL.")
        print("[INFO] Для ручного ввода: python run.py --url=https://your-url.loca.lt")
        return None
    print(f"[DEBUG] Используется npx: {npx_cmd}")
    try:
        subprocess.run([npx_cmd, "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[ERROR] npx не работает: {e}")
        return None
    process = subprocess.Popen(
        [npx_cmd, "localtunnel", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    url = None
    start_time = time.time()
    print("[INFO] Ожидание URL от localtunnel...")
    while time.time() - start_time < timeout:
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
                break
        if "error" in line.lower():
            print(f"[ERROR] Ошибка localtunnel: {line}")
            break
    if url:
        os.environ["API_URL"] = url
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"API_URL={url}\n")
        print(f"[OK] URL сохранён в {env_path}")
    else:
        print("[WARN] Не удалось получить URL localtunnel. Используйте localhost.")
        print("[INFO] Попробуйте запустить localtunnel вручную:")
        print("[INFO] npx localtunnel --port 8000")
        print("[INFO] И затем передайте URL: python run.py --url=https://your-url.loca.lt")
    return url

if __name__ == "__main__":
    print("[INFO] Запуск run.py")
    print(f"[DEBUG] Аргументы: {sys.argv}")
    if len(sys.argv) > 1 and sys.argv[1].startswith("--url="):
        url = sys.argv[1].split("=")[1]
        os.environ["API_URL"] = url
        print(f"[INFO] Используется переданный URL: {url}")
    else:
        get_localtunnel_url(8000)
    print("[INFO] Запуск FastAPI сервера...")
    print("[INFO] Открой в браузере: http://localhost:8000/")
    api_url = os.getenv("API_URL", "не задан")
    print(f"[INFO] Публичный адрес: {api_url}")
    print("[INFO] Нажмите CTRL+C для остановки")
    try:
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
    except KeyboardInterrupt:
        print("\n[INFO] Остановка сервера...")

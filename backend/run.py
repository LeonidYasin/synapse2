import uvicorn
import subprocess
import time
import re
import os
import sys
import shutil

def find_npx():
    """Find path to npx in the system."""
    npx_path = shutil.which("npx")
    if npx_path:
        return npx_path
    
    if sys.platform == "win32":
        possible_paths = [
            os.path.expanduser("~\\AppData\\Roaming\\npm\\npx.cmd"),
            os.path.expanduser("~\\AppData\\Roaming\\npm\\npx"),
            "C:\\Program Files\\nodejs\\npx.cmd",
            "C:\\Program Files\\nodejs\\npx",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    
    return None

def get_localtunnel_url(port=8000, timeout=30):
    """
    Start localtunnel and return public URL.
    Uses npx to run localtunnel.
    """
    print("[INFO] Starting localtunnel...")
    
    npx_cmd = find_npx()
    if not npx_cmd:
        print("[WARN] npx not found. Install Node.js or use manual URL.")
        print("[INFO] Manual usage: python run.py --url=https://your-url.loca.lt")
        return None
    
    print(f"[DEBUG] Using npx: {npx_cmd}")
    
    try:
        subprocess.run([npx_cmd, "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"[ERROR] npx is not working: {npx_cmd}")
        return None

    process = subprocess.Popen(
        [npx_cmd, "localtunnel", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    )
    
    url = None
    start_time = time.time()
    
    print("[INFO] Waiting for URL from localtunnel...")
    
    while time.time() - start_time < timeout:
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        print(f"[DEBUG] {line.strip()}")
        if "your url is:" in line:
            match = re.search(r"https://[^\s]+", line)
            if match:
                url = match.group(0)
                print(f"[OK] Tunnel opened: {url}")
                break
        if "error" in line.lower():
            print(f"[ERROR] localtunnel error: {line}")
            break
    
    if url:
        os.environ["API_URL"] = url
        print(f"[OK] API_URL set: {url}")
        
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"API_URL={url}\n")
        print(f"[OK] URL saved to {env_path}")
        
        # Обновляем frontend/index.html с новым URL
        update_frontend_index_html(url)
        # Также обновляем main.js на всякий случай
        update_frontend_main_js(url)
    else:
        print("[WARN] Could not get URL from localtunnel. Using localhost.")
        print("[INFO] Try running localtunnel manually in another terminal:")
        print("[INFO] npx localtunnel --port 8000")
        print("[INFO] Then pass the URL: python run.py --url=https://your-url.loca.lt")
    
    return url

def update_frontend_index_html(url):
    """Обновляет window.API_URL в frontend/index.html"""
    index_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    
    if not os.path.exists(index_path):
        print(f"[WARN] index.html not found at {index_path}")
        return
    
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Заменяем window.API_URL = '...' на новый URL
    new_content = re.sub(
        r"window\.API_URL\s*=\s*['\"][^'\"]*['\"];",
        f"window.API_URL = '{url}';",
        content
    )
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[OK] Updated index.html with URL: {url}")

def update_frontend_main_js(url):
    """Обновляет API_URL в frontend/main.js"""
    main_js_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "main.js")
    
    if not os.path.exists(main_js_path):
        return
    
    with open(main_js_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Заменяем const API_URL = '...' на новый URL
    new_content = re.sub(
        r"const API_URL\s*=\s*['\"][^'\"]*['\"];",
        f"const API_URL = '{url}';",
        content
    )
    
    with open(main_js_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[OK] Updated main.js with URL: {url}")

def start_uvicorn():
    """Start FastAPI server."""
    print("[INFO] Starting FastAPI server...")
    print("[INFO] Open in browser: http://localhost:8000/")
    api_url = os.getenv("API_URL", "not set")
    print(f"[INFO] Public URL: {api_url}")
    print("[INFO] Press CTRL+C to stop")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    print("[INFO] Starting run.py script")
    print(f"[DEBUG] Command line arguments: {sys.argv}")
    
    # 1. Get URL first
    if len(sys.argv) > 1 and sys.argv[1].startswith("--url="):
        url = sys.argv[1].split("=")[1]
        os.environ["API_URL"] = url
        print(f"[INFO] Using provided URL: {url}")
        update_frontend_index_html(url)
        update_frontend_main_js(url)
    else:
        # Start localtunnel and wait for URL
        url = get_localtunnel_url(8000)
        if url:
            print("[INFO] Tunnel created successfully, continuing...")
        else:
            print("[INFO] Tunnel not created, continuing with localhost...")
    
    # 2. Wait for user confirmation
    print("\n" + "="*60)
    print("[INFO] Tunnel is ready!")
    print("[INFO] Press ENTER to start the server")
    print("[INFO] Press CTRL+C to cancel")
    print("="*60)
    
    try:
        input()  # Wait for ENTER key
    except KeyboardInterrupt:
        print("\n[INFO] Startup cancelled by user")
        sys.exit(0)
    
    # 3. Only after ENTER, start uvicorn
    try:
        start_uvicorn()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped")

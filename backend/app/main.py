import os
import sys
import hashlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# ============================================================
# ПРИНУДИТЕЛЬНЫЙ СБРОС БУФЕРА
# ============================================================
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# ============================================================
# ЛОГИРОВАНИЕ В ФАЙЛ
# ============================================================
LOG_FILE = "startup.log"

def log_to_file(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
        f.flush()

log_to_file("=" * 60)
log_to_file(f"STARTUP: {__file__} at {__import__('datetime').datetime.now()}")
log_to_file("MAIN.PY VERSION: 2026-08-22-v6-LOGFILE")
log_to_file("Checking file versions...")

files_to_check = [
    "app/main.py",
    "app/routers/auth.py",
    "app/auth.py",
    "app/models.py",
    "app/database.py",
]

for f in files_to_check:
    try:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
            lines = content.split("\n")[:10]
            version_line = None
            for line in lines:
                if "VERSION" in line or "v3" in line or "v4" in line or "v5" in line or "v6" in line:
                    version_line = line.strip()
                    break
            hash_short = hashlib.md5(content.encode()).hexdigest()[:8]
            msg = f"  {f}: {version_line or 'no version'} (md5: {hash_short})"
            log_to_file(msg)
            print(msg, flush=True)
    except Exception as e:
        msg = f"  {f}: ERROR - {e}"
        log_to_file(msg)
        print(msg, flush=True)

log_to_file("=" * 60)
log_to_file("")

print("=" * 60, flush=True)
print("MAIN.PY VERSION: 2026-08-22-v6-LOGFILE", flush=True)
print("Logs also written to: startup.log", flush=True)
print("=" * 60, flush=True)
# ============================================================

from .routers import auth, recommendations, waitlist, agent

app = FastAPI(title="Synapse API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем роутеры
app.include_router(auth.router)
app.include_router(recommendations.router)
app.include_router(waitlist.router)
app.include_router(agent.router)

msg = f"Routes registered: {[r.path for r in app.routes]}"
log_to_file(msg)
print(msg, flush=True)

# Middleware для логирования
@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    msg = f"[REQUEST] {request.method} {request.url.path}"
    log_to_file(msg)
    print(msg, flush=True)
    msg = f"[REQUEST] Content-Type: {request.headers.get('content-type', 'None')}"
    log_to_file(msg)
    print(msg, flush=True)
    try:
        if body:
            msg = f"[REQUEST] Body: {body.decode('utf-8', errors='replace')}"
            log_to_file(msg)
            print(msg, flush=True)
        else:
            msg = f"[REQUEST] Body: (empty)"
            log_to_file(msg)
            print(msg, flush=True)
    except:
        msg = f"[REQUEST] Body: (binary)"
        log_to_file(msg)
        print(msg, flush=True)
    response = await call_next(request)
    msg = f"[RESPONSE] Status: {response.status_code}"
    log_to_file(msg)
    print(msg, flush=True)
    return response

# Статика
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")

@app.get("/")
async def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/{path:path}")
async def static_files(path: str):
    file_path = os.path.join(FRONTEND_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

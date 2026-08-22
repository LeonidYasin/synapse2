import os
import sys
import hashlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# ============================================================
# ПРИНУДИТЕЛЬНЫЙ СБРОС БУФЕРА ДЛЯ НЕМЕДЛЕННОГО ВЫВОДА
# ============================================================
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# ============================================================
# ВЕРСИИ ФАЙЛОВ ПРИ СТАРТЕ (с принудительным выводом)
# ============================================================
print("=" * 60, flush=True)
print("MAIN.PY VERSION: 2026-08-22-v5-FINAL", flush=True)
print("Checking file versions...", flush=True)

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
                if "VERSION" in line or "v3" in line or "v4" in line or "v5" in line:
                    version_line = line.strip()
                    break
            hash_short = hashlib.md5(content.encode()).hexdigest()[:8]
            print(f"  {f}: {version_line or 'no version'} (md5: {hash_short})", flush=True)
    except Exception as e:
        print(f"  {f}: ERROR - {e}", flush=True)

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

print("=== MAIN.PY LOADED ===", flush=True)
print(f"Routes registered: {[r.path for r in app.routes]}", flush=True)

# Middleware для логирования
@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    print(f"============================================================", flush=True)
    print(f"[REQUEST] {request.method} {request.url.path}", flush=True)
    print(f"[REQUEST] Content-Type: {request.headers.get('content-type', 'None')}", flush=True)
    try:
        if body:
            print(f"[REQUEST] Body: {body.decode('utf-8', errors='replace')}", flush=True)
        else:
            print(f"[REQUEST] Body: (empty)", flush=True)
    except:
        print(f"[REQUEST] Body: (binary)", flush=True)
    print(f"============================================================", flush=True)
    response = await call_next(request)
    print(f"[RESPONSE] Status: {response.status_code}", flush=True)
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

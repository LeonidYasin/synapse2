from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import json

# Импортируем роутеры
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

# Проверка, что роутер загружен
print("=== MAIN.PY LOADED ===")
print(f"Routes registered: {[r.path for r in app.routes]}")

# Middleware для логирования
@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    print(f"============================================================")
    print(f"[REQUEST] {request.method} {request.url.path}")
    print(f"[REQUEST] Headers: {dict(request.headers)}")
    try:
        if body:
            print(f"[REQUEST] Body: {body.decode('utf-8', errors='replace')}")
        else:
            print(f"[REQUEST] Body: (empty)")
    except:
        print(f"[REQUEST] Body: (binary)")
    print(f"============================================================")
    response = await call_next(request)
    print(f"[RESPONSE] Status: {response.status_code}")
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

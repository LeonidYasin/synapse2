from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import json
import os

from .routers import auth, recommendations, waitlist, agent
from .routers import chat2 as chat
from .database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Synapse API", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования (без чтения тела)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print("=" * 60)
    print(f"[REQUEST] {request.method} {request.url.path}")
    print(f"[REQUEST] Headers: {dict(request.headers)}")
    print("=" * 60)
    
    response = await call_next(request)
    print(f"[RESPONSE] Status: {response.status_code}")
    return response

# Routers - ДО статических файлов!
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(recommendations.router)
app.include_router(waitlist.router)
app.include_router(agent.router)

# Static files (frontend) - ПОСЛЕ роутеров
static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    # Для корневого пути используем отдельный эндпоинт

@app.get("/")
async def serve_index():
    from fastapi.responses import HTMLResponse
    index_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return {"status": "ok", "message": "Frontend not found"}

@app.get("/{path:path}")
async def serve_static(path: str):
    from fastapi.responses import FileResponse, HTMLResponse
    import mimetypes
    
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
    file_path = os.path.join(frontend_dir, path)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Если файл не найден, пробуем index.html
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    
    return {"error": "File not found"}, 404

@app.get("/health")
async def health_check():
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .routers import chat, agent, auth, recommendations, waitlist
import os

app = FastAPI(title="Synapse API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем статические файлы (CSS, JS, изображения)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    # Монтируем всю папку фронтенда для статических файлов
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(agent.router)
app.include_router(recommendations.router)
app.include_router(waitlist.router)

@app.get("/")
async def serve_frontend():
    """
    Отдаёт фронтенд с подставленным API_URL.
    Если API_URL не задан, использует localhost.
    """
    api_url = os.getenv("API_URL", "http://localhost:8000")
    
    frontend_index = os.path.join(frontend_path, "index.html")
    try:
        with open(frontend_index, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>File frontend/index.html not found</h1>", status_code=404)
    
    # Вставляем API_URL в глобальную переменную JavaScript
    script_tag = f'<script>window.API_URL = "{api_url}";</script>'
    content = content.replace('</head>', f'{script_tag}\n</head>')
    
    return HTMLResponse(content=content)

@app.get("/style.css")
async def serve_css():
    """Отдаёт CSS файл"""
    css_path = os.path.join(frontend_path, "style.css")
    if os.path.exists(css_path):
        return FileResponse(css_path, media_type="text/css")
    return HTMLResponse(status_code=404)

@app.get("/app.js")
async def serve_js():
    """Отдаёт JS файл"""
    js_path = os.path.join(frontend_path, "app.js")
    if os.path.exists(js_path):
        return FileResponse(js_path, media_type="application/javascript")
    return HTMLResponse(status_code=404)

@app.get("/manifest.json")
async def serve_manifest():
    """Отдаёт manifest.json"""
    manifest_path = os.path.join(frontend_path, "manifest.json")
    if os.path.exists(manifest_path):
        return FileResponse(manifest_path, media_type="application/json")
    return HTMLResponse(status_code=404)

@app.get("/favicon.ico")
async def serve_favicon():
    """Отдаёт favicon.ico"""
    favicon_path = os.path.join(frontend_path, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    return HTMLResponse(status_code=404)

@app.get("/sw.js")
async def serve_sw():
    """Отдаёт service worker"""
    sw_path = os.path.join(frontend_path, "sw.js")
    if os.path.exists(sw_path):
        return FileResponse(sw_path, media_type="application/javascript")
    return HTMLResponse(status_code=404)

@app.get("/health")
async def health():
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")
    app.mount("/style.css", StaticFiles(directory=frontend_path, html=True), name="style")
    app.mount("/app.js", StaticFiles(directory=frontend_path, html=True), name="app")

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
    
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "index.html")
    try:
        with open(frontend_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>File frontend/index.html not found</h1>", status_code=404)
    
    # Вставляем API_URL в глобальную переменную JavaScript
    script_tag = f'<script>window.API_URL = "{api_url}";</script>'
    content = content.replace('</head>', f'{script_tag}\n</head>')
    
    return HTMLResponse(content=content)

@app.get("/health")
async def health():
    return {"status": "ok"}

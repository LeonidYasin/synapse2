from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(agent.router)
app.include_router(recommendations.router)
app.include_router(waitlist.router)

@app.get("/")
async def root():
    return {"message": "Synapse API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/app", response_class=HTMLResponse)
async def serve_app():
    """
    Отдаёт фронтенд с подставленным API_URL из переменной окружения.
    """
    # Берём URL из переменной окружения, или используем localhost по умолчанию
    api_url = os.getenv("API_URL", "http://localhost:8000")
    
    # Читаем файл index.html
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "index.html")
    try:
        with open(frontend_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Файл frontend/index.html не найден</h1>", status_code=404)
    
    # Вставляем API_URL в глобальную переменную JavaScript
    # Ищем тег <script> перед подключением app.js
    script_tag = f'<script>window.API_URL = "{api_url}";</script>'
    # Вставляем перед <script src="app.js">
    content = content.replace('</head>', f'{script_tag}</head>')
    
    return HTMLResponse(content=content)

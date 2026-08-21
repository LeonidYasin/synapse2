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
async def serve_frontend():
    """
    Отдаёт фронтенд с подставленным API_URL.
    Если API_URL не задан, использует текущий хост из запроса.
    """
    api_url = os.getenv("API_URL", "http://localhost:8000")
    
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "index.html")
    try:
        with open(frontend_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Файл frontend/index.html не найден</h1>", status_code=404)
    
    script_tag = f'<script>window.API_URL = "{api_url}";</script>'
    content = content.replace('</head>', f'{script_tag}\n</head>')
    
    return HTMLResponse(content=content)

@app.get("/app", response_class=HTMLResponse)
async def serve_app():
    return await serve_frontend()

@app.get("/health")
async def health():
    return {"status": "ok"}

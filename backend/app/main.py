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

# Middleware для логирования всех запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print("=" * 60)
    print(f"[REQUEST] {request.method} {request.url.path}")
    print(f"[REQUEST] Headers: {dict(request.headers)}")
    
    # Пытаемся прочитать тело запроса
    try:
        body = await request.body()
        if body:
            try:
                body_str = body.decode('utf-8')
                print(f"[REQUEST] Body: {body_str}")
            except:
                print(f"[REQUEST] Body: (binary, {len(body)} bytes)")
        else:
            print("[REQUEST] Body: (empty)")
    except Exception as e:
        print(f"[REQUEST] Body read error: {e}")
    
    print("=" * 60)
    
    response = await call_next(request)
    print(f"[RESPONSE] Status: {response.status_code}")
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(recommendations.router)
app.include_router(waitlist.router)
app.include_router(agent.router)

# Static files (frontend)
static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

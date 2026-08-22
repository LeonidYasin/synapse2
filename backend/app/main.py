from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import json

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

print("=== MAIN.PY LOADED ===")
print(f"Routes registered: {[r.path for r in app.routes]}")

# ТЕСТОВЫЙ ЭНДПОИНТ ПРЯМО В MAIN.PY
@app.post("/test")
async def test_post(request: Request):
    print("=== TEST POST CALLED ===")
    try:
        body = await request.body()
        print(f"Raw body: {body}")
        data = json.loads(body)
        print(f"Parsed: {data}")
        return {"status": "ok", "data": data}
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})

# Middleware для логирования - НЕ читает тело запроса
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"============================================================")
    print(f"[REQUEST] {request.method} {request.url.path}")
    print(f"[REQUEST] Content-Type: {request.headers.get('content-type')}")
    
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

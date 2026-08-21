from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat, agent, auth, recommendations, waitlist

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

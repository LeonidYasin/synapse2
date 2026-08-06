from fastapi import APIRouter, Depends, HTTPException
from ..models import ProfileRequest
from ..database import SessionLocal, Profile
from ..auth import get_current_user
from ..agent.scanner import AgentScanner
import json
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/agent", tags=["agent"])

class ProfileResponse(BaseModel):
    topics: List[str]
    summary: str
    entities: Optional[List[str]] = []
    intentions: Optional[List[str]] = []

@router.post("/analyze", response_model=ProfileResponse)
async def analyze(request: ProfileRequest):
    """
    Анализирует диалоги пользователя и строит профиль.
    Если user_id не указан, используется текущий аутентифицированный пользователь.
    """
    # Используем переданный user_id или заглушку для демо
    user_id = request.user_id or "demo-user"
    
    # Сохраняем диалоги в БД, если они переданы
    if request.messages:
        db = SessionLocal()
        for msg in request.messages:
            # Здесь можно сохранять диалоги
            pass
        db.close()
    
    # Создаем сканер и запускаем анализ
    scanner = AgentScanner(user_id)
    result = await scanner.scan_and_update_profile()
    
    if result.get("status") == "no_dialogues":
        # Если диалогов нет, пытаемся получить профиль из БД
        db = SessionLocal()
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        db.close()
        if profile:
            return ProfileResponse(
                topics=json.loads(profile.topics) if profile.topics else [],
                summary=profile.summary or "Профиль пока не заполнен",
                entities=[],
                intentions=[]
            )
        raise HTTPException(status_code=404, detail="Диалоги не найдены")
    
    return ProfileResponse(
        topics=result.get("topics", []),
        summary=result.get("summary", ""),
        entities=result.get("entities", []),
        intentions=result.get("intentions", [])
    )

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(current_user = Depends(get_current_user)):
    """
    Получает профиль текущего пользователя.
    Требуется аутентификация.
    """
    db = SessionLocal()
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    db.close()
    
    if not profile:
        return ProfileResponse(
            topics=[],
            summary="Профиль ещё не создан. Начните общаться с ИИ, чтобы агент мог проанализировать ваши интересы.",
            entities=[],
            intentions=[]
        )
    
    return ProfileResponse(
        topics=json.loads(profile.topics) if profile.topics else [],
        summary=profile.summary or "",
        entities=[],
        intentions=[]
    )

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import ProfileRequest, ProfileResponse, Profile
from ..database import get_db
from ..auth import get_current_user
from ..agent.scanner import AgentScanner
import json
from typing import List, Optional

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/analyze", response_model=ProfileResponse)
async def analyze(
    request: ProfileRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Анализирует диалоги пользователя и строит профиль.
    Использует текущего аутентифицированного пользователя.
    """
    # Используем ID текущего пользователя
    user_id = current_user.id
    
    # Проверяем, есть ли уже профиль
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    
    # Создаем сканер и запускаем анализ
    scanner = AgentScanner(str(user_id))
    
    # Если есть сообщения в запросе, сохраняем их
    if request.messages:
        # Здесь можно сохранять диалоги в БД
        pass
    
    result = await scanner.scan_and_update_profile()
    
    if result.get("status") == "no_dialogues":
        # Если диалогов нет, пытаемся получить профиль из БД
        if profile:
            return ProfileResponse(
                topics=json.loads(profile.topics) if profile.topics else [],
                summary=profile.summary or "Профиль пока не заполнен",
                entities=[],
                intentions=[]
            )
        return ProfileResponse(
            topics=[],
            summary="У вас пока нет диалогов. Начните общение, чтобы агент мог проанализировать ваши интересы.",
            entities=[],
            intentions=[]
        )
    
    # Обновляем или создаём профиль в БД
    topics_json = json.dumps(result.get("topics", []))
    summary = result.get("summary", "")
    
    if profile:
        profile.topics = topics_json
        profile.summary = summary
    else:
        new_profile = Profile(
            user_id=user_id,
            topics=topics_json,
            summary=summary
        )
        db.add(new_profile)
    db.commit()
    
    return ProfileResponse(
        topics=result.get("topics", []),
        summary=result.get("summary", ""),
        entities=result.get("entities", []),
        intentions=result.get("intentions", [])
    )

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получает профиль текущего пользователя.
    Требуется аутентификация.
    """
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
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

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal, Profile, User
from ..auth import get_current_user
import json
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

class MatchResponse(BaseModel):
    user_id: str
    common_topics: List[str]
    match_score: float
    summary: str

@router.get("/matches", response_model=List[MatchResponse])
async def get_matches(current_user: User = Depends(get_current_user)):
    """
    Находит пользователей с похожими интересами на основе профилей.
    """
    db = SessionLocal()
    
    # Получаем профиль текущего пользователя
    current_profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if not current_profile or not current_profile.topics:
        db.close()
        return []
    
    current_topics = set(json.loads(current_profile.topics))
    
    # Получаем все профили других пользователей
    all_profiles = db.query(Profile).filter(Profile.user_id != current_user.id).all()
    db.close()
    
    matches = []
    for profile in all_profiles:
        if not profile.topics:
            continue
        other_topics = set(json.loads(profile.topics))
        
        # Находим общие темы
        common = current_topics.intersection(other_topics)
        if common:
            # Вычисляем score как долю общих тем
            union = current_topics.union(other_topics)
            score = len(common) / len(union) if union else 0
            
            # Добавляем бонус за количество общих тем
            score = min(score * 1.5, 1.0)
            
            matches.append(MatchResponse(
                user_id=profile.user_id,
                common_topics=list(common),
                match_score=round(score * 100, 1),
                summary=profile.summary or "Пользователь с похожими интересами"
            ))
    
    # Сортируем по убыванию score
    matches.sort(key=lambda x: x.match_score, reverse=True)
    return matches[:10]

@router.get("/suggestions")
async def get_suggestions(current_user: User = Depends(get_current_user)):
    """
    Возвращает предложения по улучшению профиля и поиску связей.
    """
    db = SessionLocal()
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    db.close()
    
    if not profile or not profile.topics:
        return {"suggestions": ["Начните общаться с ИИ, чтобы агент мог проанализировать ваши интересы."]}
    
    topics = json.loads(profile.topics)
    suggestions = []
    
    if len(topics) < 3:
        suggestions.append("Попробуйте обсудить с ИИ больше разных тем, чтобы профиль стал полнее.")
    
    if "партнёр" in str(topics).lower() or "инвестор" in str(topics).lower():
        suggestions.append("В ваших диалогах часто упоминается поиск партнёров. Попробуйте заполнить профиль подробнее, чтобы найти лучшие совпадения.")
    
    if not suggestions:
        suggestions.append("Ваш профиль активен. Продолжайте общаться с ИИ, чтобы получать более точные рекомендации.")
    
    return {"suggestions": suggestions}

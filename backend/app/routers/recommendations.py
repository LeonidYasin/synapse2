from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import User, Dialogue
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
    Находит пользователей с похожими интересами на основе диалогов.
    """
    db = SessionLocal()
    
    # Получаем диалоги текущего пользователя
    current_dialogues = db.query(Dialogue).filter(Dialogue.user_id == current_user.id).all()
    if not current_dialogues:
        db.close()
        return []
    
    # Извлекаем темы из диалогов
    current_topics = set()
    for dialogue in current_dialogues:
        if dialogue.messages:
            try:
                messages = json.loads(dialogue.messages)
                for msg in messages:
                    if isinstance(msg, dict) and 'content' in msg:
                        # Простой анализ: ищем ключевые слова
                        content = msg.get('content', '').lower()
                        # Извлекаем простые темы (слова длиннее 4 символов)
                        words = [w for w in content.split() if len(w) > 4]
                        current_topics.update(words[:10])  # ограничиваем
            except:
                pass
    
    if not current_topics:
        db.close()
        return []
    
    # Получаем всех других пользователей
    all_users = db.query(User).filter(User.id != current_user.id).all()
    matches = []
    
    for user in all_users:
        # Получаем диалоги пользователя
        user_dialogues = db.query(Dialogue).filter(Dialogue.user_id == user.id).all()
        user_topics = set()
        
        for dialogue in user_dialogues:
            if dialogue.messages:
                try:
                    messages = json.loads(dialogue.messages)
                    for msg in messages:
                        if isinstance(msg, dict) and 'content' in msg:
                            content = msg.get('content', '').lower()
                            words = [w for w in content.split() if len(w) > 4]
                            user_topics.update(words[:10])
                except:
                    pass
        
        if user_topics:
            common = current_topics.intersection(user_topics)
            if common:
                union = current_topics.union(user_topics)
                score = len(common) / len(union) if union else 0
                score = min(score * 1.5, 1.0)
                
                matches.append(MatchResponse(
                    user_id=str(user.id),
                    common_topics=list(common)[:10],
                    match_score=round(score * 100, 1),
                    summary=f"Пользователь {user.username} — общие интересы"
                ))
    
    db.close()
    matches.sort(key=lambda x: x.match_score, reverse=True)
    return matches[:10]

@router.get("/suggestions")
async def get_suggestions(current_user: User = Depends(get_current_user)):
    """
    Возвращает предложения по улучшению профиля и поиску связей.
    """
    db = SessionLocal()
    dialogues = db.query(Dialogue).filter(Dialogue.user_id == current_user.id).all()
    db.close()
    
    if not dialogues:
        return {"suggestions": ["Начните общаться с ИИ, чтобы агент мог проанализировать ваши интересы."]}
    
    suggestions = []
    
    # Проверяем количество диалогов
    if len(dialogues) < 3:
        suggestions.append("Попробуйте обсудить с ИИ больше разных тем, чтобы профиль стал полнее.")
    
    # Проверяем наличие ключевых слов
    all_text = ""
    for dialogue in dialogues:
        if dialogue.messages:
            try:
                messages = json.loads(dialogue.messages)
                for msg in messages:
                    if isinstance(msg, dict) and 'content' in msg:
                        all_text += msg.get('content', '') + " "
            except:
                pass
    
    if "партнёр" in all_text.lower() or "инвестор" in all_text.lower():
        suggestions.append("В ваших диалогах часто упоминается поиск партнёров. Продолжайте общаться, чтобы получить более точные рекомендации.")
    
    if not suggestions:
        suggestions.append("Ваш профиль активен. Продолжайте общаться с ИИ, чтобы получать более точные рекомендации.")
    
    return {"suggestions": suggestions}

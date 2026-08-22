import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import Profile, Dialogue, User
from ..database import SessionLocal

class AgentScanner:
    """Сканер для анализа профилей пользователей и диалогов"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def scan_profile(self, user_id: int) -> Dict[str, Any]:
        """Сканирует профиль пользователя и возвращает анализ"""
        profile = self.db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return {"error": "Profile not found"}
        
        return {
            "user_id": user_id,
            "topics": json.loads(profile.topics) if profile.topics else [],
            "summary": profile.summary,
            "entities": json.loads(profile.entities) if profile.entities else [],
            "intentions": json.loads(profile.intentions) if profile.intentions else []
        }
    
    def scan_dialogues(self, user_id: int) -> List[Dict[str, Any]]:
        """Сканирует диалоги пользователя"""
        dialogues = self.db.query(Dialogue).filter(Dialogue.user_id == user_id).all()
        result = []
        for dialogue in dialogues:
            result.append({
                "id": dialogue.id,
                "title": dialogue.title,
                "messages": json.loads(dialogue.messages) if dialogue.messages else []
            })
        return result
    
    def get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Получает полный контекст пользователя"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        profile_data = self.scan_profile(user_id)
        dialogues = self.scan_dialogues(user_id)
        
        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name
            },
            "profile": profile_data,
            "dialogues": dialogues
        }

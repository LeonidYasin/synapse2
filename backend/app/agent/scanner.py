import json
import datetime
from collections import Counter
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Profile, Dialogue
from ..utils.llm_client import call_deepseek

class AgentScanner:
    """
    Агент-сканер для анализа диалогов и построения профиля пользователя.
    Использует LLM для извлечения сущностей, эмоций, намерений и тем.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = SessionLocal()
        
    def get_dialogues(self) -> List[Dict]:
        """Получает все диалоги пользователя из БД"""
        dialogues = self.db.query(Dialogue).filter(
            Dialogue.user_id == self.user_id
        ).order_by(Dialogue.timestamp).all()
        return [{"role": d.role, "content": d.content} for d in dialogues]
    
    async def analyze_with_llm(self, dialogues: List[Dict]) -> Dict[str, Any]:
        """
        Анализирует диалоги с помощью LLM и возвращает структурированный профиль.
        """
        if not dialogues:
            return {"topics": [], "summary": "Нет диалогов для анализа", "entities": [], "intentions": []}
        
        # Формируем текст для анализа
        full_text = "\n".join([f"{d['role']}: {d['content']}" for d in dialogues[-20:]])
        
        prompt = f"""
        Проанализируй следующие диалоги пользователя. Извлеки:
        1. Ключевые темы (5-7 тем, которые чаще всего обсуждаются)
        2. Сущности (люди, компании, технологии, проекты)
        3. Намерения (что хочет пользователь: найти партнёра, инвестора, продать продукт, найти решение проблемы)
        4. Краткое резюме (2-3 предложения о том, кто этот пользователь и что его интересует)
        
        Диалоги:
        {full_text}
        
        Ответь в формате JSON:
        {{
            "topics": ["тема1", "тема2", ...],
            "entities": ["сущность1", "сущность2", ...],
            "intentions": ["намерение1", "намерение2", ...],
            "summary": "краткое резюме"
        }}
        """
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await call_deepseek(
                messages=messages,
                model="deepseek-chat",
                temperature=0.3,
                max_tokens=500
            )
            
            # Парсим JSON из ответа
            content = response.get("content", "{}")
            # Ищем JSON в ответе
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Если JSON не найден, используем простой анализ
                return self._simple_analysis(dialogues)
        except Exception as e:
            print(f"LLM analysis error: {e}")
            return self._simple_analysis(dialogues)
    
    def _simple_analysis(self, dialogues: List[Dict]) -> Dict[str, Any]:
        """Простой анализ без LLM (запасной вариант)"""
        full_text = " ".join([d["content"] for d in dialogues])
        words = full_text.split()
        counter = Counter(words)
        top_topics = [word for word, _ in counter.most_common(5) if len(word) > 3]
        
        return {
            "topics": top_topics,
            "entities": [],
            "intentions": [],
            "summary": f"Основные темы диалогов: {', '.join(top_topics)}"
        }
    
    async def scan_and_update_profile(self) -> Dict[str, Any]:
        """
        Основной метод: сканирует диалоги, обновляет профиль пользователя.
        """
        dialogues = self.get_dialogues()
        if not dialogues:
            return {"status": "no_dialogues", "message": "Диалоги не найдены"}
        
        # Анализируем диалоги
        analysis = await self.analyze_with_llm(dialogues)
        
        # Сохраняем профиль
        profile = Profile(
            user_id=self.user_id,
            topics=json.dumps(analysis.get("topics", [])),
            summary=analysis.get("summary", ""),
            updated_at=datetime.datetime.utcnow()
        )
        self.db.merge(profile)
        self.db.commit()
        
        # Сохраняем также дополнительные данные (можно расширить)
        # Здесь можно добавить сохранение entities и intentions в отдельные таблицы
        
        self.db.close()
        
        return {
            "status": "success",
            "topics": analysis.get("topics", []),
            "entities": analysis.get("entities", []),
            "intentions": analysis.get("intentions", []),
            "summary": analysis.get("summary", "")
        }
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

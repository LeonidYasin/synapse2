from fastapi import APIRouter, HTTPException
from ..models import ProfileRequest
from ..database import SessionLocal, Profile
import json
import datetime
from collections import Counter

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/analyze")
async def analyze(request: ProfileRequest):
    full_text = " ".join([msg.content for msg in request.messages])
    words = full_text.split()
    counter = Counter(words)
    top_topics = [word for word, _ in counter.most_common(5)]
    
    db = SessionLocal()
    profile = Profile(
        user_id=request.user_id,
        topics=json.dumps(top_topics),
        summary=f"Анализ на {datetime.datetime.now()}: основные темы - {', '.join(top_topics)}",
        updated_at=datetime.datetime.utcnow()
    )
    db.merge(profile)
    db.commit()
    db.close()
    
    return {
        "user_id": request.user_id,
        "topics": top_topics,
        "summary": profile.summary
    }

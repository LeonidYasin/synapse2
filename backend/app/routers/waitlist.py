from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, String, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from ..config import Config

router = APIRouter(prefix="/waitlist", tags=["waitlist"])

# Используем ту же базу данных, что и в основном приложении
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class WaitlistEntry(Base):
    __tablename__ = "waitlist"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class WaitlistRequest(BaseModel):
    email: EmailStr

@router.post("/subscribe")
async def subscribe_to_waitlist(request: WaitlistRequest):
    """
    Сохраняет email в лист ожидания.
    """
    db = SessionLocal()
    # Проверяем, есть ли уже такой email
    existing = db.query(WaitlistEntry).filter(WaitlistEntry.email == request.email).first()
    if existing:
        db.close()
        return {"message": "Этот email уже в списке ожидания", "status": "already_exists"}
    
    # Сохраняем новый email
    entry = WaitlistEntry(email=request.email)
    db.add(entry)
    db.commit()
    db.close()
    
    return {"message": "Спасибо! Вы добавлены в лист ожидания.", "status": "success"}

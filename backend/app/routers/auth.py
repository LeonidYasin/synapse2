from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr, Field
import json

from ..database import SessionLocal
from ..models import User
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user, authenticate_user
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=4, max_length=72)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

@router.post("/register")
async def register(request: Request, db: Session = Depends(SessionLocal)):
    # Отладочный вывод
    body = await request.body()
    print(f"[DEBUG] Raw body: {body}")
    try:
        data = json.loads(body)
        print(f"[DEBUG] Parsed data: {data}")
    except:
        print(f"[DEBUG] Failed to parse JSON")
    
    # Ручная валидация
    try:
        user_data = await request.json()
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON"
        )
    
    username = user_data.get("username", "").strip()
    email = user_data.get("email", "").strip()
    password = user_data.get("password", "")
    
    if not username or len(username) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 2 characters"
        )
    if not email or "@" not in email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid email is required"
        )
    if not password or len(password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 4 characters"
        )
    
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        # Если пользователь уже существует, проверяем пароль и выдаём токен
        if verify_password(password, existing_user.hashed_password):
            access_token = create_access_token(
                data={"sub": existing_user.username}
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "message": "Welcome back!"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered with different password"
            )
    
    # Создаём нового пользователя
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Выдаём токен
    access_token = create_access_token(
        data={"sub": db_user.username}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Registration successful"
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionLocal)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email
    )

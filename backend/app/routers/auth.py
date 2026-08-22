from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr, validator

from ..database import SessionLocal
from ..models import User
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user, authenticate_user
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# Простая модель для регистрации
class RegisterUser(BaseModel):
    username: str
    email: str
    password: str
    
    @validator('username')
    def username_not_empty(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Username must be at least 2 characters')
        return v.strip()
    
    @validator('email')
    def email_valid(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email')
        return v.strip()
    
    @validator('password')
    def password_not_empty(cls, v):
        if not v or len(v) < 4:
            raise ValueError('Password must be at least 4 characters')
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

@router.post("/register")
def register(user: RegisterUser, db: Session = Depends(SessionLocal)):
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        # Если пользователь уже существует, проверяем пароль и выдаём токен
        if verify_password(user.password, existing_user.hashed_password):
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
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
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

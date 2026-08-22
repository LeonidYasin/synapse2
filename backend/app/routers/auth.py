import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr, Field

from ..database import SessionLocal
from ..models import User
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user, authenticate_user
from ..config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
def register(user: UserRegister, db: Session = Depends(SessionLocal)):
    logger.info(f"=== REGISTRATION START ===")
    logger.info(f"Username: {user.username}")
    logger.info(f"Email: {user.email}")
    logger.info(f"Password length: {len(user.password)}")
    
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        logger.info(f"User exists: {existing_user.username} (id={existing_user.id})")
        # Если пользователь уже существует, проверяем пароль и выдаём токен
        if verify_password(user.password, existing_user.hashed_password):
            logger.info("Password correct, logging in existing user")
            access_token = create_access_token(
                data={"sub": existing_user.username}
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "message": "Welcome back!"
            }
        else:
            logger.warning("Password incorrect for existing user")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered with different password"
            )
    
    # Создаём нового пользователя
    logger.info("Creating new user...")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created with id={db_user.id}")
    
    # Выдаём токен
    access_token = create_access_token(
        data={"sub": db_user.username}
    )
    logger.info("=== REGISTRATION SUCCESS ===")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Registration successful"
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionLocal)):
    logger.info(f"=== LOGIN START ===")
    logger.info(f"Username: {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning("Login failed: invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Login successful for user: {user.username} (id={user.id})")
    access_token = create_access_token(
        data={"sub": user.username}
    )
    logger.info("=== LOGIN SUCCESS ===")
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    logger.info(f"=== GET /me ===")
    logger.info(f"Current user: {current_user.username} (id={current_user.id})")
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email
    )

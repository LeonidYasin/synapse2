from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
import json

from ..database import SessionLocal
from ..models import User
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user, authenticate_user
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

def log(msg):
    print(f"[AUTH] {msg}")

# ПРОСТЕЙШИЙ ТЕСТОВЫЙ ЭНДПОИНТ
@router.post("/test")
def test_endpoint(request: Request):
    log("=" * 50)
    log("TEST ENDPOINT CALLED")
    log("=" * 50)
    return {"status": "ok", "method": "POST", "path": "/auth/test"}

# ЭНДПОИНТ РЕГИСТРАЦИИ - НОВОЕ ИМЯ
@router.post("/register2")
def register2(request: Request, db: Session = Depends(SessionLocal)):
    log("=" * 50)
    log("REGISTER2 ENDPOINT CALLED (new name)")
    
    # Получаем тело запроса
    body = request._body
    log(f"Raw body: {body}")
    
    if not body:
        log("Empty body")
        raise HTTPException(status_code=400, detail="Empty body")
    
    try:
        data = json.loads(body.decode('utf-8'))
        log(f"Parsed data: {data}")
    except Exception as e:
        log(f"JSON parse error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not username or not email or not password:
        log("Missing required fields")
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    log(f"Username: {username}")
    log(f"Email: {email}")
    log(f"Password length: {len(password)}")
    
    # Проверяем существующего пользователя
    log("Checking if user exists...")
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        log(f"User exists: {existing_user.username} (id={existing_user.id})")
        if verify_password(password, existing_user.hashed_password):
            log("Password correct, logging in existing user")
            access_token = create_access_token(data={"sub": existing_user.username})
            log("=" * 50)
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "message": "Welcome back!"
            }
        else:
            log("Password incorrect")
            log("=" * 50)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered with different password"
            )
    
    # Создаём нового пользователя
    log("Creating new user...")
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    log(f"User created with id={db_user.id}")
    
    access_token = create_access_token(data={"sub": db_user.username})
    log("=" * 50)
    log("REGISTER2 SUCCESS")
    log("=" * 50)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Registration successful"
    }

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(SessionLocal)):
    log("=" * 50)
    log("LOGIN ENDPOINT CALLED")
    log(f"Username: {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        log("Login failed: invalid credentials")
        log("=" * 50)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    log(f"Login successful for user: {user.username} (id={user.id})")
    access_token = create_access_token(
        data={"sub": user.username}
    )
    log("=" * 50)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    log("=" * 50)
    log("GET /me CALLED")
    log(f"Current user: {current_user.username} (id={current_user.id})")
    log("=" * 50)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import json

from ..database import SessionLocal
from ..models import User
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user, authenticate_user
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

def log(msg):
    print(f"[AUTH] {msg}")

# Прямой эндпоинт без Pydantic - принимает raw JSON
@router.post("/register")
async def register_raw(request: Request, db: Session = Depends(SessionLocal)):
    log("=" * 50)
    log("REGISTER RAW ENDPOINT CALLED")
    
    try:
        body = await request.body()
        log(f"Raw body (bytes): {body}")
        log(f"Raw body (hex): {body.hex()}")
        
        # Пробуем декодировать как UTF-8
        try:
            text = body.decode('utf-8')
            log(f"Decoded as UTF-8: {text}")
        except UnicodeDecodeError as e:
            log(f"UTF-8 decode error: {e}")
            # Пробуем другие кодировки
            for encoding in ['cp1251', 'latin-1', 'cp866']:
                try:
                    text = body.decode(encoding)
                    log(f"Decoded as {encoding}: {text}")
                except:
                    pass
        
        # Парсим JSON
        try:
            data = json.loads(body)
            log(f"Parsed JSON: {data}")
            log(f"Keys: {list(data.keys())}")
            log(f"Username: {data.get('username')}")
            log(f"Email: {data.get('email')}")
            log(f"Password: {data.get('password')}")
            log(f"Password type: {type(data.get('password'))}")
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            
            if not username or not email or not password:
                log("Missing required fields")
                raise HTTPException(status_code=400, detail="Missing required fields")
            
            # Проверяем, существует ли пользователь
            log("Checking if user exists...")
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                log(f"User exists: {existing_user.username} (id={existing_user.id})")
                if verify_password(password, existing_user.hashed_password):
                    log("Password correct, logging in existing user")
                    access_token = create_access_token(
                        data={"sub": existing_user.username}
                    )
                    log("=" * 50)
                    return {
                        "access_token": access_token,
                        "token_type": "bearer",
                        "message": "Welcome back!"
                    }
                else:
                    log("Password incorrect")
                    raise HTTPException(status_code=400, detail="Invalid password")
            
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
            
            access_token = create_access_token(
                data={"sub": db_user.username}
            )
            log("=" * 50)
            log("REGISTER SUCCESS")
            log("=" * 50)
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "message": "Registration successful"
            }
            
        except json.JSONDecodeError as e:
            log(f"JSON decode error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
            
    except Exception as e:
        log(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

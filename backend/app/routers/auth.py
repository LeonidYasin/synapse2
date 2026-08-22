# VERSION: 2026-08-22-v7-TEST-NEW-ENDPOINT

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import json

from ..database import SessionLocal
from ..models import User
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user, authenticate_user
from ..config import settings

print("=" * 60)
print("[AUTH] ROUTER LOADED - VERSION: 2026-08-22-v7-TEST-NEW-ENDPOINT")
print("=" * 60)

router = APIRouter(prefix="/auth", tags=["auth"])

def log(msg):
    print(f"[AUTH] {msg}", flush=True)

# НОВЫЙ ТЕСТОВЫЙ ЭНДПОИНТ - /auth/register2
@router.post("/register2")
async def register2(request: Request):
    log("=" * 50)
    log("REGISTER2 ENDPOINT CALLED - TEST")
    body = await request.body()
    log(f"Raw body: {body}")
    try:
        decoded = body.decode('utf-8')
        log(f"Decoded: {decoded}")
        data = json.loads(decoded)
        log(f"Parsed: {data}")
        log("=" * 50)
        return {"status": "ok", "data": data, "endpoint": "/auth/register2"}
    except Exception as e:
        log(f"Error: {e}")
        log("=" * 50)
        return {"status": "error", "error": str(e)}

# Оригинальный /auth/register - копия register2
@router.post("/register")
async def register(request: Request, db: Session = Depends(SessionLocal)):
    log("=" * 50)
    log("REGISTER ENDPOINT CALLED (v7)")
    body = await request.body()
    log(f"Raw body: {body}")
    try:
        decoded = body.decode('utf-8')
        log(f"Decoded: {decoded}")
        data = json.loads(decoded)
        log(f"Parsed: {data}")
        
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        log(f"Username: {username}")
        log(f"Email: {email}")
        log(f"Password length: {len(password)}")
        
        if not username or len(username) < 2:
            raise HTTPException(status_code=400, detail="Username must be at least 2 characters")
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="Invalid email")
        if not password or len(password) < 4:
            raise HTTPException(status_code=400, detail="Password must be at least 4 characters")
        
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            log(f"User exists: {existing_user.username}")
            if verify_password(password, existing_user.hashed_password):
                log("Password correct, logging in")
                access_token = create_access_token(data={"sub": existing_user.username})
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "message": "Welcome back!"
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Username or email already registered with different password"
                )
        
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
        log("REGISTER SUCCESS")
        log("=" * 50)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "message": "Registration successful"
        }
        
    except json.JSONDecodeError as e:
        log(f"JSON decode error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    except HTTPException:
        raise
    except Exception as e:
        log(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Остальные эндпоинты...
@router.post("/test-raw")
async def test_raw(request: Request):
    log("=" * 50)
    log("TEST-RAW ENDPOINT CALLED")
    body = await request.body()
    log(f"Raw body: {body}")
    try:
        decoded = body.decode('utf-8')
        log(f"Decoded: {decoded}")
        data = json.loads(decoded)
        log(f"Parsed: {data}")
        log("=" * 50)
        return {"status": "ok", "data": data}
    except Exception as e:
        log(f"Error: {e}")
        log("=" * 50)
        return {"status": "error", "error": str(e), "body": body.decode('utf-8', errors='replace')}

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

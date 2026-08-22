from fastapi import APIRouter, Depends, HTTPException
from ..models import ChatRequest, ChatResponse, User
from ..utils.llm_client import call_deepseek
from ..database import SessionLocal
from ..auth import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """
    Отправляет сообщение в чат с ИИ и сохраняет диалог в БД.
    Требуется аутентификация.
    """
    try:
        messages = [msg.dict() for msg in request.messages]
        system_prompt = {
            "role": "system",
            "content": "Ты — ИИ-ассистент Синапс. Ты помогаешь пользователю развивать идеи, находить партнёров и инвесторов. Отвечай полезно, структурированно, но дружелюбно."
        }
        full_messages = [system_prompt] + messages
        
        response = await call_deepseek(
            messages=full_messages,
            api_key=request.api_key,
            model=request.model
        )
        
        # TODO: сохранять диалог в БД позже
        # для сейчас просто возвращаем ответ
        return ChatResponse(role=response["role"], content=response["content"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/public")
async def chat_public(request: ChatRequest):
    """
    Публичный чат без аутентификации (для демо).
    Диалоги не сохраняются.
    """
    try:
        messages = [msg.dict() for msg in request.messages]
        system_prompt = {
            "role": "system",
            "content": "Ты — ИИ-ассистент Синапс. Ты помогаешь пользователю развивать идеи, находить партнёров и инвесторов. Отвечай полезно, структурированно, но дружелюбно."
        }
        full_messages = [system_prompt] + messages
        
        response = await call_deepseek(
            messages=full_messages,
            api_key=request.api_key,
            model=request.model
        )
        
        return ChatResponse(role=response["role"], content=response["content"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

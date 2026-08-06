from fastapi import APIRouter, HTTPException
from ..models import ChatRequest, ChatResponse
from ..utils.llm_client import call_deepseek

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
async def chat(request: ChatRequest):
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

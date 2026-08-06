from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    api_key: Optional[str] = None
    model: str = "deepseek-chat"

class ChatResponse(BaseModel):
    role: str
    content: str

class ProfileRequest(BaseModel):
    user_id: str
    messages: List[Message]

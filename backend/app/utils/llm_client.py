import httpx
from ..config import Config

async def call_deepseek(
    messages: list,
    api_key: str = None,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 1000
):
    headers = {
        "Authorization": f"Bearer {api_key or Config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{Config.DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]

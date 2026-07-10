from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.core.config import settings
from app.schemas.chat import ChatRequest
import httpx

print("新版 ai.py 已加载（Pydantic 版本）")

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": request.prompt}],
                "stream": False
            },
            timeout=30.0
        )
        return response.json()
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.core.config import settings
from app.schemas.chat import ChatRequest
import httpx
import json
import asyncio

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key not configured")

    TIMEOUT = 25

    async def generate():
        try:
            # RAG 上下文构造（可保留模拟 sources）
            sources = []
            if request.return_sources:
                sources = [
                    {"source": "docs/fastapi_intro.md", "content_preview": "FastAPI 是一个现代 Python Web 框架...", "score": 0.87},
                    {"source": "docs/rag_overview.md", "content_preview": "RAG 通过检索外部知识库增强大模型回答...", "score": 0.76}
                ]
                context = "\n".join([s["content_preview"] for s in sources])
                final_prompt = f"基于以下文档回答问题：\n{context}\n\n问题：{request.prompt}"
            else:
                final_prompt = request.prompt

            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                async with client.stream(
                    "POST",
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": final_prompt}],
                        "stream": True
                    }
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    yield f"data: {json.dumps({'content': content})}\n\n"
                            except json.JSONDecodeError:
                                continue
                    yield "data: [DONE]\n\n"

        except asyncio.TimeoutError:
            yield f"data: {json.dumps({'error': '请求超时，请稍后重试'})}\n\n"
        except httpx.HTTPStatusError as e:
            yield f"data: {json.dumps({'error': f'API错误: {e.response.status_code}'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': f'服务器内部错误: {str(e)}'})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
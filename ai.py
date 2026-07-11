from fastapi import APIRouter, Depends, HTTPException
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.core.config import settings
from app.schemas.chat import ChatRequest
import httpx

router = APIRouter()

@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    import traceback
    try:
        print('收到请求:',request)
        print('prompt:',request.prompt)
        print('return_sources:',request.return_sources)
        api_key = settings.DEEPSEEK_API_KEY
        if not api_key:
            raise HTTPException(status_code=500, detail="API Key not configured")

        # ---------- 模拟 RAG 检索（真实项目替换为向量库查询） ----------
        sources = []
        if request.return_sources:
            # 模拟检索到的文档片段（实际应查询 Chroma / Pgvector）
            sources = [
                {
                    "source": "docs/fastapi_intro.md",
                    "content_preview": "FastAPI 是一个现代 Python Web 框架，用于构建高效、可维护的 API。",
                    "score": 0.87
                },
                {
                    "source": "docs/rag_overview.md",
                    "content_preview": "RAG 通过检索外部知识库增强大模型回答，有效降低幻觉。",
                    "score": 0.76
                }
            ]

            # 构建上下文注入 Prompt
            context = "\n".join([s["content_preview"] for s in sources])
            final_prompt = f"基于以下文档回答问题：\n{context}\n\n问题：{request.prompt}"
        else:
            final_prompt = request.prompt

        # ---------- 调用 DeepSeek API ----------
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": final_prompt}],
                    "stream": False
                },
                timeout=30.0
            )
            result = response.json()
            answer = result["choices"][0]["message"]["content"]

        # ---------- 返回结构化结果 ----------
        return {
            "answer": answer,
            "sources": [
                {
                    "source": s["source"],
                    "content_preview": s["content_preview"],
                    "score": s["score"]
                }
                for s in sources
            ] if request.return_sources else None
        }
    except Exception as e:
        print("异常捕获:", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
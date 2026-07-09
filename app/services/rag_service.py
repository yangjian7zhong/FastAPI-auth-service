from rag.vector_store import query_documents
from rag.embedding import get_embedding
import httpx
from app.core.config import settings

async def ask_with_rag(question: str) -> dict:
    # 1. 检索相关文档[reference:15]
    retrieved_docs = query_documents(question, n_results=3)
    context = "\n---\n".join(retrieved_docs) if retrieved_docs else "未找到相关资料。"

    # 2. 构建 Prompt[reference:16]
    prompt = f"""你是一个知识库问答助手。请根据以下资料回答用户的问题。
如果资料中没有相关信息，请直接说"未找到相关资料"。

### 资料 ###
{context}

### 问题 ###
{question}

### 回答 ###"""

    # 3. 调用 DeepSeek 生成回答
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=60.0
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]

    return {
        "answer": answer,
        "sources": retrieved_docs,  # 返回引用来源
        "context_used": context
    }
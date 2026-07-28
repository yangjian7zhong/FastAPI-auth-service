import asyncio

import httpx

from app.core.config import settings
from rag.vector_store import query_documents


async def ask_with_rag(question: str, n_results: int = 3) -> dict:
    retrieved_docs = await asyncio.to_thread(query_documents, question, n_results)
    context = "\n---\n".join(retrieved_docs) if retrieved_docs else "未找到相关资料。"

    prompt = f"""你是一个知识库问答助手。请根据以下资料回答用户的问题。
如果资料中没有相关信息，请直接说"未找到相关资料"。

### 资料 ###
{context}

### 问题 ###
{question}

### 回答 ###"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-v4-pro",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]

    return {
        "answer": answer,
        "sources": retrieved_docs,
        "context_used": context,
    }
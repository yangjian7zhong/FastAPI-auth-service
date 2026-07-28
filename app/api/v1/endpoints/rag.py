import asyncio
import time
import os
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.endpoints.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.rag import RagAskRequest, RagRetrieveRequest
from app.services.rag_service import ask_with_rag
from rag.vector_store import query_documents

# 新增本地依赖
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings

router = APIRouter()

# ========== 鉴权逻辑（不变） ==========
async def rag_auth(
    authorization: str | None = Header(None, alias="Authorization"),
    user: User = Depends(get_current_user),
) -> User | None:
    bench = settings.RAG_BENCHMARK_TOKEN
    if bench and authorization:
        token = authorization[7:] if authorization.startswith("Bearer ") else authorization
        if token == bench:
            return None
    return user

# ========== 纯本地 RAG 检索（压测专用） ==========
@lru_cache()
def get_local_model():
    return SentenceTransformer('paraphrase-MiniLM-L3-v2')

# 使用独立路径，避免与现有 chroma_db 冲突
LOCAL_CHROMA_PATH = "./chroma_db_local"
os.makedirs(LOCAL_CHROMA_PATH, exist_ok=True)


_local_client = chromadb.PersistentClient(
    path=LOCAL_CHROMA_PATH,
)
_local_collection = _local_client.get_or_create_collection("local_docs")


@router.post("/rag/local_search")
async def local_rag_search(req: RagRetrieveRequest, _: User | None = Depends(rag_auth)):
    """纯本地检索：模型在内存，向量在本地 Chroma，无外部 API 调用。"""
    t0 = time.perf_counter()
    model = get_local_model()

    # 关键修复：将同步阻塞操作放入线程池
    def _blocking_task():
        embedding = model.encode(req.question).tolist()
        results = _local_collection.query(
            query_embeddings=[embedding],
            n_results=req.top_k
        )
        return results['documents'][0] if results['documents'] else []

    docs = await asyncio.to_thread(_blocking_task)

    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    return {
        "documents": docs,
        "top_k": req.top_k,
        "latency_ms": latency_ms,
        "note": "纯本地检索，无外部API"
    }

# ========== 原有接口（保持不变） ==========
@router.post("/rag/retrieve")
async def rag_retrieve(req: RagRetrieveRequest, _: User | None = Depends(rag_auth)):
    t0 = time.perf_counter()
    docs = await asyncio.to_thread(query_documents, req.question, req.top_k)
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
    return {
        "documents": docs,
        "top_k": req.top_k,
        "latency_ms": latency_ms,
    }

@router.post("/rag/ask")
async def rag_ask(req: RagAskRequest, _: User | None = Depends(rag_auth)):
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="DEEPSEEK_API_KEY not configured")
    t0 = time.perf_counter()
    result = await ask_with_rag(req.question, n_results=req.top_k)
    result["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return result





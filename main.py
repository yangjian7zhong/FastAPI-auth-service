from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import time
import logging

from app.api.v1.endpoints import auth, ai
from app.core.database import engine
from app.models.user import Base

# ---------- 日志配置 ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- 数据库初始化函数 ----------
async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表创建完成")

# ---------- 生命周期管理 ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("🚀 正在初始化数据库...")
    await init_db()
    print("✅ 数据库表初始化完成")
    yield
    # 关闭时执行（如果有需要清理的资源）
    print("🛑 应用关闭")

# ---------- 创建 FastAPI 实例 ----------
app = FastAPI(
    title="AI 应用后端",
    description="支持用户认证、AI对话、RAG检索",
    version="1.0.0",
    lifespan=lifespan
)

# ---------- 中间件：记录响应时间 ----------
@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} "
        f"耗时: {process_time:.2f}ms "
        f"状态码: {response.status_code}"
    )
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response

# ---------- 注册路由 ----------
app.include_router(auth.router, prefix="/api/v1", tags=["认证"])
app.include_router(ai.router, prefix="/api/v1", tags=["AI"])

# ---------- 根路径 ----------
@app.get("/")
async def root():
    return {"msg": "FastAPI 项目已启动", "docs": "/docs"}












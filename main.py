import sqlite3
import os
from fastapi import FastAPI, Request
import time
import logging
from contextlib import asynccontextmanager

from app.api.v1.endpoints import auth, ai
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import hash_password
from sqlalchemy import select
from app.core.redis_client import redis_client

# ---------- 同步建表（确保表存在） ----------
def ensure_db():
    db_path = os.path.join(os.path.dirname(__file__), "test.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("数据库表已确认（同步建表）")

ensure_db()

# ---------- 日志配置 ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- FastAPI 实例 ----------
app = FastAPI(
    title="AI 应用后端",
    description="""
##测试账号

| 用户名 | 密码 | 说明 |
|--------|------|------|
| `demo` | `demo123` | 演示账号（已激活） |

### 使用步骤
1. 调用 `POST /api/v1/login` 获取 `access_token`
2. 点击右上角 **Authorize** 按钮，输入 `Bearer <你的token>`
3. 调用任意带锁接口

### 注册与激活
- 注册接口 `POST /api/v1/register` 会返回 `activation_link`，复制链接到浏览器打开即可激活账号
""",
    version="1.0.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False,
        "clientId": "swagger",
        "appName": "AI 应用后端",
    }
)

# ---------- 启动事件：强制创建演示账号 ----------
@app.on_event("startup")
async def startup():
    # 创建 demo 用户（无论环境变量是否启用，都强制创建）
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == "demo"))
        user = result.scalar_one_or_none()
        if not user:
            demo_user = User(
                username="demo",
                email="demo@test.com",
                hashed_password=hash_password("demo123"),
                is_active=True
            )
            session.add(demo_user)
            await session.commit()
            logger.info("演示账号已强制创建: demo / demo123")
        else:
            logger.info("演示账号已存在: demo / demo123")
    await redis_client.connect()

# ---------- 中间件 ----------
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

# ---------- 路由 ----------
app.include_router(auth.router, prefix="/api/v1", tags=["认证"])
app.include_router(ai.router, prefix="/api/v1", tags=["AI"])

@app.get("/")
async def root():
    return {"msg": "FastAPI 项目已启动", "docs": "/docs"}












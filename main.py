from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import time
import logging

from app.api.v1.endpoints import auth, ai
from app.core.database import engine
from app.models.user import Base
from app.core.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" 正在初始化数据库...")
    await init_db()
    print(" 数据库表初始化完成")
    yield
    print(" 应用关闭")

app = FastAPI(
    title="AI 应用后端",
    description="""
## 测试账号

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
    lifespan=lifespan,
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False,
        "clientId": "swagger",
        "appName": "AI 应用后端",
    }
)

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

app.include_router(auth.router, prefix="/api/v1", tags=["认证"])
app.include_router(ai.router, prefix="/api/v1", tags=["AI"])

@app.get("/")
async def root():
    return {"msg": "FastAPI 项目已启动", "docs": "/docs"}












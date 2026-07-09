from fastapi import FastAPI,Request
from app.api.v1.endpoints import auth,ai
from fastapi.security import APIKeyHeader

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app:FastAPI):
    from app.core.database import init_db
    await init_db()
    print('数据库表初始化完成')
    yield




app=FastAPI(title='AI 应用后端',lifespan=lifespan)

import time
import logging

# 配置日志（如果还没配置的话）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    """记录每个请求的响应时间"""
    start_time = time.perf_counter()

    # 执行请求
    response = await call_next(request)

    # 计算耗时（毫秒）
    process_time = (time.perf_counter() - start_time) * 1000

    # 打印日志
    logger.info(
        f"{request.method} {request.url.path} "
        f"耗时: {process_time:.2f}ms "
        f"状态码: {response.status_code}"
    )

    # 可选：把耗时加到响应头里（方便前端/监控抓取）
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

    return response



# 添加 API Key 安全方案，让 Swagger 显示输入框
security_scheme = APIKeyHeader(name="Authorization", auto_error=False)



app.include_router(auth.router,prefix='/api/v1',tags=['认证'])

@app.get('/')
async def root():
    return {'msg':'FastAPI项目已启动','docs':'/docs'}

app.include_router(ai.router, prefix="/api/v1", tags=["AI"])


app.include_router(auth.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")












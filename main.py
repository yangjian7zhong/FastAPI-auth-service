from fastapi import FastAPI
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

# 添加 API Key 安全方案，让 Swagger 显示输入框
security_scheme = APIKeyHeader(name="Authorization", auto_error=False)



app.include_router(auth.router,prefix='/api/v1',tags=['认证'])

@app.get('/')
async def root():
    return {'msg':'FastAPI项目已启动','docs':'/docs'}

app.include_router(ai.router, prefix="/api/v1", tags=["AI"])


app.include_router(auth.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")












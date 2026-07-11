from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select
from app.models.user import Base, User
from app.core.config import settings
from app.core.security import hash_password
import logging

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """初始化数据库：建表 + 强制创建演示账号"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建完成")

    # 强制创建 demo 用户（忽略环境变量）
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == "demo")
        )
        existing = result.scalar_one_or_none()
        if not existing:
            demo_user = User(
                username="demo",
                email="demo@test.com",
                hashed_password=hash_password("demo123"),
                is_active=True
            )
            session.add(demo_user)
            await session.commit()
            logger.info("演示账号已创建: demo / demo123")
        else:
            logger.info("演示账号已存在: demo / demo123")





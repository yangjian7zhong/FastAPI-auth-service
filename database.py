from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.user import Base, User
from app.core.config import settings
from sqlalchemy import select
from app.core.security import hash_password

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """初始化数据库：建表 + 创建演示账号（如果启用）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print(" 数据库表创建完成")

    # 如果启用演示账号，创建 demo 用户
    if settings.ENABLE_DEMO_ACCOUNT:
        async with AsyncSessionLocal() as session:
            # 检查 demo 用户是否存在
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
                print(" 演示账号已创建: demo / demo123")
            else:
                print(" 演示账号已存在: demo / demo123")
    else:
        print("ℹ 演示账号未启用（ENABLE_DEMO_ACCOUNT=false）")







# app/services/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, BackgroundTasks
from datetime import timedelta
from fastapi import Depends
from app.core.database import get_db
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
import os

from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserRegister
from email_utils import send_activation_email

class UserService:
    # app/services/user.py
    @staticmethod
    async def register(user_data: UserRegister, db: AsyncSession, background_tasks: BackgroundTasks):
        # 🟢 如果 ENV=test，自动删除同名用户（防止重复注册报错）
        if settings.ENV == "test":
            existing = await db.execute(select(User).where(User.username == user_data.username))
            old_user = existing.scalar_one_or_none()
            if old_user:
                await db.delete(old_user)
                await db.commit()
                print(f"🧹 已清理旧用户: {old_user.username}")

            existing_email = await db.execute(select(User).where(User.email == user_data.email))
            old_user_by_email = existing_email.scalar_one_or_none()
            if old_user_by_email:
                await db.delete(old_user_by_email)
                await db.commit()
                print(f"🧹 已清理旧用户: {old_user_by_email.username}")

        # 原有注册逻辑（不变）
        existing = await db.execute(select(User).where(User.username == user_data.username))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="用户名已存在")

        existing_email = await db.execute(select(User).where(User.email == user_data.email))
        if existing_email.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="邮箱已被注册")

        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            is_active=False
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        token = create_access_token(
            data={"sub": new_user.username, "type": "activation"},
            expires_delta=timedelta(minutes=settings.ACTIVATION_TOKEN_EXPIRE_MINUTES)
        )
        background_tasks.add_task(send_activation_email, new_user.email, new_user.username, token)
        return new_user
    @staticmethod
    async def activate_account(token: str, db: AsyncSession):
        payload = decode_token(token)
        if payload.get("type") != "activation":
            raise HTTPException(status_code=400, detail="无效的激活链接")

        user = (await db.execute(select(User).where(User.username == payload.get("sub")))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        if user.is_active:
            return user

        user.is_active = True
        await db.commit()
        return user

    @staticmethod
    async def login(username: str, password: str, db: AsyncSession):
        user = (await db.execute(select(User).where(User.username == username))).scalar_one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="账号或密码错误")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="请先激活账号")

        access_token = create_access_token(data={"sub": user.username})
        return access_token

    @staticmethod
    async def get_current_user_by_token(token: str, db: AsyncSession):
        payload = decode_token(token)
        username = payload.get("sub")
        user = (await db.execute(select(User).where(User.username == username))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        return user


# 这是 FastAPI 依赖注入用的函数
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await UserService.get_current_user_by_token(token, db)



















































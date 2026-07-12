from fastapi import APIRouter, Depends, BackgroundTasks, Security, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import os

from app.core.database import get_db
from app.core.security import decode_token, create_access_token,verify_password
from app.core.config import settings
from app.schemas.user import UserRegister, UserResponse, UserLogin
from app.services.user import UserService
from app.models.user import User

api_key_scheme = APIKeyHeader(name='Authorization', auto_error=False)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


@router.post('/register')
async def register(
        user_data: UserRegister,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db)
):
    user = await UserService.register(user_data, db, background_tasks)

    activation_token = create_access_token(
        data={"sub": str(user.id), "type": "activation"},
        expires_delta=timedelta(minutes=settings.ACTIVATION_TOKEN_EXPIRE_MINUTES)
    )
    activation_link = f"{settings.BASE_URL}/api/v1/activate?token={activation_token}"

    print(f"注册成功，激活链接: {activation_link}")

    return {
        'msg': '注册成功！请点击下方链接激活账号（10分钟内有效）',
        'activation_link': activation_link,
        'user_id': user.id
    }


@router.get('/activate')
async def activate_account(
        token: str,
        db: AsyncSession = Depends(get_db)
):
    print(f"进入激活接口，token: {token[:20]}...")  # 打印前20字符防止刷屏

    payload = decode_token(token)
    print(f"解析后的 payload: {payload}")

    if payload.get("type") != "activation":
        raise HTTPException(status_code=400, detail="无效的激活链接")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=400, detail="无效的激活链接")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的激活链接")

    print(f"查询 user_id: {user_id}")

    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        print(f"用户不存在: id={user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.is_active:
        return {'msg': '账号已激活'}

    user.is_active = True
    await db.commit()
    print(f"用户激活成功: {user.username} (id={user.id})")
    return {'msg': '账号激活成功！'}


@router.post('/login')
async def login(
        login_data: UserLogin,
        db: AsyncSession = Depends(get_db)
):
    user = (await db.execute(select(User).where(User.username == login_data.username))).scalar_one_or_none()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="账号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="请先激活账号")

    access_token = create_access_token(data={"sub": str(user.id)})
    return {'access_token': access_token, 'token_type': 'bearer'}


async def get_current_user(
        token: str = Security(api_key_scheme),
        db: AsyncSession = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if token.startswith("Bearer "):
        token = token[7:]
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/users/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
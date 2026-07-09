from fastapi import APIRouter,Depends,BackgroundTasks
from fastapi.security import OAuth2PasswordBearer,APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Security,HTTPException,status
from sqlalchemy import select



from app.core.database import get_db
from app.core.security import decode_token
from app.schemas.user import UserRegister, UserResponse, UserLogin
from app.services.user import UserService
from app.models.user import User

api_key_scheme = APIKeyHeader(name='Authorization',auto_error=False)

router = APIRouter()
oauth2_scheme=OAuth2PasswordBearer(tokenUrl='login')

@router.post('/register')
async def register(
        user_data:UserRegister,
        background_tasks:BackgroundTasks,
        db:AsyncSession=Depends(get_db)
):
    user=await UserService.register(user_data,db,background_tasks)
    return {'msg':'注册成功，请查收激活邮件','user_id':user.id}

@router.get('/activate')
async def activate_account(
        token:str,
        db:AsyncSession=Depends(get_db)
):
    user=await UserService.activate_account(token,db)
    return {'msg':'账号激活成功！'if not user.is_active else'账号已激活'}

@router.post('/login')
async def login(
        login_data:UserLogin,
        db:AsyncSession=Depends(get_db)
):
    access_token=await UserService.login(
        login_data.username,login_data.password,db)
    return {'access_token':access_token,'token_type':'bearer'}


async def get_current_user(
        token: str = Security(api_key_scheme),
        db: AsyncSession = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if token.startswith("Bearer "):
        token = token[7:]
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/users/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

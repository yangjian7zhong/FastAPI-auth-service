from pydantic import BaseModel,EmailStr,Field

class UserRegister(BaseModel):
    username:str
    email:EmailStr
    password:str=Field(...,min_length=6,max_length=64)

class UserResponse(BaseModel):
    id:int
    username:str
    email:str
    is_active:bool

class Config:
    from_attributes = True

class UserLogin(BaseModel):
    username:str
    password:str
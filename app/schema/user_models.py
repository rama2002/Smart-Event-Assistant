from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_id: int  


class UserUpdate(BaseModel):
    username: str = None
    email: EmailStr = None
    password: str = None

class User(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    role_id: int


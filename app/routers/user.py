from typing import Optional
from fastapi import HTTPException, Depends, Body, Path,status,Security,APIRouter
from pydantic import EmailStr
from app.common.auth import ALGORITHM, SECRET_KEY
from app.database.user_db import create_user, get_user_by_username, update_user, get_user_by_email, authenticate_user
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.schema.user_models import User, UserCreate 
from zoneinfo import ZoneInfo 
from app.logging_config import get_logger
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
#from app.config import SECRET_KEY, ALGORITHM
logger = get_logger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(username=username)
    if user is None:
        raise credentials_exception
    return User(**user)

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_speaker_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_id != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_attendee_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role_id != 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(ZoneInfo("UTC")) + expires_delta
    else:
        expire = datetime.now(ZoneInfo("UTC")) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/users/", response_model=User, status_code=201)
async def create_user_endpoint(user: UserCreate,current_user: User = Security(get_current_admin_user)):
    new_user = create_user(user.username, user.email, user.password, user.role_id)
    if not new_user:
        raise HTTPException(status_code=400, detail="Could not create user.")
    data_dict = {
        "user_id": new_user[0],
        "username": new_user[1],
        "email": new_user[2],
        "role_id": new_user[3]  
    }
    return data_dict

@router.put("/users/{user_id}", response_model=User)
async def update_user_endpoint(
        user_id: int = Path(..., description="The ID of the user to update"),
        username: Optional[str] = Body(None, description="New username"),
        email: Optional[EmailStr] = Body(None, description="New email address"),
        password: Optional[str] = Body(None, description="New password"),
        current_user: User = Security(get_current_admin_user)):
    updated_user = update_user(user_id, username, email, password)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    data_dict = {
        "user_id": updated_user[0],
        "username": updated_user[1],
        "email": updated_user[2]
    }
    return data_dict


@router.get("/users/", response_model=User)
async def get_user_endpoint(email: EmailStr,current_user: User = Security(get_current_admin_user)):
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    data_dict = {
        "user_id": user[0],
        "username": user[1],
        "email": user[2]
    }
    return data_dict

@router.post("/token/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": user['username']})  
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me")
async def read_users_me(current_user: User = Security(get_current_admin_user)):
    del current_user["password_hash"]
    return current_user




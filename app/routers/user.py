from typing import Optional
from fastapi import HTTPException, Depends, Body, Path,status,Security,APIRouter
from pydantic import EmailStr
from app.common.auth import create_access_token, get_current_admin_user
from app.database.user_db import create_user, update_user, get_user_by_email, authenticate_user
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schema.user_models import User, UserCreate 
from app.logging_config import get_logger
from fastapi.security import OAuth2PasswordBearer


logger = get_logger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, current_user: User = Security(get_current_admin_user)):
    new_user = create_user(
        username=user.username,
        email=user.email,
        password=user.password,
        role_id=user.role_id
    )
    if not new_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create user.")
    return new_user

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




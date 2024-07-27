from config.config import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm
from utils import verify_password, Depends, get_user, HTTPException, status, create_access_token, timedelta, create_user, User
from fastapi import APIRouter
from models.models import Token

router = APIRouter()

# Authentication Endpoints

import logging

logger = logging.getLogger(__name__)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info("Attempting to authenticate user: %s", form_data.username)
    user = await get_user(form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        logger.warning("Authentication failed for user: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin},
        expires_delta=access_token_expires,
    )
    logger.info("User authenticated: %s", form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/register", response_model=User)
async def register_user(username: str, email: str, password: str, is_admin: bool = False):
    existing_user = await get_user(username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user_id = await create_user(username, email, password, is_admin)
    return {"id": str(user_id), "username": username, "email": email, "is_admin": is_admin}

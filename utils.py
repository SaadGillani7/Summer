from fastapi import HTTPException, Depends, status
from passlib.context import CryptContext
from typing import List, Optional
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta
from models.models import UserInDB,User,TokenData
from config.config import ALGORITHM,SECRET_KEY,oauth2_scheme
from Database.connection import users_collection


pwd_context = CryptContext(schemes=["bcrypt"])


# Verifies that a plain text password matches the hashed password.
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#Hashes the password
def get_password_hash(password):
    return pwd_context.hash(password)


#Fetches a user from the database
async def get_user(username: str):
    user = await users_collection.find_one({"username": username})
    if user:
        return UserInDB(**user)

#Creating user either admin or guest
async def create_user(username: str, email: str, password: str, is_admin: bool):
    hashed_password = get_password_hash(password)
    user = {"username": username, "email": email, "hashed_password": hashed_password, "is_admin": is_admin}
    result = await users_collection.insert_one(user)
    return result.inserted_id


# Functions to work with JWT tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


#Validation
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, is_admin=is_admin)
    except jwt.PyJWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


#checks for user
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

#checks for admin
async def get_current_active_admin(current_user: User = Depends(get_current_user)):
    if current_user is None or not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Admin required")
    return current_user

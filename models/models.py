from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Car(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # Mark as Optional and provide alias
    make: str
    model: str
    year: int
    price: float

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

class Bike(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # Mark as Optional and provide alias
    make: str
    model: str
    year: int
    price: float

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

class Order(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # Mark as Optional and provide alias
    bike_id: str
    timestamp: datetime

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True


class UserBase(BaseModel):
    username: str
    email: str
    is_admin: bool

class User(UserBase):
    id: str

class UserInDB(UserBase):
    hashed_password: str
    orders: Optional[List[Order]] = []

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    is_admin: bool

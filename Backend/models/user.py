# /models/user.py
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str
    income: float
    expenses: float
    investment_goals: str
    risk_tolerance: Optional[str] = "medium"

class UserInDB(UserBase):
    id: str
    hashed_password: str
    user_id: str
    income: float
    expenses: float
    investment_goals: str
    risk_tolerance: str

class User(UserBase):
    id: str
    user_id: str

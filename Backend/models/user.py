from pydantic import BaseModel, EmailStr
from typing import List, Tuple, Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str
    income: float
    expenses: float
    investment_goals: str
    risk_tolerance: str = "medium"

class UserInDB(UserBase):
    id: str
    hashed_password: str
    income: float
    expenses: float
    investment_goals: str
    risk_tolerance: str
    chat_history: List[Tuple[str, str]] 

class User(UserBase):
    id: str
    income: float
    expenses: float
    investment_goals: str
    risk_tolerance: str
    chat_history: List[Tuple[str, str]]
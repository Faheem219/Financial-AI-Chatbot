from pydantic import BaseModel, EmailStr
from typing import List, Tuple

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
    chat_history: List[Tuple[str, str]]  # Add chat history here (list of tuples with prompt and response)

class User(UserBase):
    id: str
    chat_history: List[Tuple[str, str]]  # Add chat history here too

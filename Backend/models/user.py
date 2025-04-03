from pydantic import BaseModel, EmailStr
from typing import List, Tuple

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str
    chat_history: List[Tuple[str, str]]  # Add chat history here (list of tuples with prompt and response)

class User(UserBase):
    id: str
    chat_history: List[Tuple[str, str]]  # Add chat history here too
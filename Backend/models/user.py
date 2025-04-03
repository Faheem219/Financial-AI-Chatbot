from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str
    password: str  # Store password as a plain text field

class UserCreate(UserBase):
    pass  # No changes here, just use the password field

class UserInDB(UserBase):
    id: str

class User(UserBase):
    id: str

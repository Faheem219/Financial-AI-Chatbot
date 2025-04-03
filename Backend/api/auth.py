# /api/auth.py
from fastapi import APIRouter, HTTPException, Depends
from models.user import UserCreate, User, UserInDB
from core.security import get_password_hash, verify_password, create_access_token
from db.database import get_database
from pymongo.errors import DuplicateKeyError
from fastapi.security import OAuth2PasswordRequestForm
from uuid import uuid4

router = APIRouter()

@router.post("/signup", response_model=User)
async def signup(user: UserCreate, db = Depends(get_database)):
    user_collection = db.users
    user_id = str(uuid4())  # Generate a unique user ID
    
    hashed_password = get_password_hash(user.password)
    
    # Create a new user with the provided fields and additional financial info
    user_data = user.dict()
    user_data["user_id"] = user_id
    user_data["hashed_password"] = hashed_password
    user_data["income"] = user.income
    user_data["expenses"] = user.expenses
    user_data["investment_goals"] = user.investment_goals
    user_data["risk_tolerance"] = user.risk_tolerance or "medium"
    
    try:
        result = await user_collection.insert_one(user_data)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")

    created_user = UserInDB(
        id=str(result.inserted_id),
        user_id=user_id,
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        income=user.income,
        expenses=user.expenses,
        investment_goals=user.investment_goals,
        risk_tolerance=user.risk_tolerance
    )
    
    return User(
        id=created_user.id,
        user_id=created_user.user_id,
        email=created_user.email,
        username=created_user.username
    )

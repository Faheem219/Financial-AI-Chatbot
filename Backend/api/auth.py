from fastapi import APIRouter, HTTPException, Depends
from models.user import UserCreate, User, UserInDB
from core.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from db.database import get_database
from pymongo.errors import DuplicateKeyError
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter()

@router.post("/signup", response_model=User)
async def signup(user: UserCreate, db = Depends(get_database)):
    user_collection = db.users
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data["hashed_password"] = hashed_password
    try:
        result = await user_collection.insert_one(user_data)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create the UserInDB object and pass the required fields, including income, expenses, etc.
    created_user = UserInDB(
        id=str(result.inserted_id),
        email=user.email,
        username=user.username,
        income=user.income,
        expenses=user.expenses,
        investment_goals=user.investment_goals,
        risk_tolerance=user.risk_tolerance,
        hashed_password=hashed_password,
        chat_history=[]  # Initialize chat history as an empty list
    )

    # Return the User object with all required fields
    return User(
        id=created_user.id,
        email=created_user.email,
        username=created_user.username,
        income=created_user.income,
        expenses=created_user.expenses,
        investment_goals=created_user.investment_goals,
        risk_tolerance=created_user.risk_tolerance,
        chat_history=created_user.chat_history
    )

# /api/auth.py
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_database)):
    user_collection = db.users
    user_data = await user_collection.find_one({"email": form_data.username})
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(form_data.password, user_data["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["email"]},
        expires_delta=access_token_expires
    )

    # Include user object in the response
    user_dict = {
        "id": str(user_data["_id"]),
        "email": user_data["email"],
        "username": user_data["username"],
        "income": user_data["income"],
        "expenses": user_data["expenses"],
        "investment_goals": user_data["investment_goals"],
        "risk_tolerance": user_data["risk_tolerance"],
        "chat_history": user_data.get("chat_history", [])
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }
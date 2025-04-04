# Backend/api/auth.py
from fastapi import APIRouter, HTTPException, Depends
from models.user import UserCreate, User, UserInDB
from core.security import get_password_hash, verify_password
from db.database import get_database
from pymongo.errors import DuplicateKeyError
from fastapi import Body

router = APIRouter()

@router.post("/signup", response_model=User)
async def signup(user: UserCreate, db = Depends(get_database)):
    user_collection = db.users
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data["hashed_password"] = hashed_password
    user_data["chat_history"] = []
    try:
        result = await user_collection.insert_one(user_data)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")
    
    created_user = UserInDB(
        id=str(result.inserted_id),
        email=user.email,
        username=user.username,
        income=user.income,
        expenses=user.expenses,
        investment_goals=user.investment_goals,
        risk_tolerance=user.risk_tolerance,
        hashed_password=hashed_password,
        chat_history=[]
    )

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

@router.post("/login")
async def login(email: str = Body(...), password: str = Body(...), db = Depends(get_database)):
    user_collection = db.users
    user_data = await user_collection.find_one({"email": email})
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(password, user_data["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    user_data["id"] = str(user_data["_id"])
    if "chat_history" not in user_data:
        user_data["chat_history"] = []
    
    return {
        "email": user_data["email"],
        "username": user_data["username"],
        "income": user_data.get("income", 0),
        "expenses": user_data.get("expenses", 0),
        "investment_goals": user_data.get("investment_goals", ""),
        "risk_tolerance": user_data.get("risk_tolerance", "medium"),
        "chat_history": user_data["chat_history"]
    }

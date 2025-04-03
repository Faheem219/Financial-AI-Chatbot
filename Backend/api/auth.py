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
    created_user = UserInDB(
        id=str(result.inserted_id),
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    return User(id=created_user.id, email=created_user.email, username=created_user.username)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_database)):
    user_collection = db.users
    user_data = await user_collection.find_one({"email": form_data.username})
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(form_data.password, user_data["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["email"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
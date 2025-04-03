from fastapi import APIRouter, HTTPException, Depends
from models.user import UserCreate, User, UserInDB
from db.database import get_database
from pymongo.errors import DuplicateKeyError
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/signup", response_model=User)
async def signup(user: UserCreate, db = Depends(get_database)):
    user_collection = db.users
    user_data = user.dict()  # No hashing, directly storing the password
    try:
        result = await user_collection.insert_one(user_data)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already exists")
    created_user = UserInDB(
        id=str(result.inserted_id),
        email=user.email,
        username=user.username,
        password=user.password  # Store the password as is
    )
    return User(id=created_user.id, email=created_user.email, username=created_user.username)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_database)):
    user_collection = db.users
    user_data = await user_collection.find_one({"email": form_data.username})
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if user_data["password"] != form_data.password:  # Check password directly without hashing
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": user_data["email"]},
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {"access_token": access_token, "token_type": "bearer"}

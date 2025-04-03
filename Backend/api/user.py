# /api/user.py
from fastapi import APIRouter, HTTPException, Depends
from db.database import get_database
from models.user import User
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_access_token
from pydantic import BaseModel

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class UserUpdateRequest(BaseModel):
    income: Optional[float] = None
    expenses: Optional[float] = None
    investment_goals: Optional[str] = None
    risk_tolerance: Optional[str] = None

@router.put("/update")
async def update_user_details(
    request_data: UserUpdateRequest,
    token: str = Depends(oauth2_scheme),
    db = Depends(get_database)
):
    """
    Update the user's financial details:
    - income
    - expenses
    - investment_goals
    - risk_tolerance
    """

    # Decode the token to get the user's email
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token or token expired")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token or token missing user info")

    user_collection = db.users
    user_data = await user_collection.find_one({"email": email})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # Build an update dictionary
    update_fields = {}
    if request_data.income is not None:
        update_fields["income"] = request_data.income
    if request_data.expenses is not None:
        update_fields["expenses"] = request_data.expenses
    if request_data.investment_goals is not None:
        update_fields["investment_goals"] = request_data.investment_goals
    if request_data.risk_tolerance is not None:
        update_fields["risk_tolerance"] = request_data.risk_tolerance

    # If we have fields to update, apply them
    if update_fields:
        await user_collection.update_one({"email": email}, {"$set": update_fields})

    # Fetch the updated user
    updated_user = await user_collection.find_one({"email": email})

    # Return the updated user data 
    # (Optionally, you can return a Pydantic model. Below is a direct JSON structure.)
    return {
        "id": str(updated_user["_id"]),
        "email": updated_user["email"],
        "username": updated_user["username"],
        "income": updated_user["income"],
        "expenses": updated_user["expenses"],
        "investment_goals": updated_user["investment_goals"],
        "risk_tolerance": updated_user["risk_tolerance"],
        "chat_history": updated_user.get("chat_history", []),
    }

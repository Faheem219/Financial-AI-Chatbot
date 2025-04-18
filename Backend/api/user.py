# Backend/api/user.py
from fastapi import APIRouter, HTTPException, Depends
from db.database import get_database
from models.user import User
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

class UserUpdateRequest(BaseModel):
    email: str
    income: Optional[float] = None
    expenses: Optional[float] = None
    investment_goals: Optional[str] = None
    risk_tolerance: Optional[str] = None

@router.put("/update")
async def update_user_details(
    request_data: UserUpdateRequest,
    db = Depends(get_database)
):
    email = request_data.email
    user_collection = db.users
    user_data = await user_collection.find_one({"email": email})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    update_fields = {}
    if request_data.income is not None:
        update_fields["income"] = request_data.income
    if request_data.expenses is not None:
        update_fields["expenses"] = request_data.expenses
    if request_data.investment_goals is not None:
        update_fields["investment_goals"] = request_data.investment_goals
    if request_data.risk_tolerance is not None:
        update_fields["risk_tolerance"] = request_data.risk_tolerance

    if update_fields:
        await user_collection.update_one({"email": email}, {"$set": update_fields})

    updated_user = await user_collection.find_one({"email": email})

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

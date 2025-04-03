from pydantic import BaseModel
from typing import Optional

class FinancialInfo(BaseModel):
    user_id: str
    income: float
    expenses: float
    investment_goals: str
    risk_tolerance: Optional[str] = "medium"
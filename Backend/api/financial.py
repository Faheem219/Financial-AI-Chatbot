import requests
from fastapi import APIRouter, HTTPException
from core.config import settings

router = APIRouter()

@router.get("/market-data")
async def get_market_data(symbol: str = "AAPL"):
    try:
        # Example: using Alpha Vantage free API for global quotes.
        api_url = (
            f"{settings.FINANCE_API_URL}/query?function=GLOBAL_QUOTE"
            f"&symbol={symbol}&apikey={settings.FINANCE_API_KEY}"
        )
        response = requests.get(api_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching market data")
        data = response.json()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
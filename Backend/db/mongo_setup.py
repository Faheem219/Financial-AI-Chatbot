import asyncio
from db.database import db

async def setup_indexes():
    # Ensure the users collection has a unique email index.
    await db.users.create_index("email", unique=True)
    # Create an index for financial info (if needed)
    await db.financial_info.create_index("user_id")

if __name__ == "__main__":
    asyncio.run(setup_indexes())
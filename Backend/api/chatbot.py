# /api/chatbot.py
from fastapi import APIRouter, HTTPException, Depends
from services.llm_service import process_prompt, process_document
from db.database import get_database
from models.user import UserInDB
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

# Dependency for getting the current user from the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user_from_token(token: str, db=Depends(get_database)):
    user_collection = db.users
    user_data = user_collection.find_one({"email": token})  # Or use a different way to decode the user from the token
    if not user_data:
        raise HTTPException(status_code=401, detail="User not found")
    return UserInDB(**user_data)

@router.post("/prompt")
async def chatbot_prompt(prompt: str, token: str = Depends(oauth2_scheme), db = Depends(get_database)):
    try:
        # Fetch the current user
        user = await get_current_user_from_token(token, db)

        # Fetch chat history
        chat_history = user.chat_history if user.chat_history else []

        # Process prompt with the history
        response = process_prompt(db, prompt)
        
        # Update the chat history in the database
        chat_history.append((prompt, response))
        db.users.update_one(
            {"email": user.email}, 
            {"$set": {"chat_history": chat_history}}
        )

        return {"result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/upload-pdf")
# async def upload_pdf(file: UploadFile = File(...), token: str = Depends(oauth2_scheme), db = Depends(get_database)):
#     try:
#         # Save the uploaded PDF temporarily
#         filename = f"temp_{uuid4().hex}.pdf"
#         with open(filename, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
        
#         # Process the PDF to update the vector database
#         process_document(filename)
        
#         # Clean up the temporary file
#         os.remove(filename)
#         return {"detail": "PDF processed successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
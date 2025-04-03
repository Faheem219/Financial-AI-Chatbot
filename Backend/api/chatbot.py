# Backend/api/chatbot.py
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from uuid import uuid4
import shutil
import os
from services.llm_service import process_prompt, process_document
from db.database import get_database
from models.user import UserInDB
from pydantic import BaseModel

router = APIRouter()

# Instead of token-based auth, we now simply expect an "email" field.
class PromptRequest(BaseModel):
    email: str
    prompt: str

async def get_user_by_email(email: str, db):
    user_collection = db.users
    user_data = await user_collection.find_one({"email": email})
    if not user_data:
        raise HTTPException(status_code=401, detail="User not found")
    # Convert _id to id and ensure chat_history exists.
    user_data["id"] = str(user_data["_id"])
    if "chat_history" not in user_data:
        user_data["chat_history"] = []
    return UserInDB(**user_data)

@router.post("/prompt")
async def chatbot_prompt(request: PromptRequest, db = Depends(get_database)):
    try:
        print("[DEBUG] chatbot_prompt: Received prompt:", request.prompt)
        user = await get_user_by_email(request.email, db)
        print("[DEBUG] chatbot_prompt: Fetched user:", user.email)

        if not request.prompt.strip():
            print("[DEBUG] chatbot_prompt: Empty prompt, returning chat history.")
            return {"history": user.chat_history or []}

        # Process the prompt
        response = await process_prompt(db, request.prompt)
        print("[DEBUG] chatbot_prompt: Received response:", response)

        chat_history = user.chat_history if user.chat_history else []
        chat_history.append((request.prompt, response))
        await db.users.update_one(
            {"email": user.email}, 
            {"$set": {"chat_history": chat_history}}
        )
        print("[DEBUG] chatbot_prompt: Updated chat history for user.")

        return {"result": response}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    email: str = Form(...),  # Use Form(...) to get the email from the form data
    db = Depends(get_database)
):
    try:
        # Save the uploaded PDF temporarily.
        filename = f"temp_{uuid4().hex}.pdf"
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the PDF to update the vector database.
        await process_document(filename, db)
        
        # Clean up the temporary file.
        os.remove(filename)
        return {"detail": "PDF processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import os
import shutil
from uuid import uuid4
from fastapi import APIRouter, HTTPException, UploadFile, File
from services.llm_service import process_prompt, process_document

router = APIRouter()

@router.post("/prompt")
async def chatbot_prompt(prompt: str):
    try:
        answer = process_prompt(prompt)
        return {"result": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded PDF temporarily
        filename = f"temp_{uuid4().hex}.pdf"
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # Process the PDF to update the vector database
        process_document(filename)
        # Clean up the temporary file
        os.remove(filename)
        return {"detail": "PDF processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
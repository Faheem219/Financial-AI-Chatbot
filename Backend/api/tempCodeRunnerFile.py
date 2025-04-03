@router.post("/upload-pdf")
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
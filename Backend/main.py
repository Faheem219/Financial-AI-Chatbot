from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, chatbot, financial
import uvicorn

app = FastAPI(title="AI-Powered Financial Advisory Chatbot API")

# Set up CORS middleware – adjust origins as necessary.
origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["chatbot"])
app.include_router(financial.router, prefix="/api/financial", tags=["financial"])

@app.get("/")
async def root():
    return {"message": "Welcome to the AI-Powered Financial Advisory Chatbot API"}

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
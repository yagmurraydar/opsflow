from fastapi import FastAPI

from app.routes.chat import router as chat_router

app = FastAPI(
    title = "Agentic DevOps Platform",
    description = " LLM- powered Agentic AI platform",
    version = "0.1.0",
    
    
)
app.include_router(chat_router, prefix = "/api")

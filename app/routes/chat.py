
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_service import generate_response

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = generate_response(request.message)
        return ChatResponse(answer=answer)

    except Exception:
        logger.exception("Chat isteği işlenemedi.")

        raise HTTPException(
            status_code=503,
            detail="AI servisi şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin.",
        )

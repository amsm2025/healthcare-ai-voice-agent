from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService

router = APIRouter(prefix="/api/v1", tags=["chat"])
service = LLMService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    reply, intent, safe_to_continue = await service.reply(request.message)
    return ChatResponse(
        reply=reply,
        intent=intent,
        safe_to_continue=safe_to_continue,
    )

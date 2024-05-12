from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.utils.azurechatbot import send

router = APIRouter()

class ChatInput(BaseModel):
    session_id: str
    input: str

@router.post("/chat/")
async def chat_with_bot(chat_input: ChatInput):
    result = send(chat_input.session_id, chat_input.input)
    return result

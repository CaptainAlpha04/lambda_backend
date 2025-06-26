from controller.mentorController import Mentor
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    userId: str
    message: str

@router.post("/mentor/chat")
async def chat_with_mentor(request: ChatRequest):
    try:
        mentor = Mentor(request.userId)
        response = mentor.chat_with_mentor(request.userId, request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
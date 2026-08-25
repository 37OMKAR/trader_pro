"""
Market AI — AI Market Tutor REST Endpoints
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
from fastapi import APIRouter
from services.market_tutor.tutor import MarketTutor

router = APIRouter(prefix="/tutor", tags=["AI Market Tutor"])

tutor = MarketTutor()


class QuestionRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None


@router.post("/ask")
async def ask_tutor(req: QuestionRequest):
    return await tutor.answer_question(req.question, req.chat_history)

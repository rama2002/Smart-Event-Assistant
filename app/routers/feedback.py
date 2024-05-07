from fastapi import APIRouter, HTTPException, Security
from app.common.auth import get_current_attendee_user, get_current_speaker_user
from app.schema.feedback_models import AnswerCreate, QuestionCreate
from app.schema.user_models import User
from app.database.feedback_db import add_question, add_answer, get_questions_by_event, get_questions_and_answers_by_event

router = APIRouter()

@router.post("/questions/")
async def post_question(question: QuestionCreate, current_user: User = Security(get_current_attendee_user)):
    result = add_question(question.event_id, current_user.user_id, question.question_text)
    if result:
        return result
    else:
        raise HTTPException(status_code=400, detail="Failed to post question")

@router.post("/answers/")
async def post_answer(answer: AnswerCreate, current_user: User = Security(get_current_speaker_user)):
    result = add_answer(answer.question_id, current_user.user_id, answer.answer_text)
    if result:
        return result
    else:
        raise HTTPException(status_code=400, detail="Failed to post answer")

@router.get("/events/{event_id}/questions/")
async def get_questions_for_event(event_id: int):
    result = get_questions_by_event(event_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="No questions found for this event")

@router.get("/question/{question_id}/answers/")
async def get_answers_for_question(question_id: int):
    result = get_answers_by_question(question_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="No answers found for this question")

@router.get("/questions/{event_id}/questions-answers/")
async def get_questions_and_answers_for_event(event_id: int):
    result = get_questions_and_answers_by_event(event_id)
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="No questions found for this event")
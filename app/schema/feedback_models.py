from pydantic import BaseModel

class QuestionCreate(BaseModel):
    event_id: int
    question_text: str

class AnswerCreate(BaseModel):
    question_id: int
    answer_text: str
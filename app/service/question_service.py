# 3rd party modules
from crazerace.http.error import NotFoundError
from crazerace.http.instrumentation import trace

# Internal modules
from app.models import Question
from app.models.dto import QuestionDTO
from app.repository import question_repo
from app.service import util


@trace("question_service")
def add_question(new_q: QuestionDTO) -> None:
    question = Question(
        id=new_q.id,
        latitude=new_q.latitude,
        longitude=new_q.longitude,
        text=new_q.text,
        text_en=new_q.text_en,
        answer=new_q.answer,
        answer_en=new_q.answer_en,
        created_at=new_q.created_at,
    )
    question_repo.save(question)


@trace("question_service")
def get_question(question_id: str) -> QuestionDTO:
    question = question_repo.find(question_id)
    if not question:
        raise NotFoundError()
    return QuestionDTO(
        id=question.id,
        latitude=question.latitude,
        longitude=question.longitude,
        text=question.text,
        text_en=question.text_en,
        answer=question.answer,
        answer_en=question.answer_en,
        created_at=question.created_at,
    )

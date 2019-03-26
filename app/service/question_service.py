# Internal modules
from app.models import Question
from app.models.dto import QuestionDTO
from app.repository import question_repo
from app.service import util

def add_question(new_q: QuestionDTO) -> None:
    question = Question(
        id=util.new_id(),
        latitude=new_q.latitude,
        longitude=new_q.longitude,
        text=new_q.text,
        text_en=new_q.text_en,
        answer=new_q.answer,
        answer_en=new_q.answer_en
    )

    question_repo.save(question)
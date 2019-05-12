# Standard library
import random
from typing import List

# 3rd party modules
from crazerace.http.error import NotFoundError, InternalServerError
from crazerace.http.instrumentation import trace

# Internal modules
from app.config import DEFAULT_NO_QUESTIONS, DEFAULT_MIN_DISTANCE, DEFAULT_MAX_DISTANCE
from app.models import Question, Game, GameMember
from app.models.dto import QuestionDTO, CoordinateDTO
from app.repository import question_repo
from app.service import util, distance_util


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


@trace("question_service")
def find_questions_for_game(game: Game, coordinate: CoordinateDTO) -> List[Question]:
    prev_ids = question_repo.find_previous_question_ids(game)
    available_questions = question_repo.find_all(except_ids=prev_ids)
    return _select_questions(available_questions, coordinate, DEFAULT_NO_QUESTIONS)


def _select_questions(
    questions: List[Question], origin: CoordinateDTO, no_questions: int
) -> List[Question]:
    if len(questions) < no_questions:
        raise InternalServerError("Not enough questions")
    question = _select_question(questions, origin)
    return (
        [question]
        if no_questions <= 1
        else [question]
        + _select_questions(
            _filter_questions(questions, question),
            question.coordinate(),
            no_questions - 1,
        )
    )


def _select_question(questions: List[Question], origin: CoordinateDTO) -> Question:
    matching_questions = [
        q
        for q in questions
        if distance_util.is_within(
            origin, q.coordinate(), DEFAULT_MAX_DISTANCE, DEFAULT_MIN_DISTANCE
        )
    ]
    if not matching_questions:
        raise InternalServerError("No questions could be selected")
    return random.choice(matching_questions)


def _filter_questions(questions: List[Question], exclude: Question) -> List[Question]:
    return [q for q in questions if q.id != exclude.id]

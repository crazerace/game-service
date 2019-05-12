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
    _assert_engough_questions(questions, no_questions)
    selected: List[Question] = []
    for _ in range(no_questions):
        question = _select_question(questions, origin, selected)
        origin = question.coordinate()
        selected += [question]
    return selected


def _select_question(
    questions: List[Question], origin: CoordinateDTO, previous: List[Question]
) -> Question:
    matching_questions = _select_questions_within(
        questions, origin, DEFAULT_MIN_DISTANCE, DEFAULT_MAX_DISTANCE, previous
    )
    if not matching_questions:
        raise InternalServerError("No questions could be selected")
    return random.choice(matching_questions)


def _select_questions_within(
    questions: List[Question],
    origin: CoordinateDTO,
    min_dist: int,
    max_dist: int,
    previous: List[Question],
) -> List[Question]:
    matches = [
        q
        for q in questions
        if distance_util.is_within(origin, q.coordinate(), max_dist, min_dist)
    ]
    return [m for m in matches if _previous_are_far_enough(m, previous, min_dist // 2)]


def _previous_are_far_enough(
    question: Question, previous: List[Question], min_dist: int
) -> bool:
    for prev in previous:
        if not distance_util.is_at_least(
            question.coordinate(), prev.coordinate(), min_dist
        ):
            return False
    return True


def _assert_engough_questions(questions: List[Question], expected: int) -> None:
    if len(questions) < expected:
        raise InternalServerError("Not enough questions")


def _filter_questions(questions: List[Question], exclude: Question) -> List[Question]:
    return [q for q in questions if q.id != exclude.id]

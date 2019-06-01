# Standard library
import random
from typing import List

# 3rd party modules
from crazerace.http.error import NotFoundError, InternalServerError
from crazerace.http.instrumentation import trace

# Internal modules
from app.config import DEFAULT_NO_QUESTIONS, DEFAULT_MIN_DISTANCE, DEFAULT_MAX_DISTANCE
from app.models import Question, Game, GameMember, GameMemberQuestion
from app.models.dto import QuestionDTO, CoordinateDTO
from app.repository import question_repo
from app.service import util, distance_util, game_state_util


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
    return _question_to_dto(question)


@trace("question_service")
def find_questions_for_game(game: Game, coordinate: CoordinateDTO) -> List[Question]:
    prev_ids = question_repo.find_previous_question_ids(game)
    available_questions = question_repo.find_all(except_ids=prev_ids)
    return _select_questions(available_questions, coordinate, DEFAULT_NO_QUESTIONS)


@trace("question_service")
def get_members_next_question(
    game_id: str, member_id: str, user_id: str, current_position: CoordinateDTO
) -> QuestionDTO:
    game = game_state_util.assert_game_exists(game_id)
    game_state_util.assert_valid_game_member(game_id, member_id, user_id)
    active_question = question_repo.find_members_active_question(game_id, member_id)
    if active_question:
        return _question_to_dto(active_question)
    questions = question_repo.find_members_possible_questions(game_id, member_id)
    question = _select_closest_question(questions, current_position)
    _create_and_save_game_member_question(game, member_id, question)
    return _question_to_dto(question)


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


def _select_closest_question(
    questions: List[Question], coordinate: CoordinateDTO
) -> Question:
    _assert_engough_questions(questions, 1)
    if len(questions) == 1:
        return questions[0]
    candidates = _filter_to_close_questions(questions, coordinate)
    return _find_closest_question(candidates, coordinate)


def _filter_to_close_questions(
    questions: List[Question], coordinate: CoordinateDTO
) -> List[Question]:
    min_dist = DEFAULT_MIN_DISTANCE // 4
    return [
        q
        for q in questions
        if distance_util.calculate(q.coordinate(), coordinate) > min_dist
    ]


def _find_closest_question(
    questions: List[Question], coordinate: CoordinateDTO
) -> Question:
    _assert_engough_questions(questions, 1)
    closest = questions[0]
    closest_distance = distance_util.calculate(closest.coordinate(), coordinate)
    for question in questions:
        distance = distance_util.calculate(question.coordinate(), coordinate)
        if distance < closest_distance:
            closest = question
            closest_distance = distance
    return closest


def _create_and_save_game_member_question(
    game: Game, member_id: str, question: Question
) -> None:
    game_question_id = [q.id for q in game.questions if q.question_id == question.id][0]
    question_repo.save_game_member_question(
        GameMemberQuestion(member_id=member_id, game_question_id=game_question_id)
    )


def _assert_engough_questions(questions: List[Question], expected: int) -> None:
    if len(questions) < expected:
        raise InternalServerError("Not enough questions")


def _filter_questions(questions: List[Question], exclude: Question) -> List[Question]:
    return [q for q in questions if q.id != exclude.id]


def _question_to_dto(question: Question) -> QuestionDTO:
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

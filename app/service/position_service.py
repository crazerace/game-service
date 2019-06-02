# Standard library
from typing import Optional, Tuple
from uuid import uuid4

# 3rd party modules
from crazerace.http.error import (
    PreconditionRequiredError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
)
from crazerace.http.instrumentation import trace

# Internal modules
from app.config import MAX_ANSWER_DISTANCE
from app.models import Game, GameMember, Position, Question
from app.models.dto import PositionDTO, PositionResultDTO
from app.repository import position_repo, question_repo
from app.service import game_service, question_service, distance_util, game_state_util


@trace("position_service")
def add_position(
    game_id: str, user_id: str, position_dto: PositionDTO
) -> PositionResultDTO:
    game, member = _assert_existing_game_and_member(
        game_id, user_id, position_dto.game_member_id
    )
    position = _create_and_store_position(position_dto)
    question = _position_is_answer_to(game, position)
    if not question:
        return PositionResultDTO.incorrect()
    game_finished = _answer_question(game, member, question, position)
    return _create_success_result(question, game_finished)


@trace("position_service")
def _position_is_answer_to(game: Game, position: Position) -> Optional[Question]:
    question = question_repo.find_members_active_question(
        game.id, position.game_member_id
    )
    origin = position.coordinate()
    destination = question.coordinate()
    return (
        question
        if question and distance_util.is_within(origin, destination, MAX_ANSWER_DISTANCE)
        else None
    )


@trace("position_service")
def _answer_question(
    game: Game, member: GameMember, question: Question, position: Position
) -> bool:
    question_repo.set_member_question_as_answered(question.id, position)
    if _member_is_done(game, member):
        return game_service.check_if_game_ended(game)
    return False


def _create_and_store_position(dto: PositionDTO) -> Position:
    position = Position(
        id=dto.id,
        game_member_id=dto.game_member_id,
        latitude=dto.latitude,
        longitude=dto.longitude,
        created_at=dto.created_at,
    )
    position_repo.save(position)
    return position


def _create_success_result(question: Question, finished: bool) -> PositionResultDTO:
    return PositionResultDTO(
        is_answer=True, game_finished=finished, question=question_service.to_dto(question)
    )


def _member_is_done(game: Game, member: GameMember) -> bool:
    answered_questions = [q for q in member.questions if q.position_id is not None]
    return len(answered_questions) == len(game.questions)


def _assert_existing_game_and_member(
    game_id: str, user_id: str, member_id: str
) -> Tuple[Game, GameMember]:
    game = game_state_util.assert_game_exists(game_id)
    member = game_state_util.assert_valid_game_member(game_id, member_id, user_id)
    return game, member

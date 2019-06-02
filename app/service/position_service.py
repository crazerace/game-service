# Standard library
from typing import Optional
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
from app.models import Position, Question
from app.models.dto import PositionDTO, PositionResultDTO
from app.repository import position_repo, question_repo
from app.service import question_service, distance_util, game_state_util


@trace("position_service")
def add_position(
    game_id: str, user_id: str, position_dto: PositionDTO
) -> PositionResultDTO:
    _assert_existing_game_and_member(game_id, user_id, position_dto.game_member_id)
    position = _create_position(position_dto)
    position_repo.save(position)
    question = _position_is_answer_to(game_id, position)
    if not question:
        return PositionResultDTO.incorrect()
    question_repo.set_member_question_as_answered(question.id, position)
    return PositionResultDTO(is_answer=True, question=question_service.to_dto(question))


@trace("position_service")
def _position_is_answer_to(game_id: str, position: Position) -> Optional[Question]:
    question = question_repo.find_members_active_question(
        game_id, position.game_member_id
    )
    origin = position.coordinate()
    destination = question.coordinate()
    return (
        question
        if question and distance_util.is_within(origin, destination, MAX_ANSWER_DISTANCE)
        else None
    )


def _create_position(dto: PositionDTO) -> Position:
    return Position(
        id=dto.id,
        game_member_id=dto.game_member_id,
        latitude=dto.latitude,
        longitude=dto.longitude,
        created_at=dto.created_at,
    )


def _assert_existing_game_and_member(game_id: str, user_id: str, member_id: str) -> None:
    game_state_util.assert_game_exists(game_id)
    game_state_util.assert_valid_game_member(game_id, member_id, user_id)

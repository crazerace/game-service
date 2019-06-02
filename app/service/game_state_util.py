# Standard library
from typing import List
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
from app.error import GameEndedError
from app.models import Game, GameMember, GameQuestion, Question
from app.models.dto import CreateGameDTO, GameDTO, GameMemberDTO
from app.repository import game_repo, member_repo


@trace("game_state_util")
def assert_game_exists(game_id: str) -> Game:
    game = game_repo.find(game_id)
    if not game:
        raise PreconditionRequiredError(f"Game with id={game_id} does not exit")
    return game


@trace("game_state_util")
def assert_active_game_exists(game_id: str) -> Game:
    game = assert_game_exists(game_id)
    if game.ended_at is not None:
        raise GameEndedError(game_id)
    return game


@trace("game_state_util")
def assert_valid_game_member(game_id: str, member_id: str, user_id: str) -> GameMember:
    member = member_repo.find(member_id)
    if not member:
        raise PreconditionRequiredError(f"Game member with id={member_id} does not exit")
    elif member.user_id != user_id:
        raise ForbiddenError("User ID and member ID is not related")
    elif member.game_id != game_id:
        raise PreconditionRequiredError(f"Member not part of game with id={game_id}")
    return member


@trace("game_state_util")
def assert_all_members_ready(game: Game) -> None:
    members_ready = [member.is_ready for member in game.members]
    if not all(members_ready):
        raise PreconditionRequiredError(
            f"All members are not ready in game with id={game.id}"
        )


@trace("game_state_util")
def assert_user_is_game_admin(user_id: str, game: Game) -> None:
    for member in game.members:
        if member.user_id == user_id and member.is_admin:
            return
    raise ForbiddenError(f"User is not admin on game with id={game.id}")


@trace("game_state_util")
def assert_game_not_started(game: Game) -> None:
    if game.started_at:
        raise PreconditionRequiredError(f"Game is started")

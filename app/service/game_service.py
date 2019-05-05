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
from app.models import Game, GameMember, Coordinate
from app.models.dto import CreateGameDTO, GameDTO, GameMemberDTO
from app.repository import game_repo, member_repo
from app.service import util


@trace("game_service")
def create_game(new_game: CreateGameDTO, user_id: str) -> None:
    game = Game(
        id=new_game.game_id,
        name=new_game.name,
        created_at=new_game.created_at,
        members=[
            GameMember(id=_new_id(), user_id=user_id, game_id=new_game.game_id, is_admin=True)
        ],
    )
    game_repo.save(game)


@trace("game_service")
def get_game(id: str) -> GameDTO:
    game = game_repo.find(id)
    if not game:
        raise NotFoundError(f"No game found with id: {id}")
    return GameDTO(
        id=game.id,
        name=game.name,
        questions=len(game.questions),
        created_at=game.created_at,
        started_at=game.started_at,
        ended_at=game.ended_at,
        members=_map_members_to_dto(game.members),
    )


@trace("game_service")
def start_game(game_id: str, user_id: str, coordinate: Coordinate) -> None:
    print(f"GameId={game_id} UserId={user_id} {coordinate}")
    _assert_game_can_be_started(game_id, user_id)


@trace("game_service")
def add_game_member(game_id: str, user_id: str) -> None:
    assert_game_exists(game_id)
    member = GameMember(id=util.new_id(), game_id=game_id, user_id=user_id)
    member_repo.add_member(member)


@trace("game_service")
def set_game_member_as_ready(game_id: str, member_id: str, user_id: str) -> None:
    assert_valid_game_member(game_id, member_id, user_id)
    member_repo.set_as_ready(member_id)


@trace("game_service")
def assert_game_exists(game_id: str) -> None:
    if not game_repo.find(game_id):
        raise PreconditionRequiredError(f"Game with id={game_id} does not exit")


@trace("game_service")
def assert_valid_game_member(game_id: str, member_id: str, user_id: str) -> None:
    assert_game_exists(game_id)
    member = member_repo.find(member_id)
    if not member:
        raise PreconditionRequiredError(f"Game member with id={member_id} does not exit")
    if member.user_id != user_id:
        raise ForbiddenError("Cannot set another user as ready")


@trace("game_service")
def _assert_game_can_be_started(game_id: str, user_id: str) -> None:
    game = game_repo.find(game_id)
    if not game:
        raise PreconditionRequiredError(f"Game with id={game_id} does not exit")
    _assert_user_is_game_admin(user_id, game)
    _assert_all_members_ready(game)
    if game.started_at is not None:
        raise ConflictError(f"Game with id={game_id} is already started")


def _assert_all_members_ready(game: Game) -> None:
    members_ready = [member.is_ready for member in game.members]
    if not all(members_ready):
        raise PreconditionRequiredError(f"All members are not ready in game with id={game.id}")


def _assert_user_is_game_admin(user_id: str, game: Game) -> None:
    for member in game.members:
        if member.user_id == user_id and member.is_admin:
            return
    raise ForbiddenError(f"User does not have permission to start game with id={game.id}")


def _new_id() -> str:
    return str(uuid4()).lower()


def _map_members_to_dto(members: List[GameMember]) -> List[GameMemberDTO]:
    return [
        GameMemberDTO(
            id=m.id,
            game_id=m.game_id,
            user_id=m.user_id,
            is_admin=m.is_admin,
            is_ready=m.is_ready,
            created_at=m.created_at,
        )
        for m in members
    ]

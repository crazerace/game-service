# Standard library
from uuid import uuid4

# 3rd party modules
from crazerace.http.error import PreconditionRequiredError, ForbiddenError
from crazerace.http.instrumentation import trace

# Internal modules
from app.models import Game, GameMember
from app.models.dto import CreateGameDTO
from app.repository import game_repo, member_repo
from app.service import util


@trace("game_service")
def create_game(new_game: CreateGameDTO, user_id: str) -> None:
    game = Game(
        id=new_game.game_id,
        name=new_game.name,
        created_at=new_game.created_at,
        members=[
            GameMember(
                id=_new_id(), user_id=user_id, game_id=new_game.game_id, is_admin=True
            )
        ],
    )
    game_repo.save(game)


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
        raise PreconditionRequiredError(
            f"Game member with id={member_id} does not exit"
        )
    if member.user_id != user_id:
        raise ForbiddenError("Cannot set another user as ready")


def _assert_user_is_game_admin(user_id: str, game: Game) -> None:
    for member in game.members:
        if member.user_id == user_id and member.is_admin:
            return
    raise ForbiddenError(f"User is not admin on game with id={game.id}")


def _new_id() -> str:
    return str(uuid4()).lower()

# 3rd party modules
from crazerace.http.error import PreconditionRequiredError
from crazerace.http.instrumentation import trace

# Internal modules
from app.models import Game, GameMember
from app.repository import game_repo
from app.service import util


@trace("game_service")
def add_game_member(game_id: str, user_id: str) -> None:
    assert_game_exists(game_id)
    member = GameMember(id=util.new_id(), game_id=game_id, user_id=user_id)
    game_repo.add_member(member)


@trace("game_service")
def assert_game_exists(game_id: str) -> None:
    if not game_repo.find(game_id):
        raise PreconditionRequiredError(f"Game with id={game_id} does not exit")


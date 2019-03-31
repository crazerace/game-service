#3rd party modules
from crazerace.http.error import NotFoundError
from crazerace.http.instrumentation import trace

# Internal modules
from app.models import Game
from app.models.dto import CreateGameDTO
from app.repository import game_repo
from app.service import util

@trace("game_service")
def create_game(new_game: CreateGameDTO) -> None:
    game = Game(
        id=new_game.game_id,
        name=new_game.name,
        created_at=new_game.created_at
    )
    game_repo.save(game)

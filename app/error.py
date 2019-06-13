# Internal modules
from crazerace.http import status
from crazerace.http.error import RequestError


class GameEndedError(RequestError):
    """Error attempts to access an ended game.

    game_id: Id of game"""

    def __init__(self, game_id: str) -> None:
        super().__init__(f"Game(id={game_id}) ended")
        self.id = "GAME_ENDED"

    def status(self) -> int:
        return status.HTTP_428_PRECONDITION_REQUIRED

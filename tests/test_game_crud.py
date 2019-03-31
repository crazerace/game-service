# Standard library
import json

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, JSON
from app.repository import game_repo


def test_create_game():
    with TestEnvironment() as client:

        #Ok game data
        game = json.dumps(
            {
                "name": "MyGame",
                "id": "asd123"
            }
        )
        res = client.post("/v1/games", data=game, content_type=JSON)
        assert res.status_code == status.HTTP_200_OK

        game = game_repo.find("asd123")
        assert game.name == "MyGame"

        #Incorrect game data types
        game = json.dumps(
            {
                "id": "asd123",
                "name": True,
            }
        )
        res_bad_req = client.post("/v1/games", data=game, content_type=JSON)
        assert res_bad_req.status_code == status.HTTP_400_BAD_REQUEST

        #Duplicate game id
        game = json.dumps(
            {
                "name": "MyGame",
                "id": "asd123"
            }
        )
        res_dup_game_id = client.post("/v1/games", data=game, content_type=JSON)
        assert res_dup_game_id.status_code == status.HTTP_409_CONFLICT


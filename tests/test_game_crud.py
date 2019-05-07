# Standard library
import json
from datetime import datetime

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, JSON, headers, new_id
from app.models import Game, GameMember
from app.repository import game_repo
from app.service import game_service


def test_create_game():
    with TestEnvironment() as client:

        # Ok game data
        game = json.dumps({"name": "MyGame", "id": "asd123"})
        headers_ok = headers(new_id())
        res = client.post("/v1/games", data=game, content_type=JSON, headers=headers_ok)
        assert res.status_code == status.HTTP_200_OK

        game = game_repo.find("asd123")
        assert game.name == "MyGame"

        # Incorrect game data types
        game = json.dumps({"id": "asd123", "name": True})
        res_bad_req = client.post(
            "/v1/games", data=game, content_type=JSON, headers=headers_ok
        )
        assert res_bad_req.status_code == status.HTTP_400_BAD_REQUEST

        # Duplicate game id
        game = json.dumps({"name": "MyGame", "id": "asd123"})
        res_dup_game_id = client.post(
            "/v1/games", data=game, content_type=JSON, headers=headers_ok
        )
        assert res_dup_game_id.status_code == status.HTTP_409_CONFLICT


def test_delete_game():
    game1_id = new_id()
    game2_id = new_id()
    game_member_id = new_id()
    game_admin_id = new_id()
    user1_id = new_id()
    user2_id = new_id()

    games = [
        Game(
            id=game1_id,
            name="Game Not Started",
            members=[
                GameMember(
                    id=new_id(),
                    game_id=game1_id,
                    user_id=user1_id,
                    is_admin=False,
                    is_ready=False,
                    created_at=datetime.utcnow(),
                ),
                GameMember(
                    id=new_id(),
                    game_id=game1_id,
                    user_id=user2_id,
                    is_admin=True,
                    is_ready=False,
                    created_at=datetime.utcnow(),
                ),
            ],
        ),
        Game(
            id=game2_id,
            name="Game Started",
            started_at=datetime.utcnow(),
            members=[
                GameMember(
                    id=new_id(),
                    game_id=game2_id,
                    user_id=user1_id,
                    is_admin=False,
                    is_ready=True,
                    created_at=datetime.utcnow(),
                ),
                GameMember(
                    id=new_id(),
                    game_id=game1_id,
                    user_id=user2_id,
                    is_admin=True,
                    is_ready=True,
                    created_at=datetime.utcnow(),
                ),
            ],
        ),
    ]

    with TestEnvironment(games) as client:
        headers_member = headers(user1_id)
        headers_admin = headers(user2_id)

        # Delete as regular game member (return 403)
        res_bad1 = client.delete(f"/v1/games/{game1_id}", headers=headers(user1_id))
        assert res_bad1.status_code == status.HTTP_403_FORBIDDEN
        assert game_repo.find(game1_id) is not None

        # Delete as game admin before game has started (return 200)
        res_ok = client.delete(f"/v1/games/{game1_id}", headers=headers(user2_id))
        assert res_ok.status_code == status.HTTP_200_OK
        assert game_repo.find(game1_id) is None

        # Delete as game admin after game has started (return 428)
        res_bad2 = client.delete(f"/v1/games/{game2_id}", headers=headers(user2_id))
        assert res_bad2.status_code == status.HTTP_428_PRECONDITION_REQUIRED
        assert game_repo.find(game2_id) is not None

        # Delete game that doesn't exist (return 428)
        assert game_repo.find("thisIdDoesntExist") is None
        res_bad3 = client.delete(
            f"/v1/games/thisIdDoesntExist", headers=headers(user2_id)
        )
        assert res_bad3.status_code == status.HTTP_428_PRECONDITION_REQUIRED


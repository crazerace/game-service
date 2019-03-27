# Standard library
import json
from datetime import datetime

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, headers, new_id
from app.models import Game, GameMember
from app.repository import game_repo


def test_add_question():
    game_id = new_id()
    game = Game(
        id=game_id,
        name="Text Game",
        members=[
            GameMember(
                id=new_id(),
                game_id=game_id,
                user_id=new_id(),
                is_admin=True,
                created_at=datetime.utcnow(),
            )
        ],
    )
    with TestEnvironment(items=[game]) as client:
        res_unauthorized = client.post(f"/v1/games/{game_id}/members")
        assert res_unauthorized.status_code == status.HTTP_401_UNAUTHORIZED

        user_id = new_id()
        headers_ok = headers(user_id)
        res = client.post(f"/v1/games/{game_id}/members", headers=headers_ok)
        assert res.status_code == status.HTTP_200_OK
        stored_game = game_repo.find(game_id)
        assert len(stored_game.members) == 2
        new_member = [member for member in stored_game.members if not member.is_admin][
            0
        ]
        assert len(new_member.id) > 0
        assert new_member.user_id == user_id
        assert new_member.game_id == game_id
        assert new_member.is_admin == False

        # Cannot add the same user to a game again
        res_conflict = client.post(f"/v1/games/{game_id}/members", headers=headers_ok)
        assert res_conflict.status_code == status.HTTP_409_CONFLICT
        assert len(game_repo.find(game_id).members) == 2

        # Cannot add user to a missing game
        res_missing_game = client.post(
            f"/v1/games/{new_id()}/members", headers=headers(new_id())
        )
        assert res_missing_game.status_code == status.HTTP_428_PRECONDITION_REQUIRED
        assert len(game_repo.find(game_id).members) == 2

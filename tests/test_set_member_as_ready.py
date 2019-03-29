# Standard library
import json
from datetime import datetime

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, headers, new_id
from app.models import Game, GameMember
from app.repository import game_repo


def test_add_game_member():
    game_id = new_id()
    member_id = new_id()
    user_id = new_id()
    games = [
        Game(
            id=game_id,
            name="Text Game",
            members=[
                GameMember(
                    id=new_id(),
                    game_id=game_id,
                    user_id=new_id(),
                    is_admin=True,
                    is_ready=True,
                    created_at=datetime.utcnow(),
                ),
                GameMember(
                    id=member_id,
                    game_id=game_id,
                    user_id=user_id,
                    is_admin=False,
                    is_ready=False,
                    created_at=datetime.utcnow(),
                ),
            ],
        )
    ]
    with TestEnvironment(items=games) as client:
        res_unauthorized = client.put(f"/v1/games/{game_id}/members/{member_id}/ready")
        assert res_unauthorized.status_code == status.HTTP_401_UNAUTHORIZED

        headers_ok = headers(user_id)
        res_missing_game = client.put(
            f"/v1/games/{new_id()}/members/{member_id}/ready", headers=headers_ok
        )
        assert res_missing_game.status_code == status.HTTP_428_PRECONDITION_REQUIRED

        other_member_id = new_id()
        res_missing_member = client.put(
            f"/v1/games/{game_id}/members/{other_member_id}/ready",
            headers=headers(other_member_id),
        )
        assert res_missing_member.status_code == status.HTTP_428_PRECONDITION_REQUIRED

        headers_403 = headers(new_id())
        res_forbidden = client.put(
            f"/v1/games/{game_id}/members/{member_id}/ready", headers=headers_403
        )
        assert res_forbidden.status_code == status.HTTP_403_FORBIDDEN

        res = client.put(
            f"/v1/games/{game_id}/members/{member_id}/ready", headers=headers_ok
        )
        assert res.status_code == status.HTTP_200_OK
        stored_game = game_repo.find(game_id)
        assert len(stored_game.members) == 2
        member = [m for m in stored_game.members if m.id == member_id][0]
        assert member.user_id == user_id
        assert member.game_id == game_id
        assert member.is_admin == False
        assert member.is_ready

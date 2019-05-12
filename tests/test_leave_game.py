# Standard library
import json
from datetime import datetime

# 3rd party modules
from crazerace.http import status

# Internal modules
from tests import TestEnvironment, headers, new_id
from app.models import Game, GameMember
from app.repository import game_repo, member_repo


def test_leave_game():
    game1_id = new_id()
    game2_id = new_id()
    game1_member_id = new_id()
    game2_member_id = new_id()
    other_member_id = new_id()
    user_id = new_id()

    game1_member = GameMember(
        id=game1_member_id,
        game_id=game1_id,
        user_id=user_id,
        is_admin=False,
        is_ready=False,
        created_at=datetime.utcnow(),
    )

    game2_member = GameMember(
        id=game2_member_id,
        game_id=game2_id,
        user_id=user_id,
        is_admin=False,
        is_ready=True,
        created_at=datetime.utcnow(),
    )

    game1 = Game(id=game1_id, name="Game Has Not Started", members=[game1_member])

    game2 = Game(
        id=game2_id,
        name="Game Started",
        started_at=datetime.utcnow(),
        members=[game2_member],
    )

    member_not_in_game = GameMember(
        id=other_member_id,
        game_id=new_id(),
        user_id=new_id(),
        is_admin=False,
        is_ready=False,
        created_at=datetime.utcnow(),
    )

    with TestEnvironment(
        [game1_member, game2_member, game1, game2, member_not_in_game]
    ) as client:

        # If game not started, remove game member from Game
        res_ok = client.put(
            f"/v1/games/{game1_id}/members/{game1_member_id}/leave",
            headers=headers(user_id),
        )
        assert res_ok.status_code == status.HTTP_200_OK
        game = game_repo.find(game1_id)
        assert len(game.members) == 0

        # If game started, set Game Member to resigned
        res_ok2 = client.put(
            f"/v1/games/{game2_id}/members/{game2_member_id}/leave",
            headers=headers(user_id),
        )
        assert res_ok2.status_code == status.HTTP_200_OK
        game = game_repo.find(game2_id)
        assert game2_member_id == game.members[0].id
        member = member_repo.find(game2_member_id)
        assert member.resigned_at is not None

        # user tries to make another user's GameMember leave a started game
        res_bad = client.put(
            f"/v1/games/{game1_id}/members/{other_member_id}/leave",
            headers=headers(other_member_id),
        )
        assert res_bad.status_code == status.HTTP_403_FORBIDDEN

        # If Game Member not in unstarted Game
        res_bad = client.put(
            f"/v1/games/{game2_id}/members/{other_member_id}/leave",
            headers=headers(other_member_id),
        )
        assert res_bad.status_code == status.HTTP_403_FORBIDDEN

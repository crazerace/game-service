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
        res_ok = client.delete(
            f"/v1/games/{game1_id}/members/{game1_member_id}", headers=headers(user_id)
        )
        assert res_ok.status_code == status.HTTP_200_OK
        game = game_repo.find(game1_id)
        assert len(game.members) == 0

        # If game started, set Game Member to resigned
        res_ok2 = client.delete(
            f"/v1/games/{game2_id}/members/{game2_member_id}", headers=headers(user_id)
        )
        assert res_ok2.status_code == status.HTTP_200_OK
        game = game_repo.find(game2_id)
        assert game2_member_id == game.members[0].id
        member = member_repo.find(game2_member_id)
        assert member.resigned_at is not None

        # user tries to make another user's GameMember leave a started game
        res_bad = client.delete(
            f"/v1/games/{game1_id}/members/{other_member_id}",
            headers=headers(other_member_id),
        )
        assert res_bad.status_code == status.HTTP_403_FORBIDDEN

        # If Game Member not in unstarted Game
        res_bad = client.delete(
            f"/v1/games/{game2_id}/members/{other_member_id}",
            headers=headers(other_member_id),
        )
        assert res_bad.status_code == status.HTTP_403_FORBIDDEN


def test_all_players_resign_game():
    game_id = new_id()
    game1_member_id = new_id()
    game2_member_id = new_id()
    game_not_member_id = new_id()
    user1_id = new_id()
    user2_id = new_id()
    user3_id = new_id()

    game1_member = GameMember(
        id=game1_member_id,
        game_id=game_id,
        user_id=user1_id,
        is_admin=False,
        is_ready=False,
        created_at=datetime.utcnow(),
    )

    game2_member = GameMember(
        id=game2_member_id,
        game_id=game_id,
        user_id=user2_id,
        is_admin=False,
        is_ready=True,
        created_at=datetime.utcnow(),
    )

    game_not_member = GameMember(
        id=game_not_member_id,
        game_id="InvalidGameID",
        user_id=user3_id,
        is_admin=False,
        is_ready=True,
        created_at=datetime.utcnow(),
    )

    game = Game(
        id=game_id,
        name="Game Started",
        started_at=datetime.utcnow(),
        members=[game2_member],
    )

    with TestEnvironment([game1_member, game2_member, game_not_member, game]) as client:

        # Player 1 of 2 resigns, game should not end
        res_member1_resigns = client.delete(
            f"/v1/games/{game_id}/members/{game1_member_id}", headers=headers(user1_id)
        )
        assert res_member1_resigns.status_code == status.HTTP_200_OK

        game = game_repo.find(game_id)
        assert game.ended_at == None

        # Player not member in game resigns game
        res__not_member_resigns = client.delete(
            f"/v1/games/{game_id}/members/{game_not_member_id}", headers=headers(user3_id)
        )
        assert (
            res__not_member_resigns.status_code == status.HTTP_428_PRECONDITION_REQUIRED
        )

        # Player 2 of 2 resigns, game should end
        res_member2_resigns = client.delete(
            f"/v1/games/{game_id}/members/{game2_member_id}", headers=headers(user2_id)
        )
        assert res_member2_resigns.status_code == status.HTTP_200_OK

        game = game_repo.find(game_id)
        assert game.ended_at != None

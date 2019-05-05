# Standard library
import json
from datetime import datetime, timedelta

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, JSON, headers, new_id
from app.models import Game, GameMember, GameQuestion, Question
from app.repository import game_repo


def test_start_game():
    two_hours_ago: datetime = datetime.utcnow() - timedelta(hours=2)
    one_hour_ago: datetime = datetime.utcnow() - timedelta(hours=1)
    now = datetime.utcnow()
    owner_id = new_id()

    q_old = Question(
        id=new_id(),
        latitude=52.1231,
        longitude=52.1231,
        text="t-old",
        text_en="t-old-en",
        answer="a-old",
        answer_en="a-old-en",
    )
    q1 = Question(
        id=new_id(),
        latitude=52.1231,
        longitude=52.1231,
        text="t1",
        text_en="t1-en",
        answer="a1",
        answer_en="a1-en",
    )
    q2 = Question(
        id=new_id(),
        latitude=52.1232,
        longitude=52.1232,
        text="t2",
        text_en="t2-en",
        answer="a2",
        answer_en="a2-en",
    )
    q3 = Question(
        id=new_id(),
        latitude=52.1233,
        longitude=52.1233,
        text="t3",
        text_en="t3-en",
        answer="a3",
        answer_en="a3-en",
    )
    q4 = Question(
        id=new_id(),
        latitude=52.1234,
        longitude=52.1234,
        text="t4",
        text_en="t4-en",
        answer="a4",
        answer_en="a4-en",
    )

    old_game_id = new_id()
    old_game = Game(
        id=old_game_id,
        name="Old name",
        created_at=two_hours_ago,
        started_at=one_hour_ago,
        ended_at=now,
        members=[
            GameMember(
                id="member-old-1",
                game_id=old_game_id,
                user_id=owner_id,
                is_admin=True,
                is_ready=True,
                created_at=two_hours_ago,
            )
        ],
        questions=[GameQuestion(game_id=old_game_id, question_id=q_old.id)],
    )

    game_id = new_id()
    game = Game(
        id=game_id,
        name="New name",
        created_at=now,
        members=[
            GameMember(
                id="member-new-1",
                game_id=game_id,
                user_id=owner_id,
                is_admin=True,
                is_ready=True,
                created_at=now,
            )
        ],
    )

    with TestEnvironment([q_old, q1, q2, q3, q4, old_game, game]) as client:
        headers_ok = headers(owner_id)
        res_ok = client.put(
            f"/v1/games/{game_id}/start?lat=59.318329&long=18.042192", headers=headers_ok
        )
        assert res_ok.status_code == status.HTTP_200_OK


def test_start_game_bad_state():
    now = datetime.utcnow()
    owner_id = new_id()
    guest_id = new_id()

    game_id = new_id()
    not_ready_game = Game(
        id=game_id,
        name="Not ready name",
        created_at=now,
        members=[
            GameMember(
                id="member-not-ready-1",
                game_id=game_id,
                user_id=owner_id,
                is_admin=True,
                is_ready=True,
                created_at=now,
            ),
            GameMember(
                id="member-not-ready-2",
                game_id=game_id,
                user_id=new_id(),
                is_admin=False,
                is_ready=False,
                created_at=now,
            ),
        ],
    )

    ready_game_id = new_id()
    ready_game = Game(
        id=ready_game_id,
        name="Not ready name",
        created_at=now,
        members=[
            GameMember(
                id="member-ready-1",
                game_id=ready_game_id,
                user_id=owner_id,
                is_admin=True,
                is_ready=True,
                created_at=now,
            ),
            GameMember(
                id="member-ready-2",
                game_id=ready_game_id,
                user_id=guest_id,
                is_admin=False,
                is_ready=True,
                created_at=now,
            ),
        ],
    )

    started_game_id = new_id()
    started_game = Game(
        id=started_game_id,
        name="Not ready name",
        created_at=now,
        started_at=datetime.utcnow(),
        members=[
            GameMember(
                id="member-started-1",
                game_id=started_game_id,
                user_id=owner_id,
                is_admin=True,
                is_ready=True,
                created_at=now,
            ),
            GameMember(
                id="member-started-2",
                game_id=started_game_id,
                user_id=guest_id,
                is_admin=False,
                is_ready=True,
                created_at=now,
            ),
        ],
    )
    with TestEnvironment([not_ready_game, ready_game, started_game]) as client:
        headers_ok = headers(owner_id)
        res_missing_game = client.put(
            f"/v1/games/{new_id()}/start?lat=59.318329&long=18.042192", headers=headers_ok
        )
        assert res_missing_game.status_code == status.HTTP_428_PRECONDITION_REQUIRED

        res_unready = client.put(
            f"/v1/games/{game_id}/start?lat=59.318329&long=18.042192", headers=headers_ok
        )
        assert res_unready.status_code == status.HTTP_428_PRECONDITION_REQUIRED

        headers_guest = headers(guest_id)
        res_forbidden = client.put(
            f"/v1/games/{ready_game_id}/start?lat=59.318329&long=18.042192", headers=headers_guest
        )
        assert res_forbidden.status_code == status.HTTP_403_FORBIDDEN

        res_already_started = client.put(
            f"/v1/games/{started_game_id}/start?lat=59.318329&long=18.042192", headers=headers_ok
        )
        assert res_already_started.status_code == status.HTTP_409_CONFLICT


def test_start_game_bad_request():
    game_id = new_id()
    with TestEnvironment() as client:
        res_unauthorized = client.put(f"/v1/games/{game_id}/start")
        assert res_unauthorized.status_code == status.HTTP_401_UNAUTHORIZED

        headers_ok = headers(new_id())
        res_no_lat_long = client.put(f"/v1/games/{new_id()}/start", headers=headers_ok)
        assert res_no_lat_long.status_code == status.HTTP_400_BAD_REQUEST

        res_no_lat = client.put(f"/v1/games/{game_id}/start?long=10.112", headers=headers_ok)
        assert res_no_lat.status_code == status.HTTP_400_BAD_REQUEST

        res_no_long = client.put(f"/v1/games/{game_id}/start?lat=10.112", headers=headers_ok)
        assert res_no_long.status_code == status.HTTP_400_BAD_REQUEST

        res_wrong_lat_type = client.put(
            f"/v1/games/{game_id}/start?lat=wrong&long=45.439", headers=headers_ok
        )
        assert res_wrong_lat_type.status_code == status.HTTP_400_BAD_REQUEST

        res_wrong_long_type = client.put(
            f"/v1/games/{game_id}/start?lat=43.11147&long=alsowrong", headers=headers_ok
        )
        assert res_wrong_long_type.status_code == status.HTTP_400_BAD_REQUEST

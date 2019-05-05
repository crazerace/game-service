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
        res_unauthorized = client.put(f"/v1/games/{game_id}/start")
        assert res_unauthorized.status_code == status.HTTP_401_UNAUTHORIZED

        headers_ok = headers(owner_id)
        res_ok = client.put(f"/v1/games/{game_id}/start", headers=headers_ok)
        assert res_ok.status_code == status.HTTP_200_OK

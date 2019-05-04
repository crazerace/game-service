# Standard library
import json
from datetime import datetime, timedelta

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, headers, new_id
from app.models import Game, GameMember, GameQuestion, Question


def test_get_game():
    two_hours_ago: datetime = datetime.utcnow() - timedelta(hours=2)
    one_hour_ago: datetime = datetime.utcnow() - timedelta(hours=1)
    now = datetime.utcnow()
    question_1 = Question(
        id=new_id(),
        latitude=52.1,
        longitude=52.1,
        text="Här ligger den här grejen",
        text_en="English thing",
        answer="Street 123",
        answer_en="Street 123",
    )
    question_2 = Question(
        id=new_id(),
        latitude=52.1,
        longitude=52.1,
        text="Här ligger den här grejen",
        text_en="English thing",
        answer="Street 123",
        answer_en="Street 123",
    )
    game_1_id: str = new_id()
    game_2_id: str = new_id()
    game_3_id: str = new_id()
    game_1 = Game(
        id=game_1_id,
        name="Game One",
        started_at=one_hour_ago,
        created_at=two_hours_ago,
        members=[
            GameMember(
                id="member-1-1",
                game_id=game_1_id,
                user_id="user-1",
                is_admin=True,
                is_ready=True,
                created_at=two_hours_ago,
            ),
            GameMember(
                id="member-1-2",
                game_id=game_1_id,
                user_id="user-2",
                is_admin=False,
                is_ready=True,
                created_at=two_hours_ago,
            ),
        ],
        questions=[
            GameQuestion(game_id=game_1_id, question_id=question_1.id),
            GameQuestion(game_id=game_1_id, question_id=question_2.id),
        ],
    )
    game_2 = Game(
        id=game_2_id,
        name="Game Two",
        created_at=one_hour_ago,
        members=[
            GameMember(
                id="member-2-1",
                game_id=game_2_id,
                user_id="user-1",
                is_admin=False,
                is_ready=False,
                created_at=two_hours_ago,
            ),
            GameMember(
                id="member-2-2",
                game_id=game_2_id,
                user_id="user-2",
                is_admin=True,
                is_ready=True,
                created_at=two_hours_ago,
            ),
        ],
        questions=[GameQuestion(game_id=game_2_id, question_id=question_1.id)],
    )
    game_3 = Game(
        id=game_3_id,
        name="Game Three",
        started_at=one_hour_ago,
        created_at=two_hours_ago,
        ended_at=now,
        members=[
            GameMember(
                id="member-3-1",
                game_id=game_3_id,
                user_id="user-1",
                is_admin=False,
                is_ready=True,
                created_at=two_hours_ago,
            ),
            GameMember(
                id="member-3-2",
                game_id=game_3_id,
                user_id="user-2",
                is_admin=True,
                is_ready=True,
                created_at=two_hours_ago,
            ),
        ],
        questions=[GameQuestion(game_id=game_3_id, question_id=question_2.id)],
    )
    with TestEnvironment([question_1, question_2, game_1, game_2, game_3]) as client:
        res_unauthorized = client.get(f"/v1/games/{game_1_id}")
        assert res_unauthorized.status_code == status.HTTP_401_UNAUTHORIZED

        headers_ok = headers("user-1")
        res_ok = client.get(f"/v1/games/{game_1_id}", headers=headers_ok)
        assert res_ok.status_code == status.HTTP_200_OK
        body = res_ok.get_json()
        assert body["id"] == game_1_id
        assert body["name"] == "Game One"
        assert body["createdAt"] == f"{two_hours_ago}"
        assert body["startedAt"] == f"{one_hour_ago}"
        assert body["endedAt"] == None
        assert body["status"] == "STARTED"
        # assert body["questions"] == 2
        # assert len(body["members"]) == 2

        headers_ok = headers("user-3")
        res_ok = client.get(f"/v1/games/{game_2_id}", headers=headers_ok)
        assert res_ok.status_code == status.HTTP_200_OK
        body = res_ok.get_json()
        assert body["id"] == game_2_id
        assert body["name"] == "Game Two"
        assert body["createdAt"] == f"{one_hour_ago}"
        assert body["startedAt"] == None
        assert body["endedAt"] == None
        assert body["status"] == "CREATED"
        # assert body["questions"] == 2
        # assert len(body["members"]) == 2

        headers_ok = headers("user-3")
        res_ok = client.get(f"/v1/games/{game_3_id}", headers=headers_ok)
        assert res_ok.status_code == status.HTTP_200_OK
        body = res_ok.get_json()
        assert body["id"] == game_3_id
        assert body["name"] == "Game Three"
        assert body["createdAt"] == f"{two_hours_ago}"
        assert body["startedAt"] == f"{one_hour_ago}"
        assert body["endedAt"] == f"{now}"
        assert body["status"] == "ENDED"
        # assert body["questions"] == 2
        # assert len(body["members"]) == 2

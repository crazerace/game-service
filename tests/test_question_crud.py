# Standard library
import json
from datetime import datetime

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, JSON, headers, new_id
from app.repository import question_repo
from app.models import (
    Question,
    Game,
    GameMember,
    Position,
    GameMemberQuestion,
    GameQuestion,
)


def test_add_question():
    question = {
        "latitude": 52.1,
        "longitude": 52.1,
        "text": "Här ligger den här grejen",
        "text_en": "This is where this thing is",
        "answer": "Online Street 1337",
        "answer_en": "Online Street 1337",
    }
    with TestEnvironment() as client:
        headers_ok = headers(new_id(), "ADMIN")
        res = client.post(
            "/v1/questions",
            data=json.dumps(question),
            headers=headers_ok,
            content_type=JSON,
        )
        assert res.status_code == status.HTTP_200_OK
        body = res.get_json()

        questions = question_repo.find_all()
        assert len(questions) == 1
        assert questions[0].latitude == 52.1
        assert questions[0].answer == "Online Street 1337"
        question_id = questions[0].id
        assert question_id is not None

        # Test that posting a question wit the same id fails with 409
        question["id"] = question_id
        res = client.post(
            "/v1/questions",
            data=json.dumps(question),
            headers=headers_ok,
            content_type=JSON,
        )
        assert res.status_code == status.HTTP_409_CONFLICT


def test_add_question_403_401_and_400():
    question = json.dumps(
        {
            "latitude": 52.1,
            "longitude": 52.1,
            "text": "Här ligger den här grejen",  # text_en missing
            "answer": "Online Street 1337",
            "answer_en": "Online Street 1337",
        }
    )
    with TestEnvironment() as client:
        headers_403 = headers(new_id())
        res_forbidden = client.post(
            "/v1/questions", data=question, headers=headers_403, content_type=JSON
        )
        assert res_forbidden.status_code == status.HTTP_403_FORBIDDEN

        res_unauth = client.post("/v1/questions", data=question, content_type=JSON)
        assert res_unauth.status_code == status.HTTP_401_UNAUTHORIZED

        headers_ok = headers(new_id(), "ADMIN")
        res_bad_req_1 = client.post(
            "/v1/questions", data=question, headers=headers_ok, content_type=JSON
        )
        assert res_bad_req_1.status_code == status.HTTP_400_BAD_REQUEST

        question = json.dumps(
            {
                "latitude": True,
                "longitude": 52.1,
                "text": "Här ligger den här grejen",
                "text_en": "This is where that thing is",
                "answer": "Online Street 1337",
                "answer_en": "Online Street 1337",
            }
        )
        res_bad_req_2 = client.post(
            "/v1/questions", data=question, headers=headers_ok, content_type=JSON
        )
        assert res_bad_req_2.status_code == status.HTTP_400_BAD_REQUEST


def test_get_question():
    question_id: str = new_id()
    question = Question(
        id=question_id,
        latitude=52.1,
        longitude=52.1,
        text="Här ligger den här grejen",
        text_en="English thing",
        answer="Street 123",
        answer_en="Street 123",
    )

    with TestEnvironment([question]) as client:
        res_unauthorized = client.get(f"/v1/questions/{question_id}")
        assert res_unauthorized.status_code == status.HTTP_401_UNAUTHORIZED

        headers_ok = headers(new_id())
        res = client.get(f"/v1/questions/{question_id}", headers=headers_ok)
        assert res.status_code == status.HTTP_200_OK
        body = res.get_json()
        assert body["id"] == question_id
        assert "latitude" not in body
        assert "longitude" not in body
        assert "answer" not in body
        assert "answer_en" not in body

        admin_headers = headers(new_id(), "ADMIN")
        res = client.get(f"/v1/questions/{question_id}", headers=admin_headers)
        assert res.status_code == status.HTTP_200_OK
        body = res.get_json()
        assert body["id"] == question_id
        assert body["latitude"] == 52.1
        assert body["longitude"] == 52.1
        assert body["answer"] == "Street 123"
        assert body["answer_en"] == "Street 123"

        not_found_res = client.get(f"/v1/questions/{new_id()}", headers=headers_ok)
        assert not_found_res.status_code == status.HTTP_404_NOT_FOUND


def test_get_members_next_question():
    game_id = new_id()
    member_id = new_id()
    other_member_id = new_id()

    q1_id = new_id()
    q1 = Question(
        id=q1_id,
        latitude=59.318134,
        longitude=18.063666,
        text="t1",
        text_en="t1-en",
        answer="a1",
        answer_en="a1-en",
    )
    q2_id = new_id()
    q2 = Question(
        id=q2_id,
        latitude=59.316556,
        longitude=18.033478,
        text="t2",
        text_en="t2-en",
        answer="a2",
        answer_en="a2-en",
    )
    q3_id = new_id()
    q3 = Question(
        id=q3_id,
        latitude=59.316709,
        longitude=17.984827,
        text="t3",
        text_en="t3-en",
        answer="a3",
        answer_en="a3-en",
    )

    game = Game(
        id=game_id,
        name="Test game",
        created_at=datetime.utcnow(),
        started_at=datetime.utcnow(),
        members=[
            GameMember(
                id=member_id,
                game_id=game_id,
                user_id=new_id(),
                is_admin=False,
                is_ready=True,
                created_at=datetime.utcnow(),
            ),
            GameMember(
                id=other_member_id,
                game_id=game_id,
                user_id=new_id(),
                is_admin=False,
                is_ready=True,
                created_at=datetime.utcnow(),
            ),
        ],
        questions=[
            GameQuestion(id=1, game_id=game_id, question_id=q1_id),
            GameQuestion(id=2, game_id=game_id, question_id=q2_id),
            GameQuestion(id=3, game_id=game_id, question_id=q3_id),
        ],
    )

    pos_id = new_id()
    pos = Position(
        id=pos_id,
        game_member_id=other_member_id,
        latitude=59.318133,
        longitude=18.063667,
        created_at=datetime.utcnow(),
    )

    answered_question = GameMemberQuestion(
        member_id=other_member_id,
        game_question_id=1,
        answer_position_id=pos_id,
        answered_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    db_items = [q1, q2, game, pos, answered_question]
    with TestEnvironment(db_items) as client:
        headers_ok = headers(new_id())
        res = client.get(
            f"/v1/games/{game_id}/members/{member_id}/next-question?lat=59.318132&long=18.063668",
            headers=headers_ok,
        )
        assert res.status_code == status.HTTP_200_OK

        res_no_position = client.get(
            f"/v1/games/{game_id}/members/{member_id}/next-question", headers=headers_ok
        )
        assert res_no_position.status_code == status.HTTP_400_BAD_REQUEST


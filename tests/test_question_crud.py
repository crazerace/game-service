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
    user_id = new_id()
    member_id = new_id()

    other_user_id = new_id()
    other_member_id = new_id()

    user_3_id = new_id()
    member_3_id = new_id()

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
                user_id=user_id,
                is_admin=False,
                is_ready=True,
                created_at=datetime.utcnow(),
            ),
            GameMember(
                id=other_member_id,
                game_id=game_id,
                user_id=other_user_id,
                is_admin=False,
                is_ready=True,
                created_at=datetime.utcnow(),
            ),
            GameMember(
                id=member_3_id,
                game_id=game_id,
                user_id=user_3_id,
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

    pos_1_id = new_id()
    pos_1 = Position(
        id=pos_1_id,
        game_member_id=other_member_id,
        latitude=59.318133,
        longitude=18.063667,
        created_at=datetime.utcnow(),
    )
    pos_2_id = new_id()
    pos_2 = Position(
        id=pos_2_id,
        game_member_id=member_3_id,
        latitude=59.316556,
        longitude=18.033478,
        created_at=datetime.utcnow(),
    )
    pos_3_id = new_id()
    pos_3 = Position(
        id=pos_3_id,
        game_member_id=member_3_id,
        latitude=59.316709,
        longitude=17.984827,
        created_at=datetime.utcnow(),
    )

    answered_question_1 = GameMemberQuestion(
        member_id=other_member_id,
        game_question_id=1,
        position_id=pos_1_id,
        answered_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    answered_question_2 = GameMemberQuestion(
        member_id=member_3_id,
        game_question_id=2,
        position_id=pos_2_id,
        answered_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    answered_question_3 = GameMemberQuestion(
        member_id=member_3_id,
        game_question_id=3,
        position_id=pos_3_id,
        answered_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )

    db_items = [
        q1,
        q2,
        q3,
        game,
        pos_1,
        pos_2,
        pos_3,
        answered_question_1,
        answered_question_2,
        answered_question_3,
    ]
    with TestEnvironment(db_items) as client:
        member_headers = headers(user_id)
        res_1 = client.get(
            f"/v1/games/{game_id}/members/{member_id}/next-question?lat=59.318132&long=18.063668",
            headers=member_headers,
            content_type=JSON,
        )
        assert res_1.status_code == status.HTTP_200_OK
        body_1 = res_1.get_json()
        assert body_1["id"] == q2_id
        assert "answer" not in body_1

        # Test with position closer to q1 but selected and unaswerd q2. Should return q2
        res_2 = client.get(
            f"/v1/games/{game_id}/members/{member_id}/next-question?lat=59.316&long=18.053",
            headers=member_headers,
            content_type=JSON,
        )
        assert res_2.status_code == status.HTTP_200_OK
        body_2 = res_2.get_json()
        assert body_2["id"] == q2_id
        assert "answer" not in body_2

        res_other_user_1 = client.get(
            f"/v1/games/{game_id}/members/{other_member_id}/next-question?lat=59.316&long=18.053",
            headers=headers(other_user_id),
            content_type=JSON,
        )
        assert res_other_user_1.status_code == status.HTTP_200_OK
        other_body_1 = res_other_user_1.get_json()
        assert other_body_1["id"] == q2_id
        assert "answer" not in other_body_1

        # Test with position closer to q3 but selected and unaswerd q2. Should return q2
        res_other_user_2 = client.get(
            f"/v1/games/{game_id}/members/{other_member_id}/next-question?lat=59.316&long=18.0",
            headers=headers(other_user_id),
            content_type=JSON,
        )
        assert res_other_user_2.status_code == status.HTTP_200_OK
        other_body_2 = res_other_user_2.get_json()
        assert other_body_2["id"] == q2_id
        assert "answer" not in other_body_2

        # Test with position to close to q1 but that being the only available question. Should return q1
        res_member_3 = client.get(
            f"/v1/games/{game_id}/members/{member_3_id}/next-question?lat=59.317&long=18.062",
            headers=headers(user_3_id),
            content_type=JSON,
        )
        assert res_member_3.status_code == status.HTTP_200_OK
        member_3_body = res_member_3.get_json()
        assert member_3_body["id"] == q1_id
        assert "answer" not in member_3_body

        res_no_position = client.get(
            f"/v1/games/{game_id}/members/{member_id}/next-question",
            headers=member_headers,
        )
        assert res_no_position.status_code == status.HTTP_400_BAD_REQUEST

# Standard library
import json

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, JSON, headers, new_id
from app.repository import question_repo
from app.models import Question


def test_add_question():
    question = json.dumps(
        {
            "latitude": 52.1,
            "longitude": 52.1,
            "text": "Här ligger den här grejen",
            "text_en": "This is where this thing is",
            "answer": "Online Street 1337",
            "answer_en": "Online Street 1337",
        }
    )
    with TestEnvironment() as client:
        headers_ok = headers(new_id(), "ADMIN")
        res = client.post(
            "/v1/questions", data=question, headers=headers_ok, content_type=JSON
        )
        assert res.status_code == status.HTTP_200_OK
        body = res.get_json()

        questions = question_repo.find_all()
        assert len(questions) == 1
        assert questions[0].latitude == 52.1
        assert questions[0].answer == "Online Street 1337"


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
        answer_en="Street 123"
    )

    with TestEnvironment([question]) as client:
        res = client.get(
            f"/v1/questions/{question_id}"
        )
        assert res.status_code == status.HTTP_200_OK

# Standard library
import json

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, JSON, headers, new_id


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


def test_add_question_401_and_403():
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
        headers_403 = headers(new_id())
        res_forbidden = client.post(
            "/v1/questions", data=question, headers=headers_403, content_type=JSON
        )
        assert res_forbidden.status_code == status.HTTP_403_FORBIDDEN

        res_unauth = client.post("/v1/questions", data=question, content_type=JSON)
        assert res_unauth.status_code == status.HTTP_401_UNAUTHORIZED


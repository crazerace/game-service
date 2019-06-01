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


def test_add_position():
    game_id = new_id()
    user_id = new_id()
    member_id = new_id()

    question_id = new_id()
    question = Question(
        id=question_id,
        latitude=59.318134,
        longitude=18.063666,
        text="t1",
        text_en="t1-en",
        answer="a1",
        answer_en="a1-en",
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
            )
        ],
        questions=[GameQuestion(id=1, game_id=game_id, question_id=question_id)],
    )

    pos_id = new_id()
    pos = Position(  # 137.64 meters from question 1.
        id=pos_id,
        game_member_id=member_id,
        latitude=59.317,
        longitude=18.063,
        created_at=datetime.utcnow(),
    )

    member_question = GameMemberQuestion(
        member_id=member_id,
        game_question_id=1,
        answer_position_id=None,
        answered_at=None,
        created_at=datetime.utcnow(),
    )

    db_items = [question, game, pos, member_question]
    with TestEnvironment(db_items) as client:
        # Registering a position 66.27 meters from question 1. Should NOT return answer
        res_miss = client.post(
            f"/v1/games/{game_id}/members/{member_id}/position",
            headers=headers(user_id),
            content_type=JSON,
            data=json.dumps({"latitude": 59.3181, "longitude": 18.0625}),
        )
        assert res_miss.status_code == status.HTTP_200_OK
        miss_body = res_miss.get_json()
        assert not miss_body["isAnswer"]
        assert miss_body["question"] is None

        # Registering a position 9.02 meters from question 1. Should return answer
        res_success = client.post(
            f"/v1/games/{game_id}/members/{member_id}/position",
            headers=headers(user_id),
            content_type=JSON,
            data=json.dumps({"latitude": 59.318078, "longitude": 18.063551}),
        )
        assert res_success.status_code == status.HTTP_200_OK
        success_body = res_success.get_json()
        assert success_body["isAnswer"]
        assert success_body["question"]["id"] == question_id
        assert success_body["question"]["answer"] == "a1"
        assert success_body["question"]["answer_en"] == "a1-en"

# Standard library
import json
from datetime import datetime, timedelta

# 3rd party modules
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, JSON, headers, new_id
from app.repository import position_repo, question_repo, placement_repo
from app.models import (
    Question,
    Game,
    GameMember,
    Placement,
    Position,
    GameMemberQuestion,
    GameQuestion,
)


def test_add_position():
    now = datetime.utcnow()
    one_minute_ago = now - timedelta(minutes=1)
    two_minutes_ago = now - timedelta(minutes=2)

    game_id = new_id()
    user_id = new_id()
    member_id = new_id()
    other_member_id = new_id()

    question_1_id = new_id()
    question_1 = Question(
        id=question_1_id,
        latitude=59.318134,
        longitude=18.063666,
        text="t1",
        text_en="t1-en",
        answer="a1",
        answer_en="a1-en",
    )

    question_2_id = new_id()
    question_2 = Question(
        id=question_2_id,
        latitude=59.31,
        longitude=18.06,
        text="t2",
        text_en="t2-en",
        answer="a2",
        answer_en="a2-en",
    )

    game = Game(
        id=game_id,
        name="Test game",
        created_at=two_minutes_ago,
        started_at=two_minutes_ago,
        members=[
            GameMember(
                id=member_id,
                game_id=game_id,
                user_id=user_id,
                is_admin=False,
                is_ready=True,
                created_at=two_minutes_ago,
            ),
            GameMember(
                id=other_member_id,
                game_id=game_id,
                user_id=new_id(),
                is_admin=True,
                is_ready=True,
                created_at=two_minutes_ago,
            ),
            GameMember(
                id=new_id(),
                game_id=game_id,
                user_id=new_id(),
                is_admin=False,
                is_ready=True,
                created_at=two_minutes_ago,
                resigned_at=one_minute_ago,
            ),
        ],
        questions=[
            GameQuestion(id=1, game_id=game_id, question_id=question_1_id),
            GameQuestion(id=2, game_id=game_id, question_id=question_2_id),
        ],
        placements=[
            Placement(
                game_id=game_id, member_id=other_member_id, created_at=one_minute_ago
            )
        ],
    )

    pos_1_id = new_id()
    pos_1 = Position(  # 137.64 meters from question 1.
        id=pos_1_id,
        game_member_id=member_id,
        latitude=59.317,
        longitude=18.063,
        created_at=datetime.utcnow(),
    )

    pos_2_id = new_id()
    pos_2 = Position(  # 137.64 meters from question 1.
        id=pos_2_id,
        game_member_id=other_member_id,
        latitude=59.31,
        longitude=18.06,
        created_at=two_minutes_ago,
    )

    pos_3_id = new_id()
    pos_3 = Position(  # 137.64 meters from question 1.
        id=pos_3_id,
        game_member_id=other_member_id,
        latitude=59.318134,
        longitude=18.063666,
        created_at=one_minute_ago,
    )

    member_question = GameMemberQuestion(
        member_id=member_id,
        game_question_id=1,
        position_id=None,
        answered_at=None,
        created_at=datetime.utcnow(),
    )

    other_member_question_1 = GameMemberQuestion(
        member_id=other_member_id,
        game_question_id=2,
        position_id=pos_2_id,
        answered_at=two_minutes_ago,
        created_at=two_minutes_ago,
    )

    other_member_question_2 = GameMemberQuestion(
        member_id=other_member_id,
        game_question_id=1,
        position_id=pos_3_id,
        answered_at=one_minute_ago,
        created_at=two_minutes_ago,
    )

    db_items = [
        question_1,
        question_2,
        game,
        pos_1,
        pos_2,
        pos_3,
        member_question,
        other_member_question_1,
        other_member_question_2,
    ]
    with TestEnvironment(db_items) as client:
        assert len(position_repo.find_member_positions(member_id)) == 1
        placements = placement_repo.find_game_placements(game_id)
        assert len(placements) == 1 and placements[0].member_id == other_member_id

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
        assert not miss_body["gameFinished"]
        assert miss_body["question"] is None
        assert len(position_repo.find_member_positions(member_id)) == 2
        active_question = question_repo.find_members_active_question(game_id, member_id)
        assert active_question.id == question_1_id

        placements = placement_repo.find_game_placements(game_id)
        assert len(placements) == 1 and placements[0].member_id == other_member_id

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
        assert not success_body["gameFinished"]
        assert success_body["question"]["id"] == question_1_id
        assert success_body["question"]["answer"] == "a1"
        assert success_body["question"]["answer_en"] == "a1-en"
        assert len(position_repo.find_member_positions(member_id)) == 3

        placements = placement_repo.find_game_placements(game_id)
        assert len(placements) == 1 and placements[0].member_id == other_member_id

        # Call question selection to get next question
        res_get_next_question = client.get(
            f"/v1/games/{game_id}/members/{member_id}/next-question?lat=59.318078&long=18.063551",
            headers=headers(user_id),
            content_type=JSON,
        )
        assert res_get_next_question.status_code == status.HTTP_200_OK
        assert res_get_next_question.get_json()["id"] == question_2_id
        next_active_question = question_repo.find_members_active_question(
            game_id, member_id
        )
        assert next_active_question.id == question_2_id

        # Registering a position 1.25 meters from question 2. Should return answer and finish game
        res_final = client.post(
            f"/v1/games/{game_id}/members/{member_id}/position",
            headers=headers(user_id),
            content_type=JSON,
            data=json.dumps({"latitude": 59.31001, "longitude": 18.06001}),
        )
        assert res_final.status_code == status.HTTP_200_OK
        final_body = res_final.get_json()
        assert final_body["isAnswer"]
        assert final_body["gameFinished"]
        assert final_body["question"]["id"] == question_2_id
        assert final_body["question"]["answer"] == "a2"
        assert final_body["question"]["answer_en"] == "a2-en"
        assert len(position_repo.find_member_positions(member_id)) == 4

        placements = placement_repo.find_game_placements(game_id)
        assert len(placements) == 2
        assert placements[0].member_id == other_member_id
        assert placements[1].member_id == member_id

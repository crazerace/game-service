# Standard library
import json
from datetime import datetime, timedelta

# 3rd party modules
import requests_mock
from crazerace.http import status

# Intenal modules
from tests import TestEnvironment, JSON, headers, new_id
from app.config import USER_SERVICE_URL
from app.models import Game, GameMember, GameQuestion, Question
from app.repository import game_repo
from app.service import game_service


def test_create_game():
    with TestEnvironment() as client:
        # Ok game data
        game = json.dumps({"name": "MyGame", "id": "asd123"})
        headers_ok = headers(new_id())
        res = client.post("/v1/games", data=game, content_type=JSON, headers=headers_ok)
        assert res.status_code == status.HTTP_200_OK
        assert res.get_json()["name"] == "MyGame"
        assert res.get_json()["id"] == "asd123"

        game = game_repo.find("asd123")
        assert game.name == "MyGame"

        game = json.dumps({"name": "gameWithoutId"})
        res = client.post("/v1/games", data=game, content_type=JSON, headers=headers_ok)
        assert res.status_code == status.HTTP_200_OK
        assert res.get_json()["name"] == "gameWithoutId"
        game_id = res.get_json()["id"]
        assert len(game_id) == 36  # Check is UUID

        game = game_repo.find(game_id)
        assert game.name == "gameWithoutId"

        # Incorrect game data types
        game = json.dumps({"id": "asd123", "name": True})
        res_bad_req = client.post(
            "/v1/games", data=game, content_type=JSON, headers=headers_ok
        )
        assert res_bad_req.status_code == status.HTTP_400_BAD_REQUEST

        # Duplicate game id
        game = json.dumps({"name": "MyGame", "id": "asd123"})
        res_dup_game_id = client.post(
            "/v1/games", data=game, content_type=JSON, headers=headers_ok
        )
        assert res_dup_game_id.status_code == status.HTTP_409_CONFLICT


def test_delete_game():
    game1_id = new_id()
    game2_id = new_id()
    user1_id = new_id()
    user2_id = new_id()

    games = [
        Game(
            id=game1_id,
            name="Game Not Started",
            members=[
                GameMember(
                    id=new_id(),
                    game_id=game1_id,
                    user_id=user1_id,
                    is_admin=False,
                    is_ready=False,
                    created_at=datetime.utcnow(),
                ),
                GameMember(
                    id=new_id(),
                    game_id=game1_id,
                    user_id=user2_id,
                    is_admin=True,
                    is_ready=False,
                    created_at=datetime.utcnow(),
                ),
            ],
        ),
        Game(
            id=game2_id,
            name="Game Started",
            started_at=datetime.utcnow(),
            members=[
                GameMember(
                    id=new_id(),
                    game_id=game2_id,
                    user_id=user1_id,
                    is_admin=False,
                    is_ready=True,
                    created_at=datetime.utcnow(),
                ),
                GameMember(
                    id=new_id(),
                    game_id=game1_id,
                    user_id=user2_id,
                    is_admin=True,
                    is_ready=True,
                    created_at=datetime.utcnow(),
                ),
            ],
        ),
    ]

    with TestEnvironment(games) as client:

        # Delete as regular game member (return 403)
        res_bad1 = client.delete(f"/v1/games/{game1_id}", headers=headers(user1_id))
        assert res_bad1.status_code == status.HTTP_403_FORBIDDEN
        assert game_repo.find(game1_id) is not None

        # Delete as game admin before game has started (return 200)
        res_ok = client.delete(f"/v1/games/{game1_id}", headers=headers(user2_id))
        assert res_ok.status_code == status.HTTP_200_OK
        assert game_repo.find(game1_id) is None

        # Delete as game admin after game has started (return 428)
        res_bad2 = client.delete(f"/v1/games/{game2_id}", headers=headers(user2_id))
        assert res_bad2.status_code == status.HTTP_428_PRECONDITION_REQUIRED
        assert game_repo.find(game2_id) is not None

        # Delete game that doesn't exist (return 428)
        assert game_repo.find("thisIdDoesntExist") is None
        res_bad3 = client.delete(
            f"/v1/games/thisIdDoesntExist", headers=headers(user2_id)
        )
        assert res_bad3.status_code == status.HTTP_428_PRECONDITION_REQUIRED


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
    with requests_mock.mock() as m:
        m.get(
            f"{USER_SERVICE_URL}/v1/users/user-1",
            json={
                "id": "user-1",
                "username": "User 1",
                "createdAt": "2019-01-01 12:12:12.222",
            },
            headers={"Content-Type": "application/json"},
        )
        m.get(
            f"{USER_SERVICE_URL}/v1/users/user-2",
            json={
                "id": "user-2",
                "username": "User 2",
                "createdAt": "2019-01-01 12:12:12.222",
            },
            headers={"Content-Type": "application/json"},
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
            assert body["questions"] == 2
            assert len(body["members"]) == 2

            member_1 = body["members"][0]
            assert member_1["id"] == "member-1-1"
            assert member_1["isAdmin"] == True
            assert member_1["user"]["id"] == "user-1"
            assert member_1["user"]["username"] == "User 1"

            member_2 = body["members"][1]
            assert member_2["id"] == "member-1-2"
            assert member_2["isAdmin"] == False
            assert member_2["user"]["id"] == "user-2"
            assert member_2["user"]["username"] == "User 2"

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
            assert body["questions"] == 1
            assert len(body["members"]) == 2

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
            assert body["questions"] == 1
            assert len(body["members"]) == 2

            res_missing = client.get(f"/v1/games/{new_id()}", headers=headers_ok)
            assert res_missing.status_code == status.HTTP_404_NOT_FOUND


def test_get_game_by_shortcode():
    two_hours_ago: datetime = datetime.utcnow() - timedelta(hours=2)
    one_hour_ago: datetime = datetime.utcnow() - timedelta(hours=1)
    now = datetime.utcnow()

    game_1_id: str = "5a11d445-2b53-4047-8db5-d414d1c882c6"
    game_2_id: str = "fc79d60b-ef95-4499-aaa7-04bced45516f"
    game_3_id: str = "dd053768-267d-43fd-ada4-69cb144037aa"
    game_1 = Game(
        id=game_1_id, name="Game One", started_at=one_hour_ago, created_at=two_hours_ago
    )
    game_2 = Game(id=game_2_id, name="Game Two", created_at=one_hour_ago)
    game_3 = Game(
        id=game_3_id, name="Game Three", started_at=None, created_at=two_hours_ago
    )
    with TestEnvironment([game_1, game_2, game_3]) as client:
        res_unauthorized = client.get(f"/v1/games/shortcode/{game_1_id[:4]}")
        assert res_unauthorized.status_code == status.HTTP_401_UNAUTHORIZED

        headers_ok = headers("user-1")
        res_not_found = client.get(
            f"/v1/games/shortcode/{game_1_id[:4]}", headers=headers_ok
        )
        assert res_not_found.status_code == status.HTTP_404_NOT_FOUND
        body = res_not_found.get_json()
        assert body["message"] == f"No unstarted game found with code: {game_1_id[:4]}"

        headers_ok = headers("user-3")
        res_ok = client.get(f"/v1/games/shortcode/{game_2_id[:4]}", headers=headers_ok)
        assert res_ok.status_code == status.HTTP_200_OK
        body = res_ok.get_json()
        assert body["id"] == game_2_id
        assert body["name"] == "Game Two"

        headers_ok = headers("user-3")
        res_ok = client.get(f"/v1/games/shortcode/{game_3_id[:4]}", headers=headers_ok)
        assert res_ok.status_code == status.HTTP_200_OK
        body = res_ok.get_json()
        assert body["id"] == game_3_id
        assert body["name"] == "Game Three"

        res_missing = client.get(
            f"/v1/games/shortcode/{new_id()[:4]}", headers=headers_ok
        )
        assert res_missing.status_code == status.HTTP_404_NOT_FOUND

        res_invalid_shortcode_length = client.get(
            f"/v1/games/shortcode/{new_id()[:6]}", headers=headers_ok
        )
        assert res_invalid_shortcode_length.status_code == status.HTTP_400_BAD_REQUEST
        body1 = res_invalid_shortcode_length.get_json()
        assert body1["message"] == "Invalid shortcode length"

        res_invalid_shortcode_characters = client.get(
            f"/v1/games/shortcode/€as%", headers=headers_ok
        )
        assert res_invalid_shortcode_characters.status_code == status.HTTP_400_BAD_REQUEST
        body2 = res_invalid_shortcode_characters.get_json()
        assert body2["message"] == "Shortcode contains invalid characters"

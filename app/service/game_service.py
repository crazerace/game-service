# Standard library
from typing import List
from uuid import uuid4

# 3rd party modules
from crazerace.http.error import (
    PreconditionRequiredError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
)
from crazerace.http.instrumentation import trace

# Internal modules
from app.models import Game, GameMember, GameQuestion, Question
from app.models.dto import CreateGameDTO, GameDTO, GameMemberDTO, CoordinateDTO
from app.repository import game_repo, member_repo, question_repo
from app.service import util, question_service, game_state_util


@trace("game_service")
def create_game(new_game: CreateGameDTO, user_id: str) -> None:
    game = Game(
        id=new_game.game_id,
        name=new_game.name,
        created_at=new_game.created_at,
        members=[
            GameMember(
                id=util.new_id(), user_id=user_id, game_id=new_game.game_id, is_admin=True
            )
        ],
    )
    game_repo.save(game)


@trace("game_service")
def delete_game(game_id: str, user_id: str) -> None:
    game = game_state_util.assert_game_exists(game_id)
    game_state_util.assert_user_is_game_admin(user_id, game)
    game_state_util.assert_game_not_started(game)
    game_repo.delete(game)


@trace("game_service")
def get_game(id: str) -> GameDTO:
    game = game_repo.find(id)
    if not game:
        raise NotFoundError(f"No game found with id: {id}")
    return GameDTO(
        id=game.id,
        name=game.name,
        questions=len(game.questions),
        created_at=game.created_at,
        started_at=game.started_at,
        ended_at=game.ended_at,
        members=_map_members_to_dto(game.members),
    )


@trace("game_service")
def start_game(game_id: str, user_id: str, coordinate: CoordinateDTO) -> None:
    game = _find_game_and_assert_can_be_started(game_id, user_id)
    questions = question_service.find_questions_for_game(game, coordinate)
    game_questions = _map_questions_to_game(game.id, questions)
    game_repo.save_questions(game_questions)
    game_repo.set_started(game)


@trace("game_service")
def add_game_member(game_id: str, user_id: str) -> None:
    game_state_util.assert_game_exists(game_id)
    member = GameMember(id=util.new_id(), game_id=game_id, user_id=user_id)
    member_repo.add_member(member)


@trace("game_service")
def set_game_member_as_ready(game_id: str, member_id: str, user_id: str) -> None:
    game_state_util.assert_valid_game_member(game_id, member_id, user_id)
    member_repo.set_as_ready(member_id)


@trace("game_service")
def leave_game(game_id: str, member_id: str, user_id: str) -> None:
    game = game_state_util.assert_game_exists(game_id)
    member = game_state_util.assert_valid_game_member(game_id, member_id, user_id)
    if game.started_at is None:
        member_repo.delete_member(member)
    else:
        member_repo.set_member_status_as_resigned(member)
    check_if_game_ended(game)


@trace("game_service")
def check_if_game_ended(game: Game) -> bool:
    active_member_ids = [m.id for m in game.members if m.resigned_at == None]
    if len(active_member_ids) == 0:
        game_repo.end(game)
        return True
    answered = question_repo.count_answered_questions(game.id)
    total_questions = len(game.questions)
    for member_id in active_member_ids:
        if member_id not in answered or answered[member_id] != total_questions:
            return False
    game_repo.end(game)
    return True


@trace("game_service")
def _find_game_and_assert_can_be_started(game_id: str, user_id: str) -> Game:
    game = game_state_util.assert_game_exists(game_id)
    game_state_util.assert_user_is_game_admin(user_id, game)
    game_state_util.assert_all_members_ready(game)
    if game.started_at is not None:
        raise ConflictError(f"Game with id={game_id} is already started")
    return game


def _map_members_to_dto(members: List[GameMember]) -> List[GameMemberDTO]:
    return [
        GameMemberDTO(
            id=m.id,
            game_id=m.game_id,
            user_id=m.user_id,
            is_admin=m.is_admin,
            is_ready=m.is_ready,
            created_at=m.created_at,
        )
        for m in members
    ]


def _map_questions_to_game(game_id: str, questions: List[Question]) -> List[GameQuestion]:
    return [GameQuestion(game_id=game_id, question_id=q.id) for q in questions]


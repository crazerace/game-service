# Standard libraries
import logging
from datetime import datetime
from typing import List, Optional

# 3rd party libraries
from crazerace.http.error import ConflictError, InternalServerError
from crazerace.http.instrumentation import trace

# Internal modules
from app import db
from app.models import (
    Question,
    Game,
    GameMember,
    GameQuestion,
    GameMemberQuestion,
    Position,
)
from .util import handle_error


_log = logging.getLogger(__name__)


@trace("question_repo")
@handle_error(logger=_log, integrity_error_class=ConflictError)
def save(question: Question) -> None:
    db.session.add(question)
    db.session.commit()


@trace("question_repo")
def find_all(except_ids: List[str] = []) -> List[Question]:
    if not except_ids:
        return Question.query.all()
    return Question.query.filter(Question.id.notin_(except_ids)).all()  # type: ignore


@trace("question_repo")
def find_previous_question_ids(game: Game) -> List[str]:
    user_ids = [m.user_id for m in game.members]
    res = (
        db.session.query(GameQuestion, GameMember)
        .filter(GameQuestion.game_id == GameMember.game_id)
        .filter(GameMember.user_id.in_(user_ids))  # type: ignore
        .all()
    )
    return list({game_question.question_id for game_question, _ in res})


# The performance of this probably sucks, should be refactored
@trace("question_repo")
def find_members_possible_questions(game_id: str, member_id: str) -> List[Question]:
    answered_ids = [
        q.game_question_id
        for q in GameMemberQuestion.query.filter(
            GameMemberQuestion.member_id == member_id,
            GameMemberQuestion.answered_at.isnot(None),  #  type: ignore
        ).all()
    ]
    return (
        db.session.query(Question)
        .join(GameQuestion)
        .filter(
            GameQuestion.game_id == game_id,
            GameQuestion.id.notin_(answered_ids),  # type: ignore
        )
        .all()
    )


# The performance of this probably sucks, should be refactored
@trace("question_repo")
def find_members_active_question(game_id: str, member_id: str) -> Optional[Question]:
    active_question = GameMemberQuestion.query.filter(
        GameMemberQuestion.member_id == member_id,
        GameMemberQuestion.answered_at.is_(None),  #  type: ignore
    ).first()
    if not active_question:
        return None

    return (
        db.session.query(Question)
        .join(GameQuestion)
        .filter(
            GameQuestion.game_id == game_id,
            GameQuestion.id == active_question.game_question_id,
        )
        .first()
    )


@trace("question_repo")
def set_member_question_as_answered(question_id: str, position: Position) -> None:
    active_question = (
        GameMemberQuestion.query.join(GameQuestion)
        .filter(
            GameMemberQuestion.member_id == position.game_member_id,
            GameMemberQuestion.answered_at.is_(None),  #  type: ignore
            GameQuestion.question_id == question_id,
        )
        .first()
    )
    if not active_question:
        return InternalServerError("Could not find active question")

    active_question.answered_at = datetime.utcnow()
    active_question.answer_position_id = position.id
    db.session.commit()


@trace("question_repo")
@handle_error(logger=_log, integrity_error_class=ConflictError)
def save_game_member_question(question: GameMemberQuestion) -> None:
    db.session.add(question)
    db.session.commit()


@trace("question_repo")
def find(id: str) -> Optional[Question]:
    return Question.query.filter(Question.id == id).first()

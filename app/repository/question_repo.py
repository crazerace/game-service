# Standard libraries
import logging
from typing import List, Optional

# 3rd party libraries
from crazerace.http.error import ConflictError
from crazerace.http.instrumentation import trace

# Internal modules
from app import db
from app.models import Question, Game, GameMember, GameQuestion
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


@trace("question_repo")
def find(id: str) -> Optional[Question]:
    return Question.query.filter(Question.id == id).first()

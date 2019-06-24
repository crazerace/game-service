# Standard libraries
import logging
from datetime import datetime
from typing import List, Optional

# 3rd party libraries
from crazerace.http.error import ConflictError, InternalServerError
from crazerace.http.instrumentation import trace

# Internal modules
from app import db
from app.models import Game, GameQuestion, GameMember
from .util import handle_error


_log = logging.getLogger(__name__)


@trace("game_repo")
@handle_error(logger=_log, integrity_error_class=ConflictError)
def save(game: Game) -> None:
    db.session.add(game)
    db.session.commit()


@trace("game_repo")
@handle_error(logger=_log, integrity_error_class=ConflictError)
def save_questions(questions: List[GameQuestion]) -> None:
    for question in questions:
        db.session.add(question)
    db.session.commit()


@trace("game_repo")
@handle_error(logger=_log, integrity_error_class=InternalServerError)
def set_started(game: Game) -> None:
    game.started_at = datetime.utcnow()
    db.session.commit()


@trace("game_repo")
def find(id: str) -> Optional[Game]:
    return Game.query.filter(Game.id == id).first()


@trace("game_repo")
def find_by_shortcode(short_code: str) -> Optional[Game]:
    return Game.query.filter(
        Game.id.startswith(short_code), Game.started_at == None
    ).first()


@trace("game_repo")
def delete(game: Game) -> None:
    for member in game.members:
        db.session.delete(member)
    db.session.delete(game)
    db.session.commit()


@trace("game_repo")
def end(game: Game) -> None:
    game.ended_at = datetime.utcnow()
    db.session.commit()

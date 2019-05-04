# Standard libraries
import logging
from typing import Optional

# 3rd party libraries
from crazerace.http.error import ConflictError, NotFoundError
from crazerace.http.instrumentation import trace

# Internal modules
from app import db
from app.models import GameMember
from .util import handle_error


_log = logging.getLogger(__name__)


@trace("member_repo")
@handle_error(logger=_log, integrity_error_class=ConflictError)
def add_member(member: GameMember) -> None:
    db.session.add(member)
    db.session.commit()


@trace("member_repo")
@handle_error(logger=_log)
def set_as_ready(id: str) -> None:
    member = find(id)
    if not member:
        raise NotFoundError(f"Game member with id={id} not found")
    member.is_ready = True
    db.session.commit()


@trace("member_repo")
def find(id: str) -> Optional[GameMember]:
    return GameMember.query.filter(GameMember.id == id).first()

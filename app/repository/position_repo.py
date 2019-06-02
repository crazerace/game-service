# Standard libraries
import logging
from typing import List
from datetime import datetime

# 3rd party libraries
from crazerace.http.instrumentation import trace

# Internal modules
from app import db
from app.models import Position
from .util import handle_error


_log = logging.getLogger(__name__)


@trace("position_repo")
@handle_error(logger=_log)
def save(position: Position) -> None:
    db.session.add(position)
    db.session.commit()


@trace("position_repo")
def find_member_positions(member_id: str) -> List[Position]:
    return Position.query.filter(Position.game_member_id == member_id).all()


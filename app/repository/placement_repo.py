# Standard libraries
import logging
from typing import List

# 3rd party libraries
from crazerace.http.instrumentation import trace
from sqlalchemy import asc

# Internal modules
from app import db
from app.models import Placement
from .util import handle_error


_log = logging.getLogger(__name__)


@trace("placement_repo")
@handle_error(logger=_log)
def save(placement: Placement) -> None:
    db.session.add(placement)
    db.session.commit()


@trace("placement_repo")
def find_game_placements(game_id: str) -> List[Placement]:
    return (
        Placement.query.filter(Placement.game_id == game_id)
        .order_by(asc(Placement.created_at))
        .all()
    )


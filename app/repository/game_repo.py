# Standard libraries
import logging
from typing import Optional

# 3rd party libraries
from crazerace.http.instrumentation import trace

# Internal modules
from app import db
from app.models import Game
from .util import handle_error


_log = logging.getLogger(__name__)


@trace("game_repo")
def find(id: str) -> Optional[Game]:
    return Game.query.filter(Game.id == id).first()


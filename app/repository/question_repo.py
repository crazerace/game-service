#Standard libraries
import logging
from typing import List, Optional

# 3rd party libraries
from crazerace.http.error import ConflictError
from crazerace.http.instrumentation import trace

# Internal modules
from app import db
from app.models import Question
from .util import handle_error


_log = logging.getLogger(__name__)

@trace("question_repo")
@handle_error(logger=_log, integrity_error_class=ConflictError)
def save(question: Question) -> None:
	db.session.add(question)
	db.session.commit()


@trace("question_repo")
def find_all() -> List[Question]:
	return Question.query.all()


@trace("question_repo")
def find(id: str) -> Optional[Question]:
	return Question.query.filter(Question.id == id).first()
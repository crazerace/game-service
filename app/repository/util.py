# Standard library
import re
from logging import Logger
from typing import Any, Callable, Optional
from functools import wraps

# 3rd party modules
from sqlalchemy.exc import IntegrityError
from crazerace.http.error import DatabaseError

# Internal modules
from app import db


def handle_error(
    logger: Logger, integrity_error_class: Optional[Callable] = None
) -> Callable:
    def handle_database_error(f) -> Callable:
        @wraps(f)
        def decorated(*args, **kwargs) -> Any:
            try:
                return f(*args, **kwargs)
            except IntegrityError as e:
                if integrity_error_class:
                    logger.info(str(e))
                    raise integrity_error_class()
                else:
                    _raise_database_error(logger, e)
            except Exception as e:
                _raise_database_error(logger, e)

        return decorated

    return handle_database_error


def _raise_database_error(logger: Logger, e: Exception) -> None:
    err = DatabaseError(cause_message=str(e))
    logger.error(err.full_message())
    db.session.rollback()
    raise err


def sanitize_string(original):
    """Removes sql special characters from a string.

    :param original: Original string to santize
    :return: Sanitized string.
    """
    return re.sub("[%;\\_]", "", original)


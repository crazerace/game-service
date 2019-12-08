# Standard library
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# 3rd party libraries
from crazerace.http.error import BadGatewayError
from crazerace.http.instrumentation import get_request_id

# Internal modules
from app.config import DATETIME_FORMAT


_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class UserDTO:
    id: str
    username: str
    created_at: datetime

    @classmethod
    def fromdict(cls, raw: Dict[str, Any]) -> "UserDTO":
        try:
            user_id = raw["id"]
            username = raw["username"]
            created_at = datetime.strptime(raw["createdAt"], DATETIME_FORMAT)
            if not (isinstance(user_id, str) and isinstance(username, str)):
                raise BadGatewayError()
            return cls(id=user_id, username=username, created_at=created_at)
        except (KeyError, ValueError) as e:
            _log.warning(
                f"Failed to parse UserDTO. Error={repr(e)} requestId=[{get_request_id()}]"
            )
            raise BadGatewayError()

    def todict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "username": self.username,
            "createdAt": f"{self.created_at}",
        }


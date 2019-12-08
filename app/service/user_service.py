# Standard library
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# 3rd party libraries
from cachetools import cached, TTLCache
from crazerace.http import rpc, new_id
from crazerace.http.error import BadGatewayError
from crazerace.http.instrumentation import trace, get_request_id
from flask import request

# Internal modules
from app.config import USER_CACHE_SIZE, USER_CACHE_TTL, USER_SERVICE_URL, SERVER_NAME
from app.models.external import UserDTO


_log = logging.getLogger(__name__)


@trace("user_service")
def fetch_user(user_id: str) -> UserDTO:
    try:
        return _fetch_user_with_cache(user_id)
    except Exception as e:
        _log.error(
            f"Fetching user failed with error=[{repr(e)}] requestId=[{get_request_id()}]"
        )
        raise BadGatewayError()


@cached(cache=TTLCache(maxsize=USER_CACHE_SIZE, ttl=USER_CACHE_TTL))
def _fetch_user_with_cache(user_id: str) -> UserDTO:
    res = rpc.get(
        url=f"{USER_SERVICE_URL}/v1/users/{user_id}",
        user_id=request.user_id,
        role=request.role,
        headers={"User-Agent": SERVER_NAME},
    )
    return UserDTO.fromdict(res.json)


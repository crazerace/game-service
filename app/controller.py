# Standard library
from typing import Any, Dict, Optional

# 3rd party modules
import flask
from flask import jsonify, make_response, request

# Internal modules
from app.config import status
from app.error import BadRequestError


def check_health() -> flask.Response:
    return _create_response({"status": "OK"})


def _get_request_body(*required_fields: str) -> Dict[str, Any]:
    """Gets flask request body as dict and optionally verifies that field names are present

    :param required_fields: Optional list of required field names.
    :return: Request body.
    """
    body = request.get_json(silent=True)
    for field in required_fields:
        if field not in body:
            raise BadRequestError(message=f"Missing required field: {field}")
    return body


def _get_param(name: str, default: Optional[str]) -> str:
    """Gets a request parameter with an optional default.
    If no parameter is found and the defualt is none a BadRequestError is thown.

    :param name: Name of the parameter to get.
    :param default: Optional default value.
    :return: Value.
    """
    value = request.args.get(name, default)
    if not value:
        raise BadRequestError(message=f"Missing {name} param")
    return value


def _create_response(
    result: Dict[str, Any], status: int = status.HTTP_200_OK
) -> flask.Response:
    """Returns a response indicating that an index update was triggered.

    :return: flask.Response.
    """
    return make_response(jsonify(result), status)


def _create_ok_response() -> flask.Response:
    """Creates a 200 OK response.

    :return: flask.Response.
    """
    ok_body: Dict[str, str] = {"status": "OK"}
    return make_response(jsonify(ok_body), status.HTTP_200_OK)

# Standard library
import logging
from datetime import datetime
from functools import wraps
from typing import Callable, Optional
from uuid import uuid4

# 3rd party modules.
import flask
from flask import Flask, jsonify, make_response, request

# Internal modules
from app.config import AppConfig, status
from app.config import REQUEST_ID_HEADER, SERVICE_NAME, SERVER_NAME
from app.error import RequestError


app = Flask(SERVICE_NAME)
app.config.from_object(AppConfig)


from app import routes


_log = logging.getLogger("RequestLogger")
error_log = logging.getLogger("ErrorHandler")


@app.before_request
def add_request_id() -> None:
    """Adds a request id to an incomming request."""
    incomming_id: Optional[str] = request.headers.get(REQUEST_ID_HEADER)
    request.id = incomming_id or str(uuid4()).lower()
    _log.info(
        f"Incomming request {request.method} {request.path} requestId=[{request.id}]"
    )


@app.after_request
def add_request_id_to_response(response: flask.Response) -> flask.Response:
    """Adds request id header to each response.

    :param response: Response to add header to.
    :return: Response with header.
    """
    response.headers[REQUEST_ID_HEADER] = request.id
    response.headers["Server"] = SERVER_NAME
    response.headers["Date"] = f"{datetime.utcnow()}"
    return response


@app.errorhandler(RequestError)
def handle_request_error(error: RequestError) -> flask.Response:
    """Handles errors encountered when handling requests.

    :param error: Encountered RequestError.
    :return: flask.Response indicating the encountered error.
    """
    if error.status() >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        error_log.error(str(error))
    else:
        error_log.info(str(error))
    json_error = jsonify(error.asdict())
    return make_response(json_error, error.status())

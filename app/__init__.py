# Standard library
import logging
from datetime import datetime
from functools import wraps
from typing import Callable, Optional
from uuid import uuid4

# 3rd party modules.
import flask
import werkzeug
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from crazerace.http import status, instrumentation
from crazerace.http.error import RequestError, NotFoundError, MethodNotAllowedError

# Internal modules
from app.config import AppConfig
from app.config import REQUEST_ID_HEADER, SERVICE_NAME, SERVER_NAME


app = Flask(SERVICE_NAME)
app.config.from_object(AppConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes
from app import models


_log = logging.getLogger("RequestLogger")
error_log = logging.getLogger("ErrorHandler")


@app.before_request
def add_request_id() -> None:
    """Adds a request id to an incomming request."""
    instrumentation.add_request_id()


@app.after_request
def add_request_id_to_response(response: flask.Response) -> flask.Response:
    """Adds request id header to each response.

    :param response: Response to add header to.
    :return: Response with header.
    """
    response.headers[instrumentation.REQUEST_ID_HEADER] = request.id
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


@app.errorhandler(404)
def handle_not_found(err: werkzeug.exceptions.NotFound) -> flask.Response:
    """Handles 404 errors.

    :return: flask.Response indicating the encountered error.
    """
    error = NotFoundError()
    return make_response(jsonify(error.asdict()), error.status())


@app.errorhandler(405)
def handle_method_not_allowed(
    err: werkzeug.exceptions.MethodNotAllowed
) -> flask.Response:
    """Handles 405 errors.

    :return: flask.Response indicating the encountered error.
    """
    error = MethodNotAllowedError()
    return make_response(jsonify(error.asdict()), error.status())

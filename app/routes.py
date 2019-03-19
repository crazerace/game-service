# Standard library
from typing import Any, Dict

# 3rd party modules.
import flask

# Internal modules
from app import app
from app import controller


@app.route("/health", methods=["GET"])
def check_health() -> flask.Response:
    return controller.check_health()


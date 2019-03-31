# Standard library
from typing import Any, Dict, Optional

# 3rd party modules
import flask
from flask import jsonify, make_response, request
from crazerace import http
from crazerace.http import status
from crazerace.http.error import BadRequestError
from crazerace.http.instrumentation import trace

# Internal modules
<<<<<<< Updated upstream
from app.service import health
=======
from app.service import health, question_service, game_service
from app.models.dto import QuestionDTO, CreateGameDTO
>>>>>>> Stashed changes


@trace("controller")
def check_health() -> flask.Response:
    health_status = health.check()
    return http.create_response(health_status)
<<<<<<< Updated upstream
=======


@trace("controller")
def add_question() -> flask.Response:
    body = get_request_body(
        "latitude", "longitude", "text", "text_en", "answer", "answer_en"
    )
    question = QuestionDTO.fromdict(body)
    question_service.add_question(question)
    return http.create_ok_response()


@trace("controller")
def get_question(question_id: str) -> flask.Response:
    question = question_service.get_question(question_id)
    body = (
        question.todict()
        if request.role == "ADMIN"
        else question.only_question().todict()
    )
    return http.create_response(body)


@trace("controller")
def create_game() -> flask.Response:
    body = get_request_body("name", "id")
    game = CreateGameDTO.fromdict(body)
    game_service.create_game(game)
    return http.create_ok_response()
>>>>>>> Stashed changes

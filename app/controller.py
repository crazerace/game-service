# Standard library
from typing import Any, Dict, Optional

# 3rd party modules
import flask
from flask import jsonify, make_response, request
from crazerace import http
from crazerace.http import status, get_request_body
from crazerace.http.error import BadRequestError
from crazerace.http.instrumentation import trace

# Internal modules
from app.service import health
from app.service import health, game_service
from app.models.dto import QuestionDTO, CreateGameDTO
from app.service import game_service
from app.service import question_service
from app.models.dto import QuestionDTO


@trace("controller")
def check_health() -> flask.Response:
    health_status = health.check()
    return http.create_response(health_status)


@trace("controller")
def add_game_member(game_id: str) -> flask.Response:
    user_id: str = request.user_id
    game_service.add_game_member(game_id, user_id)
    return http.create_ok_response()


@trace("controller")
def set_game_member_as_ready(game_id: str, member_id: str) -> flask.Response:
    user_id: str = request.user_id
    game_service.set_game_member_as_ready(game_id, member_id, user_id)
    return http.create_ok_response()


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
    user_id = request.user_id
    body = get_request_body("name")
    game = CreateGameDTO.fromdict(body)
    game_service.create_game(game, user_id)
    return http.create_ok_response()
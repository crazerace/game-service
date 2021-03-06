# Standard library
import logging
from typing import Any, Dict, Optional

# 3rd party modules
import flask
from flask import jsonify, make_response, request
from crazerace import http
from crazerace.http import status, get_request_body, get_param
from crazerace.http.error import BadRequestError
from crazerace.http.instrumentation import trace

# Internal modules
from app.service import health
from app.service import health, game_service
from app.models.dto import QuestionDTO, CreateGameDTO, CoordinateDTO, PositionDTO
from app.service import game_service
from app.service import question_service
from app.service import position_service


_log = logging.getLogger(__name__)


@trace("controller")
def check_health() -> flask.Response:
    health_status = health.check()
    return http.create_response(health_status)


@trace("controller")
def add_game_member(game_id: str) -> flask.Response:
    user_id: str = request.user_id
    member = game_service.add_game_member(game_id, user_id)
    return http.create_response(member.todict())


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
    user_id: str = request.user_id
    body = get_request_body("name")
    game = CreateGameDTO.fromdict(body)
    game_info = game_service.create_game(game, user_id)
    return http.create_response(game_info.todict())


@trace("controller")
def delete_game(game_id: str) -> flask.Response:
    user_id: str = request.user_id
    game_service.delete_game(game_id, user_id)
    return http.create_ok_response()


@trace("controller")
def get_game(game_id: str) -> flask.Response:
    game = game_service.get_game(game_id)
    return http.create_response(game.todict())


@trace("controller")
def get_game_by_shortcode(short_code: str) -> flask.Response:
    game = game_service.get_game_by_shortcode(short_code)
    return http.create_response(game.todict())


@trace("controller")
def start_game(game_id: str) -> flask.Response:
    user_id: str = request.user_id
    coordinate = _get_coordinate_from_query()
    game_service.start_game(game_id, user_id, coordinate)
    return http.create_ok_response()


@trace("controller")
def leave_game(game_id: str, member_id: str) -> flask.Response:
    user_id = request.user_id
    game_service.leave_game(game_id, member_id, user_id)
    return http.create_ok_response()


@trace("controller")
def get_members_next_question(game_id: str, member_id: str) -> flask.Response:
    user_id: str = request.user_id
    coordinate = _get_coordinate_from_query()
    question = question_service.get_members_next_question(
        game_id, member_id, user_id, coordinate
    )
    return http.create_response(question.only_question().todict())


@trace("controller")
def add_position(game_id: str, member_id: str) -> flask.Response:
    user_id = request.user_id
    position = PositionDTO.fromdict(member_id, get_request_body("latitude", "longitude"))
    result = position_service.add_position(game_id, user_id, position)
    return http.create_response(result.todict())


def _get_coordinate_from_query() -> CoordinateDTO:
    try:
        return CoordinateDTO(
            latitude=float(get_param("lat")), longitude=float(get_param("long"))
        )
    except ValueError as e:
        _log.info(f"Error parsing position: {e}")
        raise BadRequestError("Malformed position query")


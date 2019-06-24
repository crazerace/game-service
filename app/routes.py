# Standard library
from typing import Any, Dict

# 3rd party modules.
import flask
from crazerace import http
from crazerace.http.security import secured

# Internal modules
from app import app
from app.config import JWT_SECRET
from app import controller


# Create game
@app.route("/v1/games", methods=["POST"])
@secured(JWT_SECRET)
def create_game() -> flask.Response:
    return controller.create_game()


@app.route("/v1/games/<game_id>/members", methods=["POST"])
@secured(JWT_SECRET)
def add_game_member(game_id: str) -> flask.Response:
    return controller.add_game_member(game_id)


@app.route("/v1/games/shortcode/<short_code>", methods=["GET"])
@secured(JWT_SECRET)
def get_game_by_shortcode(short_code: str) -> flask.Response:
    return http.create_ok_response()


@app.route("/v1/games/<game_id>", methods=["GET"])
@secured(JWT_SECRET)
def get_game(game_id: str) -> flask.Response:
    return controller.get_game(game_id)


@app.route("/v1/games/<game_id>/members/<member_id>/ready", methods=["PUT"])
@secured(JWT_SECRET)
def set_user_ready(game_id: str, member_id: str) -> flask.Response:
    return controller.set_game_member_as_ready(game_id, member_id)


@app.route("/v1/games/<game_id>", methods=["DELETE"])
@secured(JWT_SECRET)
def delete_game(game_id: str) -> flask.Response:
    return controller.delete_game(game_id)


@app.route("/v1/games/<game_id>/start", methods=["PUT"])
@secured(JWT_SECRET)
def start_game(game_id: str) -> flask.Response:
    return controller.start_game(game_id)


@app.route("/v1/games/<game_id>/members/<member_id>/leave", methods=["PUT"])
@secured(JWT_SECRET)
def leave_game(game_id: str, member_id: str) -> flask.Response:
    return controller.leave_game(game_id, member_id)


@app.route("/v1/games/<game_id>/members/<member_id>/next-question", methods=["GET"])
@secured(JWT_SECRET)
def get_current_question(game_id: str, member_id: str) -> flask.Response:
    return controller.get_members_next_question(game_id, member_id)


@app.route("/v1/games/<game_id>/members/<member_id>/position", methods=["POST"])
@secured(JWT_SECRET)
def add_user_position(game_id: str, member_id: str) -> flask.Response:
    return controller.add_position(game_id, member_id)


@app.route("/v1/questions/<question_id>", methods=["GET"])
@secured(JWT_SECRET)
def get_question(question_id: str) -> flask.Response:
    return controller.get_question(question_id)


@app.route("/v1/questions", methods=["POST"])
@secured(JWT_SECRET, roles=["ADMIN"])
def create_question() -> flask.Response:
    return controller.add_question()


@app.route("/health", methods=["GET"])
def check_health() -> flask.Response:
    return controller.check_health()


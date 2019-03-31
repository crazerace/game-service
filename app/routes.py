# Standard library
from typing import Any, Dict

# 3rd party modules.
import flask
from crazerace import http

# Internal modules
from app import app
from app import controller


# Create game
@app.route("/v1/games", methods=["POST"])
def create_game() -> flask.Response:
    return controller.create_game()


# Add members to a game
@app.route("/v1/games/<game_id>/members", methods=["POST"])
def add_game_member(game_id: str) -> flask.Response:
    return http.create_ok_response()


# Get all state info about a game
@app.route("/v1/games/<game_id>", methods=["GET"])
def get_game(game_id: str) -> flask.Response:
    return http.create_ok_response()


# When all users are ready, game will start.
@app.route("/v1/games/<game_id>/members/<member_id>/ready", methods=["PUT"])
def set_user_ready(game_id: str, member_id: str) -> flask.Response:
    return http.create_ok_response()


# Game master ends game
@app.route("/v1/games/<game_id>/ended", methods=["PUT"])
def end_game(game_id: str) -> flask.Response:
    return http.create_ok_response()


# Get members next question id
@app.route("/v1/games/<game_id>/members/<member_id>/question", methods=["GET"])
def get_current_question(game_id: str, member_id: str) -> flask.Response:
    return http.create_ok_response()


# Update position
@app.route("/v1/games/<game_id>/members/<member_id>/position", methods=["POST"])
def add_user_position(game_id: str, member_id: str) -> flask.Response:
    return http.create_ok_response()


# Get question
@app.route("/v1/questions/<question_id>", methods=["GET"])
def get_question(question_id: str) -> flask.Response:
    return http.create_ok_response()


# Create question
@app.route("/v1/questions", methods=["POST"])
def create_question(question_id: str) -> flask.Response:
    return http.create_ok_response()


@app.route("/health", methods=["GET"])
def check_health() -> flask.Response:
    return controller.check_health()


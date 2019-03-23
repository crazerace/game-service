# Standard library
from typing import Dict, List
from uuid import uuid4

# 3rd party modules
from flask.testing import FlaskClient
from crazerace import jwt

# Internal modules
from app import app
from app import db
from app.config import JWT_SECRET


JSON: str = "application/json"


def new_id() -> str:
    return str(uuid4()).lower()


def insert_items(items: List[db.Model]) -> None:
    for item in items:
        db.session.add(item)
    db.session.commit()


def headers(user_id: str, role: str = "USER") -> Dict[str, str]:
    jwt_token = jwt.create_token(user_id, role, JWT_SECRET)
    return {
        "Authorization": f"Bearer {jwt_token}",
        "Accepted": JSON,
        "Content-Type": JSON,
    }


class TestEnvironment:
    def __init__(self, items: List[db.Model] = []) -> None:
        self.client = app.test_client()
        self.items = items

    def __enter__(self) -> FlaskClient:
        db.create_all()
        insert_items(self.items)
        return self.client

    def __exit__(self, type, value, traceback) -> None:
        db.drop_all()


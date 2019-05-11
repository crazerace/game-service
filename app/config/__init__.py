# Standard library
import os
from logging.config import dictConfig

# Internal modules
from .logging import LOGGING_CONIFG


dictConfig(LOGGING_CONIFG)


SERVICE_NAME: str = "game-service"
SERVICE_VERSION: str = "0.1"
SERVER_NAME: str = f"{SERVICE_NAME}/{SERVICE_VERSION}"
REQUEST_ID_HEADER: str = "X-Request-ID"
TEST_MODE: bool = os.getenv("TEST_MODE", "0") == "1"
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"
JWT_SECRET: str = os.environ["JWT_SECRET"]
DEFAULT_NO_QUESTIONS: int = 3
DEFAULT_MIN_DISTANCE: int = 1000
DEFAULT_MAX_DISTANCE: int = 3000


class AppConfig:
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


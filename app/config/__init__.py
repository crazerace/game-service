# Standard library
import os
from logging.config import dictConfig

# Internal modules
from .logging import LOGGING_CONIFG
from .util import get_dsn


dictConfig(LOGGING_CONIFG)


SERVICE_NAME: str = "game-service"
SERVICE_VERSION: str = "1.0-RC"
SERVER_NAME: str = f"{SERVICE_NAME}/{SERVICE_VERSION}"
TEST_MODE: bool = os.getenv("TEST_MODE", "0") == "1"
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"
JWT_SECRET: str = os.environ["JWT_SECRET"]
USER_SERVICE_URL: str = os.environ["USER_SERVICE_URL"]
DEFAULT_NO_QUESTIONS: int = 3
DEFAULT_MIN_DISTANCE: int = 1000
DEFAULT_MAX_DISTANCE: int = 3000
MAX_ANSWER_DISTANCE: int = 10

USER_CACHE_SIZE: int = int(os.getenv("USER_CACHE_SIZE", "1000"))
USER_CACHE_TTL: int = int(os.getenv("USER_CACHE_TTL", "600"))


class AppConfig:
    SQLALCHEMY_DATABASE_URI: str = get_dsn(TEST_MODE)
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


# Standard library
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

# 3rd party libraries
from crazerace.http.error import BadRequestError


@dataclass
class QuestionText:
    id: str
    text: str
    text_en: str
    created_at: datetime

    def todict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "text": self.text,
            "text_en": self.text_en,
            "created_at": f"{self.created_at}",
        }


@dataclass
class QuestionDTO:
    id: str
    latitude: float
    longitude: float
    text: str
    text_en: str
    answer: str
    answer_en: str
    created_at: datetime

    @classmethod
    def fromdict(cls, raw: Dict[str, Any]) -> "QuestionDTO":
        question_id = raw.get("id") or _new_id()
        latitude = raw["latitude"]
        longitude = raw["longitude"]
        text = raw["text"]
        text_en = raw["text_en"]
        answer = raw["answer"]
        answer_en = raw["answer_en"]

        if not (
            isinstance(question_id, str)
            and isinstance(latitude, float)
            and isinstance(longitude, float)
            and isinstance(text, str)
            and isinstance(text_en, str)
            and isinstance(answer, str)
            and isinstance(answer_en, str)
        ):
            raise BadRequestError("Incorrect field types")
        return cls(
            id=question_id,
            latitude=latitude,
            longitude=longitude,
            text=text,
            text_en=text_en,
            answer=answer,
            answer_en=answer_en,
            created_at=datetime.utcnow(),
        )

    def todict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "text": self.text,
            "text_en": self.text_en,
            "answer": self.answer,
            "answer_en": self.answer_en,
            "created_at": f"{self.created_at}",
        }

    def only_question(self) -> QuestionText:
        return QuestionText(
            id=self.id, text=self.text, text_en=self.text_en, created_at=self.created_at
        )


@dataclass
class CreateGameDTO:
    game_id: str
    name: str
    created_at: datetime

    @classmethod
    def fromdict(cls, raw: Dict[str, Any]) -> "CreateGameDTO":
        name = raw["name"]
        if not (isinstance(name, str)):
            raise BadRequestError("Incorrect field types")
        return cls(game_id=raw.get("id") or _new_id(), name=name, created_at=datetime.utcnow())


@dataclass
class GameMemberDTO:
    id: str
    game_id: str
    user_id: str
    is_admin: bool
    is_ready: bool
    created_at: datetime

    def todict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "gameId": self.game_id,
            "userId": self.user_id,
            "isAdmin": self.is_admin,
            "isReady": self.is_ready,
            "createdAt": f"{self.created_at}",
        }


@dataclass
class GameDTO:
    id: str
    name: str
    questions: int
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    members: List[GameMemberDTO]

    def status(self) -> str:
        if self.ended_at:
            return "ENDED"
        if self.started_at:
            return "STARTED"
        return "CREATED"

    def todict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "questions": self.questions,
            "status": self.status(),
            "createdAt": f"{self.created_at}",
            "startedAt": f"{self.started_at}" if self.started_at else None,
            "endedAt": f"{self.ended_at}" if self.ended_at else None,
            "members": [m.todict() for m in self.members],
        }


def _new_id() -> str:
    return str(uuid4()).lower()

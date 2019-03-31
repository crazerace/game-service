# Standard library
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
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
        if not(
            isinstance(name, str)
        ):
            raise BadRequestError("Incorrect field types")
        return cls(
            game_id = raw.get("id") or _new_id(),
            name=name,
            created_at=datetime.utcnow(),
        )



def _new_id() -> str:
    return str(uuid4()).lower()

# Standard library
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

# 3rd party libraries
from crazerace.http.error import BadRequestError


@dataclass
class QuestionDTO:
    latitude: float
    longitude: float
    text: str
    text_en: str
    answer: str
    answer_en: str
    created_at: datetime

    @classmethod
    def fromdict(cls, raw: Dict[str, Any]) -> "QuestionDTO":
        latitude = raw["latitude"]
        longitude = raw["longitude"]
        text = raw["text"]
        text_en = raw["text_en"]
        answer = raw["answer"]
        answer_en = raw["answer_en"]

        if not (
            isinstance(latitude, float)
            and isinstance(longitude, float)
            and isinstance(text, str)
            and isinstance(text_en, str)
            and isinstance(answer, str)
            and isinstance(answer_en, str)
        ):
            raise BadRequestError("Incorrect field types")
        return cls(
            latitude=latitude,
            longitude=longitude,
            text=text,
            text_en=text_en,
            answer=answer,
            answer_en=answer_en,
            created_at=datetime.utcnow(),
        )

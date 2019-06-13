# Standard library
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

# Internal modules
from app import db
from .dto import CoordinateDTO


class Position(db.Model):  # type: ignore
    __tablename__ = "game_member_position"
    id: str = db.Column(db.String(50), primary_key=True)
    game_member_id: str = db.Column(
        db.String(50), db.ForeignKey("game_member.id"), nullable=False
    )
    latitude: float = db.Column(db.Float, nullable=False)
    longitude: float = db.Column(db.Float, nullable=False)
    created_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"Position(id={self.id} "
            f"game_member_id={self.game_member_id} "
            f"latitude={self.latitude} "
            f"longitude={self.longitude} "
            f"created_at={self.created_at})"
        )

    def coordinate(self) -> CoordinateDTO:
        return CoordinateDTO(latitude=self.latitude, longitude=self.longitude)


class GameMemberQuestion(db.Model):  # type: ignore
    __table_args__ = (
        db.UniqueConstraint(
            "member_id", "game_question_id", name="unique_member_id_game_question_id"
        ),
    )
    id: int = db.Column(db.Integer, primary_key=True)
    member_id: str = db.Column(
        db.String(50), db.ForeignKey("game_member.id"), nullable=False
    )
    game_question_id: int = db.Column(
        db.Integer, db.ForeignKey("game_question.id"), nullable=False
    )
    position_id: Optional[str] = db.Column(
        db.String(50), db.ForeignKey("game_member_position.id"), nullable=True
    )
    answered_at: Optional[datetime] = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"GameMemberQuestion(id={self.id} "
            f"member_id={self.member_id} "
            f"game_question_id={self.game_question_id} "
            f"answer_position_id={self.answer_position_id} "
            f"answered_at={self.answered_at} "
            f"created_at={self.created_at})"
        )


class GameMember(db.Model):  # type: ignore
    __table_args__ = (
        db.UniqueConstraint("game_id", "user_id", name="unique_game_id_user_id"),
    )
    id: str = db.Column(db.String(50), primary_key=True)
    game_id: str = db.Column(db.String(50), db.ForeignKey("game.id"), nullable=False)
    user_id: str = db.Column(db.String(50), nullable=False)
    is_admin: bool = db.Column(db.Boolean, nullable=False, default=False)
    is_ready: bool = db.Column(db.Boolean, nullable=False, default=False)
    resigned_at: Optional[datetime] = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    positions: List[Position] = db.relationship(
        "Position", backref="game_member", lazy=True
    )
    questions: List[GameMemberQuestion] = db.relationship(
        "GameMemberQuestion", backref="game_member", lazy=True
    )

    def __repr__(self) -> str:
        return (
            f"GameMember(id={self.id} "
            f"game_id={self.game_id} "
            f"user_id={self.user_id} "
            f"is_admin={self.is_admin} "
            f"created_at={self.created_at})"
        )


class Question(db.Model):  # type: ignore
    id: str = db.Column(db.String(50), primary_key=True)
    latitude: float = db.Column(db.Float, nullable=False)
    longitude: float = db.Column(db.Float, nullable=False)
    text: str = db.Column(db.Text, nullable=False)
    text_en: str = db.Column(db.Text, nullable=False)
    answer: str = db.Column(db.Text, nullable=False)
    answer_en: str = db.Column(db.Text, nullable=False)
    created_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"Question(id={self.id} "
            f"latitude={self.latitude} "
            f"longitude={self.longitude} "
            f"text={self.text} "
            f"text_en={self.text_en} "
            f"answer={self.answer} "
            f"answer_en={self.answer_en} "
            f"created_at={self.created_at})"
        )

    def coordinate(self) -> CoordinateDTO:
        return CoordinateDTO(latitude=self.latitude, longitude=self.longitude)


class GameQuestion(db.Model):  # type: ignore
    id: int = db.Column(db.Integer, primary_key=True)
    game_id: str = db.Column(db.String(50), db.ForeignKey("game.id"), nullable=False)
    question_id: str = db.Column(
        db.String(50), db.ForeignKey("question.id"), nullable=False
    )

    def __repr__(self) -> str:
        return f"GameQuestion(game_id={self.game_id} question_id={self.question_id})"


class Placement(db.Model):  # type: ignore
    __tablename__ = "game_placement"
    __table_args__ = (
        db.UniqueConstraint("game_id", "member_id", name="unique_game_id_member_id"),
    )
    id: int = db.Column(db.Integer, primary_key=True)
    game_id: str = db.Column(db.String(50), db.ForeignKey("game.id"), nullable=False)
    member_id: str = db.Column(
        db.String(50), db.ForeignKey("game_member.id"), nullable=False
    )
    created_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"Placement(id={self.id}, "
            f"game_id={self.game_id}, "
            f"member_id={self.member_id}, "
            f"created_at={self.created_at})"
        )


class Game(db.Model):  # type: ignore
    id: str = db.Column(db.String(50), primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)
    started_at: Optional[datetime] = db.Column(db.DateTime, nullable=True)
    ended_at: Optional[datetime] = db.Column(db.DateTime, nullable=True)
    created_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    questions: List[GameQuestion] = db.relationship(
        "GameQuestion", backref="game", lazy=True
    )
    members: List[GameMember] = db.relationship("GameMember", backref="game", lazy=True)
    placements: List[Placement] = db.relationship("Placement", backref="game", lazy=True)

    def __repr__(self) -> str:
        return (
            f"Game(id={self.id}, "
            f"name={self.name}, "
            f"started_at={self.started_at}, "
            f"ended_at={self.ended_at}, "
            f"created_at={self.created_at})"
        )

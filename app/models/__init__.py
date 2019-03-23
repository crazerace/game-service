#standard libraries
from datetime import DateTime

# Internal modules
from app import db

class Game(db.Model): #type: ignore
	id: str = db.Column(db.String(50), primary_key=True)
	name: str = db.Column(db.String(100), nullable=False)
	first: str = db.Column(db.String(100), nullable=True)
	second: str = db.Column(db.String(100), nullable=True)
	third: str = db.Column(db.String(100), nullable=True)
	started_at: datetime = db.Column(db.DateTime, nullable=True)
	ended_at: datetime = db.Column(db.DateTime, nullable=True)
	created_at: datetime = db.Column( 
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return (
            f"Game(id={self.id} \
          	name={self.name} \
            first={self.first} \
            second={self.second} \
            third={self.third} \
            started_at={self.started_at} \
            ended_at={self.ended_at} \
            created_at={self.created_at})"
        )


class GameMember(db.Model):  #type: ignore
	id: str = db.Column(db.String(50), primary_key=True)
	game_id: str = db.Column(db.String(50), nullable=False)
	user_id: str = db.Column(db.String(50), nullable=False)
	created_at: datetime = db.Column( 
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
    	return (
    		f"GameMember(id={self.id} \
    		game_id={self.game_id} \
    		user_id={self.user_id} \
    		created_at={self.created_at})"
    		)


class GameMemberPosition(db.Model): #type: ignore
	id: str = db.Column(db.String(50), primary_key=True)
	game_member_id: str = db.Column(db.String(50), primary_key=True)
	latitude: float = db.Column(db.Float, nullable=False)
	longitude: float = db.Column(db.Float, nullable=False)
	created_at: datetime = db.Column( 
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
    	return(
    		f"GameMemberPosition(id={self.id} \
    		game_member_id={self.game_member_id} \
    		latitude={self.latitude} \
    		longitude={self.longitude} \
    		created_at={self.created_at})"
    		)


class GameQuestion(db.Model): #type: ignore
	game_id: str = db.Column(db.String(50), nullable=False)
	question_id: str = db.Column(db.String(50), nullable=False)

	def __repr__(self) -> str:
		return(f"GameQuestion(game_id={self.game_id} question_id={self.question_id})")


class Question(db.Model): #type: ignore
	id: str = db.Column(db.String(50), primary_key=True)
	latitude: float = db.Column(db.Float, nullable=False)
	longitude: float = db.Column(db.Float, nullable=False)
	text: str = db.Column(db.Text, nullable=False)
	text_en: str = db.Column(db.Text, nullable=False)
	answer: str = db.Column(db.Text, nullable=False)
	answer_en str = db.Column(db.Text, nullable=False)
	created_at: datetime = db.Column( 
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
    	return(
    		f"Question(id={self.id} \
    		latitude={self.latitude} \
    		longitude={self.longitude} \
    		text={self.text} \
    		text_en={self.text_en} \
    		answer={self.answer} \
    		answer_en={self.answer_en} \
    		created_at={self.created_at}"
    		)




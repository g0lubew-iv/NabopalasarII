import sqlalchemy
import datetime

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

boards_to_users = sqlalchemy.Table("boards_to_users", SqlAlchemyBase.metadata,
                                   sqlalchemy.Column("board", sqlalchemy.Integer, sqlalchemy.ForeignKey("boards.id")),
                                   sqlalchemy.Column("user", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")))

boards_to_threads = sqlalchemy.Table("boards_to_threads", SqlAlchemyBase.metadata,
                                     sqlalchemy.Column("board", sqlalchemy.Integer, sqlalchemy.ForeignKey("boards.id")),
                                     sqlalchemy.Column("thread", sqlalchemy.Integer,
                                                       sqlalchemy.ForeignKey("threads.id")))

boards_to_messages = sqlalchemy.Table("boards_to_messages", SqlAlchemyBase.metadata,
                                      sqlalchemy.Column("board", sqlalchemy.Integer,
                                                        sqlalchemy.ForeignKey("boards.id")),
                                      sqlalchemy.Column("message", sqlalchemy.Integer,
                                                        sqlalchemy.ForeignKey("messages.id")))


class Boards(SqlAlchemyBase, SerializerMixin):
	__tablename__ = "boards"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	admin = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
	title = sqlalchemy.Column(sqlalchemy.String)
	about_board = sqlalchemy.Column(sqlalchemy.String, default="")
	board_users = orm.relation("User", secondary=boards_to_users, backref="user_boards")
	board_threads = orm.relation("Threads", secondary=boards_to_threads, backref="thread_boards")
	user_events = orm.relationship("UserEvents", backref="board_event")
	team_events = orm.relationship("TeamEvents", backref="board_event")
	messages_buffer = orm.relationship("Message", secondary=boards_to_messages, backref="msg_buffer")

	def __repr__(self):
		return "Board " + self.title


class Message(SqlAlchemyBase, SerializerMixin):
	__tablename__ = "messages"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	sender_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
	timestamp = sqlalchemy.Column(sqlalchemy.String, default=str(datetime.datetime.utcnow()))
	body = sqlalchemy.Column(sqlalchemy.String(200))
	html = sqlalchemy.Column(sqlalchemy.String)

	def __repr__(self):
		return f"<Message {self.body}>"

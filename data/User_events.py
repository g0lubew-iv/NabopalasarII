import sqlalchemy

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

events_to_users = sqlalchemy.Table("events_to_users", SqlAlchemyBase.metadata,
                                   sqlalchemy.Column("event", sqlalchemy.Integer,
                                                     sqlalchemy.ForeignKey("user_events.id")),
                                   sqlalchemy.Column("user", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")))


class UserEvents(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "user_events"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    board = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("boards.id"))
    title = sqlalchemy.Column(sqlalchemy.String)
    about = sqlalchemy.Column(sqlalchemy.String)
    users = orm.relation("User", secondary=events_to_users, backref="user_events")
    html = sqlalchemy.Column(sqlalchemy.String)  # html forms of the team event

    def __repr__(self):
        return "Мероприятие " + self.title

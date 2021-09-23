import sqlalchemy

from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Threads(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "threads"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    icon = sqlalchemy.Column(sqlalchemy.String)

    def __str__(self):
        return self.title

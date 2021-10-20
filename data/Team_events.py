import sqlalchemy

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase

team_to_team_events = sqlalchemy.Table("team_to_team_events", SqlAlchemyBase.metadata,
                                       sqlalchemy.Column("team", sqlalchemy.Integer, sqlalchemy.ForeignKey("teams.id")),
                                       sqlalchemy.Column("event", sqlalchemy.Integer,
                                                         sqlalchemy.ForeignKey("team_events.id")))


class TeamEvents(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "team_events"

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    board = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("boards.id"))
    title = sqlalchemy.Column(sqlalchemy.String)
    about = sqlalchemy.Column(sqlalchemy.String)
    teams = orm.relation("Team", secondary=team_to_team_events, backref="team_events")
    html = sqlalchemy.Column(sqlalchemy.String)  # html forms of the team event

    def __repr__(self):
        return "Team event " + self.title

from sqlalchemy import orm

from .db_session import SqlAlchemyBase

import sqlalchemy
import datetime


teams_to_users = sqlalchemy.Table("teams_to_users", SqlAlchemyBase.metadata,
                                  sqlalchemy.Column("team", sqlalchemy.Integer, sqlalchemy.ForeignKey("teams.id")),
                                  sqlalchemy.Column("user", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")))


class Team(SqlAlchemyBase):
    __tablename__ = "teams"
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    chief = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    title = sqlalchemy.Column(sqlalchemy.String, unique=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    avatar = sqlalchemy.Column(sqlalchemy.String, default="../static/img/teams/temp_team_image.jpg")
    users = orm.relation("User", secondary=teams_to_users, backref="user_teams")
    
    def __repr__(self):
        return self.title

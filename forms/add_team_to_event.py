from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

from data.db_session import SqlAlchemyBase


class AddTeam(Form):
    teams = SelectField("Team", choices=[], validators=[DataRequired()])
    submit = SubmitField("Register a team", default=False)

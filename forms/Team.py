from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

from data.db_session import SqlAlchemyBase
from data.Team import Team


class TeamRegisterForm(Form):
	chief = IntegerField("Chief's username", validators=[DataRequired()])
	title = StringField("Team name", validators=[DataRequired()])
	users = []
	submit = SubmitField("Create team", default=False)

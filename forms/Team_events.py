from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

from data.db_session import SqlAlchemyBase


class FormTeamEvent(Form):
    title = StringField("Events name", validators=[DataRequired()])
    about = StringField("About event", validators=[DataRequired()])
    submit = SubmitField("Create event", default=False)


class FormTeamEventEdit(Form):
    title = StringField("Events name", validators=[DataRequired()])
    about = StringField("About event", validators=[DataRequired()])
    submit = SubmitField("Edit event", default=False)

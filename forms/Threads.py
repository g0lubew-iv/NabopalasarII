from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

from data.db_session import SqlAlchemyBase


class FormThreads(Form):
    title = StringField("Thread name", validators=[DataRequired()])
    submit = SubmitField("Create thread", default=False)

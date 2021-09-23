from wtforms import StringField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

from data.db_session import SqlAlchemyBase


class FormBoardsCreate(Form):
    title = StringField("Board name", validators=[DataRequired()])
    about_board = TextAreaField("About Board")
    admin = IntegerField("Board Admin")
    submit = SubmitField("Create board", default=False)


class FormBoardsEdit(Form):
    title = StringField("Board name", validators=[DataRequired()])
    about_board = TextAreaField("About Board")
    submit = SubmitField("Edit board", default=False)

from flask_wtf.file import FileAllowed
from wtforms import PasswordField, StringField, SubmitField, BooleanField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from wtforms_tornado import Form

from data.db_session import SqlAlchemyBase
from data.User import User


class LoginForm(Form):
    email = EmailField("Email address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me", default=False)
    submit = SubmitField("Sign in", default=False)


class RegisterForm(Form):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email address", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_again = PasswordField("Repeat password, please", validators=[DataRequired()])
    submit = SubmitField("Sign up", default=False)


class DecorateForm(Form):
    name = StringField("Name")
    surname = StringField("Surname")
    is_reads = SubmitField("Email preferences", default=False)
    avatar = FileField(
        "Avatar (optional)",
        validators=[FileAllowed(["jpg", "jpeg", "png"],
                                "The file must be in one of these formats: '.jpg', '.png', '.jpeg'")])
    submit = SubmitField("Edit profile", default=False)

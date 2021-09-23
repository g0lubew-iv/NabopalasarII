from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

import sqlalchemy
import datetime

ntfs_to_users = sqlalchemy.Table(
	"ntfs_to_users", SqlAlchemyBase.metadata,
	sqlalchemy.Column("notification", sqlalchemy.Integer, sqlalchemy.ForeignKey("notifications.id")),
	sqlalchemy.Column("user", sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id")))


class User(SqlAlchemyBase):
	__tablename__ = "users"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	username = sqlalchemy.Column(sqlalchemy.String, unique=True)
	name = sqlalchemy.Column(sqlalchemy.String, default="")
	surname = sqlalchemy.Column(sqlalchemy.String, default="")
	email = sqlalchemy.Column(sqlalchemy.String, unique=True)
	hashed_password = sqlalchemy.Column(sqlalchemy.String)
	modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
	avatar = sqlalchemy.Column(sqlalchemy.String, default="../static/img/users/temp_image.jpg")
	is_confirmed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
	is_reads = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
	boards = orm.relationship("Boards", backref='board_admin')
	teams = orm.relationship("Team", backref='team_leader')
	notifications = orm.relationship("Notification", secondary=ntfs_to_users, backref="user_notifications")

	def __repr__(self):
		return self.username

	def set_password(self, password):
		self.hashed_password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.hashed_password, password)


class Notification(SqlAlchemyBase):
	__tablename__ = "notifications"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	name = sqlalchemy.Column(sqlalchemy.String(256), index=True)
	timestamp = sqlalchemy.Column(sqlalchemy.String, default=str(datetime.datetime.utcnow()))
	payload_json = sqlalchemy.Column(sqlalchemy.Text)
	is_read = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

	def get_data(self):
		import json
		return json.loads(str(self.payload_json))

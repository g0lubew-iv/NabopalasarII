import tornado.web
import tornado.auth
import tornado.locks
import tornado.escape
import tornado.ioloop
import tornado
import datetime
import random
import pytz
import json
import os

from abc import ABC
from decouple import config
from tornado.options import options, define

from token_n import generate_confirmation_token, confirm_token
from EmailSender import send_email
from data import db_session
from data.User import User, Notification
from data.Team import Team
from data.Boards import Boards, Message
from data.Threads import Threads
from data.User_events import UserEvents
from data.Team_events import TeamEvents

from forms.User import LoginForm, RegisterForm
from forms.Team import TeamRegisterForm
from forms.Boards import FormBoardsCreate

from sqlalchemy.ext.declarative import DeclarativeMeta


class AlchemyEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj.__class__, DeclarativeMeta):
			# an SQLAlchemy class
			fields = {}
			for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
				data = obj.__getattribute__(field)
				try:
					json.dumps(data)  # this will fail on non-encodable values, like other classes
					fields[field] = data
				except TypeError:
					fields[field] = None
			# a json-encodable dict
			return fields
		return json.JSONEncoder.default(self, obj)


define("port", default=int(os.environ.get("PORT", 5000)), help="run on the given port", type=int)
CACHE_SIZE = 50  # Maximum number of messages on the board


async def append_to_team(user_invited: User, team: Team) -> None:
	token = generate_confirmation_token(user_invited.email)
	db_sess = db_session.create_session()
	user = db_sess.query(User).filter(team.chief == User.id).first()
	ntf = Notification(
		name=f"Invitation to join the team &nbsp; <b>{team.title}</b>",
		payload_json=json.dumps(""),
		timestamp=str(datetime.datetime.now(pytz.timezone('Europe/Moscow')))
	)
	ntf.payload_json = json.dumps(
		f"Warm sun over your head, Sumer {user_invited.username}!\n" + f"You were invited by <a href='/{user.username}' style='color:black;'>{user.username}</a> to the <a href='/teams' style='color:black;'>{team.title}</a> team. " + f"If you want to accept the invitation, then follow <a href='/invite_team/{token}_____{team.title}_____{ntf.timestamp}' style='color:black;'>this link</a>")
	user_invited.notifications.append(ntf)
	db_sess.commit()


async def join_to_board(user_asked: User, board: Boards):
	db_sess = db_session.create_session()
	user_admin = db_sess.query(User).filter(board.admin == User.id).first()
	token = generate_confirmation_token(user_admin.email)
	ntf = Notification(
		name=f"Request to join the board &nbsp; <b>{board.title}</b>",
		payload_json=json.dumps(""),
		timestamp=str(datetime.datetime.now(pytz.timezone('Europe/Moscow')))
	)
	ntf.payload_json = json.dumps(
		f"Warm sun over your head, Sumer {user_admin.username}!\n" + f"You are asked by <a href='/{user_asked.username}' style='color:black;'>{user_asked.username}</a> to add his (her) to your board {board.title}. " + f"If you want to do this, then follow <a href='/invite_board/{token}_____{board.title}_____{ntf.timestamp}_____{user_asked.username}' style='color:black;'>this link</a>")
	user_admin.notifications.append(ntf)
	db_sess.commit()


async def notify_join_team(user_invited: User, team: Team) -> None:
	db_sess = db_session.create_session()
	user = db_sess.query(User).filter(team.chief == User.id).first()
	ntf = Notification(
		name=f"Notification of joining the team &nbsp; <b>{team.title}</b>",
		payload_json=json.dumps(""),
		timestamp=str(datetime.datetime.now(pytz.timezone('Europe/Moscow')))
	)
	ntf.payload_json = json.dumps(
		f"Warm sun over your head, Sumer {user.username}!\n" + f"User <a href='/{user_invited.username}' style='color:#000000;'>{user_invited.username}</a> has just accepted your application to join the team!\n" + "Congratulations!")
	user.notifications.append(ntf)
	db_sess.commit()


async def notify_join_board(user_asked: User, board: Boards):
	db_sess = db_session.create_session()
	ntf = Notification(
		name=f"Request to join the board &nbsp; <b>{board.title}</b>",
		payload_json=json.dumps(""),
		timestamp=str(datetime.datetime.now(pytz.timezone('Europe/Moscow')))
	)
	ntf.payload_json = json.dumps(
		f"Warm sun over your head, Sumer {user_asked.username}!\nYour request to join the board <a href='/board/{board.title}/view' style='color:#000000;'>{board.title}</a> has been accepted!\nCongratulations!")
	user_asked.notifications.append(ntf)
	db_sess.commit()


class Application(tornado.web.Application):
	def __init__(self, db=None):
		self.db = db
		handlers = [
			# Home page
			(r"/", HomeHandler),
			# For fun
			(r"/generate_error/\d\d\d", ErrorGenerator),
			(r"/chess$", ChessHandler),
			(r"/runner$", RunnerHandler),
			(r"/scrolling$", ScrollingHandler),
			# Pages related to user invite
			(r"/invite_team/\S+", InviteTeamHandler),
			(r"/invite_board/\S+", InviteBoardHandler),
			# Pages related to the site policy
			(r"/legal", LegalHandler),
			(r"/legal/cookie-policy", LegalCookiePolicyHandler),
			# Pages related to user authorization
			(r"/auth/create", AuthCreateHandler),
			(r"/auth/login", AuthLoginHandler),
			(r"/auth/logout", AuthLogoutHandler),
			(r"/auth/confirm", AuthConfirmHandler),
			(r"/auth/confirm/\S+", AuthCheckConfirmHandler),
			# Pages related to teams
			(r"/teams", TeamsHandler),
			(r"/team/\S+/edit$", TeamEditHandler),
			(r"/team/\S+/leave$", TeamLeaveHandler),
			# Pages related to boards
			(r"/boards", BoardsHandler),
			(r"/board/\S+/view$", BoardViewHandler),
			(r"/board/\S+/edit$", BoardEditHandler),
			(r"/board/\S+/leave$", BoardLeaveHandler),
			(r"/board/\S+/delete$", BoardDeleteHandler),
			(r"/board/\S+/user_event/new", UserEventCreateHandler),
			(r"/board/\S+/team_event/new", TeamEventCreateHandler),
			(r"/board/\S+/user_event/\d+$", UserEventHandler),
			(r"/board/\S+/team_event/\d+$", TeamEventHandler),
			(r"/board/\S+/user_event/edit/\d+$", UserEventEditHandler),
			(r"/board/\S+/team_event/edit/\d+$", TeamEventEditHandler),
			(r"/board/\S+/user_event/view/\d+$", UserEventAnswersView),
			(r"/board/\S+/team_event/view/\d+$", TeamEventAnswersView),
			(r"/board/\S+/flood$", BoardFloodHandler),
			(r"/board/\S+/flood/new$", MessageNewHandler),
			# Pages related to personal account (personal teams, boards, notifications, etc)
			(r"/\S+/inbox$", UserInBoxHandler),
			(r"/\S+/inbox/check$", UserInBoxCheckHandler),
			(r"/\S+/inbox/delete$", UserInBoxDeleteHandler),
			(r"/\S+/teams$", UserTeamsHandler),
			(r"/\S+/boards$", UserBoardsHandler),
			(r"/\S+/create_team$", CreateTeamHandler),
			(r"/\S+/create_board$", CreateBoardHandler),
			(r"/\S+", UserAccountHandler),
		]
		settings = dict(
			title_=u"Nabopalasar II",
			template_path=os.path.join(os.path.dirname(__file__), "templates"),
			static_path=os.path.join(os.path.dirname(__file__), "static"),
			# ui_modules={"Paginator": PaginationHandler},
			xsrf_cookies=True,
			cookie_secret=config("SECRET_KEY"),
			login_url="/auth/login",
			debug=True,
		)
		super().__init__(handlers, **settings)


class BaseHandler(tornado.web.RequestHandler, ABC):
	async def prepare(self):
		db_sess = db_session.create_session()
		user_email = tornado.escape.native_str(self.get_secure_cookie("user"))
		if user_email:
			self.current_user = db_sess.query(User).filter(User.email == user_email).first()

	# Else cookies don't establish

	def write_error(self, status_code: int, **kwargs):
		if status_code == 404:
			self.render("error404.html")
		elif status_code == 500:
			self.render("error500.html")
		else:
			self.render("error_general.html", status_code=status_code)

	def check_match_user(self, user_: User) -> bool:
		return True if self.current_user.id == user_.id else False

	@staticmethod
	def get_user(username_: str, db_sess_) -> User:
		return db_sess_.query(User).filter(User.username == username_).first()

	@staticmethod
	def get_board(board_name: str, db_sess_) -> Boards:
		return db_sess_.query(Boards).filter(Boards.title == board_name).first()

	@staticmethod
	def get_team(team_name: str, db_sess_) -> Team:
		return db_sess_.query(Team).filter(Team.title == team_name).first()

	@staticmethod
	def get_team_event(event_id: str, db_sess_) -> TeamEvents:
		return db_sess_.query(TeamEvents).filter(TeamEvents.id == int(event_id)).first()

	@staticmethod
	def get_user_event(event_id: str, db_sess_) -> UserEvents:
		return db_sess_.query(UserEvents).filter(UserEvents.id == int(event_id)).first()

	@staticmethod
	async def get_dict_t(threads: list, board: Boards):
		dict_ts = {}
		for t in threads:
			if t in board.board_threads:
				dict_ts[t] = True
			else:
				dict_ts[t] = False
		return {key: value for key, value in sorted(dict_ts.items(), key=lambda item: item[1], reverse=True)}


class HomeHandler(BaseHandler, ABC):
	"""The home class that is primarily responsible for the navbar"""

	async def get(self):
		with open('auto/news.json', mode='r', encoding='utf-8') as f:
			data = json.load(f)
		# We don't want to not only lose, but also leave non-unique news
		await self.render("base.html", title="Home", news_=data['news'])


class AuthLoginHandler(BaseHandler, ABC):
	async def get(self):
		form = LoginForm(self.request.arguments)
		await self.render("auth_login.html", title="Authorization", message=None, form=form)

	async def post(self):
		form = LoginForm(self.request.arguments)
		if form.validate():
			db_sess = db_session.create_session()
			user = db_sess.query(User).filter(User.email == form.email.data).first()
			if user and user.check_password(form.password.data):
				self.set_secure_cookie("user", self.get_argument("email"))
				await self.prepare()
				self.redirect("/")
				return
			await self.render(
				"auth_login.html", title="Authorization error",
				message="Incorrect username or password", form=form
			)
		await self.render("auth_login.html", title="Authorization", message=None, form=form)


class AuthCreateHandler(BaseHandler, ABC):
	async def get(self):
		form = RegisterForm(self.request.arguments)
		await self.render(
			"auth_create.html", form=form, title="Sign Up", message_username=None, message_email=None,
			message_password=None, )

	def post(self):
		form = RegisterForm(self.request.arguments)
		if form.validate():
			if form.password.data != form.password_again.data:
				return self.render(
					"auth_create.html", title="Password Error", form=form, message_username=None,
					message_email=None, message_password="Passwords do not match")
			db_sess = db_session.create_session()
			if db_sess.query(User).filter(User.email == form.email.data).first():
				return self.render(
					"auth_create.html", title="Email Error", form=form, message_email=f"Email is already taken",
					message_username=None, message_password=None)
			if self.get_user(form.username.data, db_sess):
				return self.render(
					"auth_create.html", title="Username Error", form=form,
					message_username=f"Username {form.username.data} is not available",
					message_password=None, message_email=None)
			user = User(
				username=form.username.data,
				email=form.email.data,
				hashed_password=form.password_again.data,
				is_reads=False,
				is_confirmed=True  # Heroku does not like my email posts (
			)
			user.set_password(form.password.data)
			db_sess.add(user)
			db_sess.commit()
			self.set_secure_cookie("user", str(form.email.data))
			# self.current_user = str(form.email.data)
			# The user immediately logs in; now you need to confirm your email address
			# self.redirect("/auth/confirm")
			self.redirect("/")
			return
		return self.render(
			"auth_create.html", form=form, title="Registration Error", message_username=None,
			message_email=None, message_password=None)


class AuthLogoutHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		self.clear_cookie("user")
		self.redirect("/")


class AuthConfirmHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		if self.current_user.is_confirmed:
			# User already confirmed his email
			self.write_error(404)
		token = generate_confirmation_token(self.current_user.email)
		text_msg = f"Have a nice time of day, friend {self.current_user.username}!\n" \
		           f"Babylon is so beautiful today only because you are on our website.\n" \
		           f"However, to confirm your email address, you need to click on the following link:\n" \
		           f"{self.request.uri}/{token}\n" \
		           f"With best wishes,\n" \
		           f"akkadian team Nabopalasar II"
		try:
			# if send_email(
			# 		self.current_user.email, "Nabopalasar II: email confirmation", text_msg,
			# 		"../static/img/news/womans_img.jpg"):
			# 	await self.render("auth_confirm.html", title="Confirm", email=self.current_user.email, success=True)
			# 	return
			pass
		except Exception:
			await self.render("auth_confirm.html", title="Confirm", email=self.current_user.email, success=False)


class AuthCheckConfirmHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	def get(self):
		if self.current_user.is_confirmed:
			# User already confirmed his email
			self.write_error(404)
		token = self.request.uri.split("/")[-1]
		try:
			email = confirm_token(token)
		except Exception:
			self.write_error(404)
			return
		db_sess = db_session.create_session()
		user = db_sess.query(User).filter(User.email == email).first()
		if user.username != self.current_user.username:
			self.write_error(403)
			return
		if user.is_confirmed:
			self.write_error(404)
			return
		user.is_confirmed = True
		db_sess.add(user)
		db_sess.commit()
		self.redirect("/")
		return


class UserAccountHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		username = str(self.request.uri)[1:]
		if '/' in username:
			# It's another address
			self.write_error(404)
			return
		db_sess = db_session.create_session()
		user = self.get_user(username, db_sess)
		if not user:
			self.write_error(404)
			return
		teams_own = db_sess.query(Team).filter(Team.chief == self.current_user.id).all()
		boards_own = db_sess.query(Boards).filter(Boards.admin == self.current_user.id).all()
		await self.render("user_view.html", title=user.username, user=user, teams_own=teams_own, boards_own=boards_own)

	@tornado.web.authenticated
	def post(self):
		db_sess = db_session.create_session()
		user = self.get_user(str(self.request.uri)[1:], db_sess)
		user.name = self.get_body_argument("first_name")
		user.surname = self.get_body_argument("last_name")
		try:
			# If checkbox is deactivated then argument check_13 miss
			_ = self.get_body_argument("check_13")
			user.is_reads = True
		except Exception:
			user.is_reads = False
		f = self.request.files.get("avatar")
		if f:
			file_avatar = f[0]  # We use only 1 file
			filename = f"static/img/users/{file_avatar['filename']}"
			with open(filename, mode='wb') as file:
				file.write(file_avatar['body'])
			user.avatar = "../" + filename
		db_sess.commit()
		self.redirect(self.request.uri)
		return


class ErrorGenerator(BaseHandler, ABC):
	@tornado.web.authenticated
	def get(self):
		self.write_error(int(self.request.uri.split('/')[-1]))


class TeamsHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		teams = sorted(db_sess.query(Team).all(), key=lambda x: len(x.users), reverse=True)

		def get_cap(id_cap: int):
			return db_sess.query(User).filter(User.id == id_cap).first()

		await self.render("teams.html", title="Teams", teams=teams, get_cap=get_cap)


class BoardsHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		boards = sorted(db_sess.query(Boards).all(), key=lambda x: len(x.board_users), reverse=True)
		await self.render("boards.html", title="Boards", boards=boards, get_admin=get_admin)


class UserTeamsHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		username = str(self.request.uri).split('/')[-2]
		db_sess = db_session.create_session()
		user = self.get_user(username, db_sess)
		if not user:
			self.write_error(404)
			return
		if user.username != self.current_user.username:
			# We cannot watch teams other user
			self.write_error(403)
			return
		teams_own = db_sess.query(Team).filter(Team.chief == self.current_user.id).all()
		teams = db_sess.query(Team).all()
		teams_in = []
		for t in teams:
			for user_ in t.users:
				if user_.username == self.current_user.username:
					teams_in.append(t)

		def get_cap(id_cap: int):
			return db_sess.query(User).filter(User.id == id_cap).first()

		await self.render(
			"user_teams.html", title="Your teams", own_teams=teams_own, in_teams=teams_in,
			get_cap=get_cap)


class LegalHandler(BaseHandler, ABC):
	async def get(self):
		await self.render("about.html", title="About")


class LegalCookiePolicyHandler(BaseHandler, ABC):
	async def get(self):
		await self.render("cookies_about.html", title="Cookie Policy")


class UserBoardsHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		username = str(self.request.uri).split('/')[-2]
		db_sess = db_session.create_session()
		user = self.get_user(username, db_sess)
		if not user:
			self.write_error(404)
			return
		if user.username != self.current_user.username:
			# We cannot watch teams other user
			self.write_error(403)
			return
		boards_own = db_sess.query(Boards).filter(Boards.admin == self.current_user.id).all()
		boards = db_sess.query(Boards).all()
		boards_in = []
		for b in boards:
			for user_ in b.board_users:
				if user_.username == self.current_user.username:
					boards_in.append(b)
		await self.render(
			"user_boards.html", title="Your boards", own_boards=boards_own, in_boards=boards_in,
			get_admin=get_admin)


class TeamEditHandler(BaseHandler, ABC):
	def get_res_sort(self, db_sess, team: Team):
		res = db_sess.query(User).filter(User.id != self.current_user.id).all()
		keys = []
		for user in res:
			if user in team.users:
				keys.insert(0, user)
			else:
				keys.append(user)
		res_sort = {}
		for key in keys:
			if key in team.users:
				res_sort[key] = 1
			else:
				res_sort[key] = 0

	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		team = self.get_team(self.request.uri.split('/')[-2], db_sess)
		if not team:
			self.write_error(404)
			return
		if self.current_user.id != team.chief:
			self.write_error(403)
			return

		await self.render("edit_team.html", title=team.title, result=self.get_res_sort(db_sess, team), team=team)

	@tornado.web.authenticated
	async def post(self):
		db_sess = db_session.create_session()
		team = self.get_team(self.request.uri.split('/')[-2], db_sess)
		try:
			s = self.get_body_argument("string")
		except Exception:
			# It's team profile!
			f = self.request.files.get("f")
			if f:
				file_avatar = f[0]  # We use only 1 file
				filename = f"static/img/teams/{file_avatar['filename']}"
				with open(filename, mode='wb') as file:
					file.write(file_avatar['body'])
				team.avatar = "../" + filename
			try:
				is_d = self.get_body_argument("DELETE_team")
			except Exception:
				is_d = None
			if is_d is not None:
				# bye :(
				db_sess.delete(team)
				db_sess.commit()
				self.redirect(f"/{self.current_user}/teams")
				return
			db_sess.commit()
			return self.render("edit_team.html", title=team.title, result=self.get_res_sort(db_sess, team), team=team)

		if s:
			res = db_sess.query(User).filter(User.username.like(f"%{s}%"), User.id != self.current_user.id).all()
		else:
			res = db_sess.query(User).filter(User.id != self.current_user.id).all()
		keys = []
		for user in res:
			if user in team.users:
				keys.insert(0, user)
			else:
				keys.append(user)
		res_sort = {}
		for key in keys:
			if key in team.users:
				res_sort[key] = 1
			else:
				res_sort[key] = 0
		# Adding members (from checkboxes values)
		try:
			_ = self.get_argument("btn2")
		except Exception:
			_ = None
		if _ is not None:
			# User saves changes
			# In general, the list has not changed, so we can handle it right like this
			for user in res_sort:
				try:
					__ = self.get_body_argument(user.username)
				except Exception:
					__ = None
				if __ == "on" and user not in team.users:
					await append_to_team(user, team)
					res_sort[user] = 1
				elif __ is None and user in team.users:
					team.users.remove(user)
					res_sort[user] = 0
		db_sess.commit()
		return self.render("edit_team.html", title=team.title, result=res_sort, text=s, team=team)


class TeamLeaveHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		team = self.get_team(self.request.uri.split('/')[-2], db_sess)
		if not team:
			self.write_error(404)
			return
		if self.current_user.id == team.chief:
			self.write_error(403)
			return
		current_user = self.get_user(self.current_user.username, db_sess)
		if current_user not in team.users:
			self.write_error(403)
			return
		team.users.remove(current_user)
		db_sess.commit()
		self.redirect(f"/{current_user.username}/teams")


class CreateTeamHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		if self.current_user.username != self.request.uri.split('/')[-2]:
			self.write_error(403)
			return
		form = TeamRegisterForm(self.request.arguments)
		await self.render("create_team.html", title="Creating team", form=form, message_title=None)

	@tornado.web.authenticated
	async def post(self):
		form = TeamRegisterForm(self.request.arguments)
		form.chief.data = self.current_user.id
		if form.validate():
			db_sess = db_session.create_session()
			if self.get_team(form.title.data, db_sess):
				await self.render(
					"create_team.html", title="Creating team", form=form,
					message_title=f"Title {form.title.data} is already taken")
				return
			team = Team(
				chief=form.chief.data,
				title=form.title.data
			)
			db_sess.add(team)
			db_sess.commit()
			self.redirect(f"/{self.current_user.username}/teams")
		await self.render("create_team.html", title="Creating team", form=form, message_title=None)


class UserInBoxHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		await self.render("inbox.html", title="Notifications", notifications=self.current_user.notifications[::-1])


class UserInBoxCheckHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def post(self):
		db_sess = db_session.create_session()
		user = self.get_user(self.current_user.username, db_sess)
		for i in range(len(user.notifications)):
			if self.get_argument("ntf" + str(i), None) is not None:
				user.notifications[i].is_read = True
		db_sess.add(user)
		db_sess.commit()
		self.redirect(f"/{self.current_user.username}/inbox")


class UserInBoxDeleteHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def post(self):
		db_sess = db_session.create_session()
		user = self.get_user(self.current_user.username, db_sess)
		i = 0
		while i < len(user.notifications):
			if self.get_argument("ntf" + str(i), None) is not None:
				db_sess.delete(user.notifications[i])
				del user.notifications[i]
				db_sess.add(user)
				db_sess.commit()
				i -= 1
			i += 1
		self.redirect(f"/{self.current_user.username}/inbox")


class InviteTeamHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		ss = self.request.uri.split('/')[-1].split('_____')
		if self.current_user.email == confirm_token(ss[0]):
			db_sess = db_session.create_session()
			user = self.get_user(self.current_user.username, db_sess)
			team = self.get_team(ss[1], db_sess)
			if user not in team.users:
				if user.id != team.chief:
					# Add user to team
					team.users.append(user)
					db_sess.add(team)
					# Delete notification
					msg = db_sess.query(Notification).filter(
						Notification.timestamp == ss[2].replace('%20', ' ')).first()
					if not msg or (msg not in user.notifications):
						self.write_error(404)
						return
					db_sess.delete(msg)
					del user.notifications[user.notifications.index(msg)]
					db_sess.add(user)
					# And... Commit db!
					db_sess.commit()
					await notify_join_team(db_sess.query(User).filter(User.id == team.chief).first(), team)
					self.redirect(f"/{user.username}/inbox")
					return
		self.write_error(404)


def get_admin(id_a: int):
	db_sess = db_session.create_session()
	return db_sess.query(User).filter(User.id == id_a).first()


class BoardViewHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		board = self.get_board(self.request.uri.split('/')[-2], db_sess)
		if not board:
			self.write_error(404)
			return
		user = self.get_user(self.current_user.username, db_sess)

		await self.render(
			"board_view.html", title=board.title, board=board, get_admin=get_admin,
			flag=False, u=user, choice=random.choice)

	@tornado.web.authenticated
	async def post(self):
		db_sess = db_session.create_session()
		board = self.get_board(self.request.uri.split('/')[-2], db_sess)
		user = self.get_user(self.current_user.username, db_sess)
		await join_to_board(user, board)

		await self.render(
			"board_view.html", title=board.title, board=board, get_admin=get_admin,
			flag=True, u=user, choice=random.choice)


class InviteBoardHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		ss = self.request.uri.split('/')[-1].split('_____')
		if self.current_user.email == confirm_token(ss[0]):
			db_sess = db_session.create_session()
			user = self.get_user(self.current_user.username, db_sess)
			user_asked = self.get_user(ss[3], db_sess)
			board = self.get_board(ss[1], db_sess)
			if user_asked not in board.board_users:
				# Add user to team
				board.board_users.append(user_asked)
				db_sess.add(board)
				# Delete notification
				msg = db_sess.query(Notification).filter(
					Notification.timestamp == ss[2].replace('%20', ' ')).first()
				if not msg or (msg not in user.notifications):
					self.write_error(404)
					return
				db_sess.delete(msg)
				del user.notifications[user.notifications.index(msg)]
				db_sess.add(user)
				# And... Commit db!
				db_sess.commit()
				await notify_join_board(user_asked, board)
				self.redirect(f"/{user.username}/inbox")
				return
		self.write_error(404)


class CreateBoardHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		if self.current_user.username != self.request.uri.split('/')[-2]:
			self.write_error(403)
			return
		form = FormBoardsCreate(self.request.arguments)
		await self.render("create_board.html", title="Creating board", form=form, message_title=None)

	@tornado.web.authenticated
	async def post(self):
		form = FormBoardsCreate(self.request.arguments)
		form.admin.data = self.current_user.id
		if form.validate():
			db_sess = db_session.create_session()
			if self.get_board(form.title.data, db_sess):
				await self.render(
					"create_board.html", title="Creating board", form=form,
					message_title=f"Title {form.title.data} is already taken")
				return
			board = Boards(
				title=form.title.data,
				about_board=form.about_board.data,
				admin=form.admin.data, )
			db_sess.add(board)
			db_sess.commit()
			self.redirect(f"/{self.current_user.username}/boards")
		await self.render("create_board.html", title="Creating board", form=form, message_title=None)


class BoardEditHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		board = self.get_board(self.request.uri.split('/')[-2], db_sess)
		if not board:
			self.write_error(404)
			return
		if self.current_user.id != board.admin:
			self.write_error(403)
			return
		threads = db_sess.query(Threads).all()
		dict_ts = await self.get_dict_t(threads, board)

		await self.render("edit_board.html", title=board.title, board=board, get_admin=get_admin, dict_threads=dict_ts)

	@tornado.web.authenticated
	async def post(self):
		db_sess = db_session.create_session()
		board = self.get_board(self.request.uri.split('/')[-2], db_sess)
		threads = db_sess.query(Threads).all()

		for thread in threads:
			if self.get_argument(f"btn-check-{thread.id}", None) is None:
				if thread in board.board_threads:
					# Delete thread
					del board.board_threads[board.board_threads.index(thread)]
					db_sess.add(board)
			else:
				if thread not in board.board_threads:
					# Add thread
					board.board_threads.append(thread)
					db_sess.add(board)

		for user in board.board_users:
			if self.get_argument(f"check-box-{user.username}", None) is None:
				# Delete user...
				del board.board_users[board.board_users.index(user)]
				db_sess.add(board)

		if self.get_argument("about_board", None) is not None:
			# Change board status
			board.about_board = self.get_argument("about_board", None)
			db_sess.add(board)

		db_sess.commit()
		dict_ts = await self.get_dict_t(threads, board)

		await self.render("edit_board.html", title=board.title, board=board, get_admin=get_admin, dict_threads=dict_ts)


class BoardDeleteHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		board = self.get_board(self.request.uri.split('/')[-2], db_sess)
		if board and (self.current_user.id == board.admin):
			# Delete board (
			db_sess.delete(board)
			db_sess.commit()
			self.redirect(f"/{self.current_user.username}/boards")
			return
		self.write_error(404)


class BoardLeaveHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		board = self.get_board(self.request.uri.split('/')[-2], db_sess)
		current_user = self.get_user(self.current_user.username, db_sess)
		if board and current_user and (current_user in board.board_users):
			del board.board_users[board.board_users.index(current_user)]
			db_sess.add(board)
			db_sess.commit()
			self.redirect(f"/{self.current_user.username}/boards")
			return
		self.write_error(404)


class BoardFloodHandler(BaseHandler, ABC):
	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		board = self.get_board(self.request.uri.split('/')[-2], db_sess)
		if not board:
			self.write_error(404)
		current_user = self.get_user(self.current_user.username, db_sess)
		msg_buffer_json = []
		for m in board.messages_buffer:
			msg_buffer_json.append(json.loads(json.dumps(m, cls=AlchemyEncoder)))
		if current_user in board.board_users or current_user.id == board.admin:
			await self.render("flood.html", messages=msg_buffer_json, title=f"{board.title} flood", b=board)
			return
		self.write_error(404)


class MessageNewHandler(BaseHandler, ABC):
	"""Post a new message to the chat room."""

	@staticmethod
	def append_message(board: Boards, message: Message, db_s):
		board.messages_buffer.append(message)
		if len(board.messages_buffer) > CACHE_SIZE:
			msg_delete = db_s.query(Message).filter(Message.id == board.messages_buffer[0].id).first()
			del board.messages_buffer[0]
			db_s.delete(msg_delete)

	@tornado.web.authenticated
	def post(self):
		db_sess = db_session.create_session()
		message = Message(sender_id=self.current_user.id, body=str(self.get_argument("body"))[:200])
		# render_string() returns a byte string, which is not supported
		# in json, so we must convert it to a character string.
		message.html = tornado.escape.to_unicode(self.render_string(
			"message.html", message=json.loads(json.dumps(message, cls=AlchemyEncoder))))
		board = self.get_board(self.request.uri.split('/')[-3], db_sess)
		if not board:
			self.write_error(403)
			return
		if self.get_argument("next", None):
			self.redirect(self.get_argument("next"))
		else:
			pass
		db_sess.add(message)
		self.append_message(board, message, db_sess)
		db_sess.commit()


class AjaxHandler(tornado.web.RequestHandler, ABC):
	"""Simple, ajax handler"""

	def get(self, *args, **kwargs):
		"""Get unlikely to be used for ajax"""
		self.write_error(403)  # Not allowed!
		self.finish()

	def post(self, *args):
		"""Example handle ajax post"""
		# useful code goes here
		self.write(json.dumps({'status': 'ok', 'sent': tornado.escape.json_decode(self.request.body)}))
		self.finish()


class UserEventCreateHandler(BaseHandler, ABC):
	def check_xsrf_cookie(self):
		pass

	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		board = self.get_board(self.request.uri.split('/')[-3], db_sess)
		if board:
			await self.render(
				"create_event.html", title="Creation a new user event", board=board, url=self.request.uri)

	def upload_file(self):
		f = self.request.files['file'][-1]
		with open(f"static/img/forms_uploads/{f['filename']}", mode='wb') as file:
			file.write(f['body'])

	@tornado.web.authenticated
	async def post(self):
		if self.request.body_arguments and self.request.body:
			db_sess = db_session.create_session()
			board = self.get_board(self.request.uri.split('/')[-3], db_sess)
			new_event = UserEvents(board=board.id)
			new_event.html = ''.join(
				[self.request.body_arguments[key][0].decode() for key in self.request.body_arguments])
			new_event.title = new_event.html.split(
				'<div class="flexBigInput" name="title_event" contenteditable="true">')[1].split('</div>')[0]
			new_event.about = new_event.html.split(
				'<div class="flexSmallInput" name="description_event" contenteditable="true">')[1].split('</div>')[0]
			db_sess.add(new_event)
			db_sess.commit()
		else:
			self.upload_file()


class TeamEventCreateHandler(BaseHandler, ABC):
	def check_xsrf_cookie(self):
		pass

	@tornado.web.authenticated
	async def get(self):
		db_sess = db_session.create_session()
		board = self.get_board(self.request.uri.split('/')[-3], db_sess)
		if board:
			await self.render(
				"create_event.html", title="Creation a new team event", board=board, url=self.request.uri)

	def upload_file(self):
		f = self.request.files['file'][-1]
		with open(f"static/img/forms_uploads/{f['filename']}", mode='wb') as file:
			file.write(f['body'])

	@tornado.web.authenticated
	async def post(self):
		if self.request.body_arguments and self.request.body:
			db_sess = db_session.create_session()
			board = self.get_board(self.request.uri.split('/')[-3], db_sess)
			new_event = TeamEvents(board=board.id)
			new_event.html = ''.join(
				[self.request.body_arguments[key][0].decode() for key in self.request.body_arguments])
			new_event.title = new_event.html.split(
				'<div class="flexBigInput" name="title_event" contenteditable="true">')[1].split('</div>')[0]
			new_event.about = new_event.html.split(
				'<div class="flexSmallInput" name="description_event" contenteditable="true">')[1].split('</div>')[0]
			db_sess.add(new_event)
			db_sess.commit()
		else:
			self.upload_file()


class UserEventHandler(BaseHandler, ABC):
	def check_xsrf_cookie(self):
		pass

	async def get(self):
		db_sess = db_session.create_session()
		e = self.get_user_event(self.request.uri.split('/')[-1], db_sess)
		current_user = self.get_user(self.current_user.username, db_sess)
		if current_user in e.users:
			self.write("You already got your answer.")
			return
		await self.render("event.html", title=e.title[:25].replace('&nbsp;', ' '), event=e, url=self.request.uri)

	async def post(self):
		db_sess = db_session.create_session()
		event = self.get_user_event(self.request.uri.split('/')[-1], db_sess)
		if not event:
			return
		current_user = self.get_user(self.current_user.username, db_sess)
		res = [self.request.body_arguments[key][0].decode() for key in self.request.body_arguments]
		res_dict = {}
		i = 0
		while i < len(res) - 1:
			res_dict[res[i]] = res[i + 1]
			i += 2
		if current_user not in event.users:
			# User's answers are ready, now post!
			event.users.append(current_user)
			db_sess.add(event)
			db_sess.commit()
			with open('auto/answers.json', mode='r', encoding='utf-8') as f:
				data = json.load(f)
			if str(event.id) in data["user_answers"]:
				data['user_answers'][str(event.id)].append({current_user.username: res_dict})
			else:
				data['user_answers'][event.id] = [{current_user.username: res_dict}]
			with open('auto/answers.json', mode='w', encoding='utf-8') as file:
				json.dump(data, file)
		else:
			self.write("You already got your answer.")


class TeamEventHandler(BaseHandler, ABC):
	def check_xsrf_cookie(self):
		pass

	async def get(self):
		db_sess = db_session.create_session()
		e = self.get_team_event(self.request.uri.split('/')[-1], db_sess)
		await self.render("event.html", title=e.title[:25], event=e, url=self.request.uri)

	async def post(self):
		pass


class UserEventAnswersView(BaseHandler, ABC):
	async def get(self):
		db_sess = db_session.create_session()
		event = self.get_user_event(self.request.uri.split('/')[-1], db_sess)
		board = None
		res = []
		for b in db_sess.query(Boards).all():
			if event in b.user_events:
				board = b
		if not board:
			self.write_error(403)
		if board.admin != self.current_user.id:
			self.write_error(403)
		with open('auto/answers.json', mode='r', encoding='utf-8') as f:
			data = json.load(f)
		try:
			res = data["user_answers"][str(event.id)]
		except Exception:
			if str(event.id) not in data["user_answers"]:
				res = []
			else:
				# Oops! We don't exist!
				self.write_error(404)
		await self.render(
			"forms_answers_view.html", answers=res,
			title="Check " + event.title[:20], event=event)


class TeamEventAnswersView(BaseHandler, ABC):
	async def get(self):
		pass


class UserEventEditHandler(BaseHandler, ABC):
	def check_xsrf_cookie(self) -> None:
		pass

	async def get(self):
		db_sess = db_session.create_session()
		event = self.get_user_event(self.request.uri.split('/')[-1], db_sess)
		if not event:
			return
		await self.render(
			"edit_user_event.html", event=event, title="Edit " + event.title[:20], url=self.request.uri)

	@tornado.web.authenticated
	async def post(self):
		if self.request.body_arguments and self.request.body:
			db_sess = db_session.create_session()
			id_ = self.request.uri.split('/')[-1]
			board = self.get_board(self.request.uri.split('/')[-4], db_sess)
			event = self.get_user_event(id_, db_sess)
			event.html = ''.join(
				[self.request.body_arguments[key][0].decode() for key in self.request.body_arguments])
			event.html = event.html.replace(
				f'''<button type="button" class="btn btn-outline-warning btn-lg" 
				onclick="save_changes('/board/{board.title}/user_event/edit/{id_}');">Edit</button>''', '')
			event.about = event.html.split(
				'<div class="flexSmallInput" name="description_event" contenteditable="true">')[1].split('</div>')[0]
			if event.users:
				for i in event.users:
					del event.users[event.users.index(i)]
				# delete user's answers from db and json files
				with open('auto/answers.json', mode='r', encoding='utf-8') as f:
					data = json.load(f)
				data['user_answers'][id_] = []
				with open('auto/answers.json', mode='w', encoding='utf-8') as file:
					json.dump(data, file)
			db_sess.add(event)
			db_sess.commit()


class TeamEventEditHandler(BaseHandler, ABC):
	async def get(self):
		pass


class ChessHandler(BaseHandler, ABC):
	async def get(self):
		await self.render("CHESS.html", title="Chess")


class RunnerHandler(BaseHandler, ABC):
	async def get(self):
		await self.render("RUNNER.html", title="Runner")


class ScrollingHandler(BaseHandler, ABC):
	async def get(self):
		await self.render("SCROLLING.html", title="Scrolling")


def main():
	db_session.global_init("db/Babylonia.db")
	app = Application()
	app.listen(options.port)
	tornado.ioloop.IOLoop.current().start()


# class MessageBuffer(object):
# 	def __init__(self):
# 		self.cache = []
# 		self.cache_size = 300
#
# 	def get_messages_since(self, cursor):
# 		# IMPORTANT: ``cursor`` should be the ``id`` of the last message received.
# 		results = []
# 		for msg in reversed(self.cache):
# 			if msg["id"] == cursor:
# 				break
# 			results.append(msg)
# 		results.reverse()
# 		return results
#
# 	def add_message(self, message):
# 		self.cache.append(message)
# 		if len(self.cache) > self.cache_size:
# 			self.cache = self.cache[-self.cache_size:]


if __name__ == "__main__":
	main()

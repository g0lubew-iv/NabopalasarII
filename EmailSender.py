from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.audio import MIMEAudio
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders

import mimetypes


def send_email(email: str, subject: str, text: str, *attachments: str):
	from decouple import config
	import smtplib

	address_from = config("FROM")
	password = config("PASSWORD")
	host_, port_ = config("HOST"), config("PORT")

	message = MIMEMultipart()
	message["From"] = address_from
	message["TO"] = email
	message["Subject"] = subject

	body = text
	message.attach(MIMEText(body, "plain"))

	process_attachments(message, attachments)

	server = smtplib.SMTP_SSL(host_, port_)
	server.connect(host_, port_)
	try:
		server.login(address_from, password)
	except smtplib.SMTPAuthenticationError:
		return False

	server.send_message(message)
	server.quit()
	return True


def process_attachments(msg, attachments, path=""):
	import os

	for file in attachments:
		file = path + file
		if os.path.isfile(file):
			# If it is file
			attach_file(msg, file)
		elif os.path.exists(file):
			# If it isn't file, but path exists. Thus, it's directory.
			list_dir = os.listdir(file)
			process_attachments(msg, list_dir, path=file + "/")


def attach_file(msg, f):
	import os

	attach_types = {
		"text": MIMEText,
		"image": MIMEImage,
		"audio": MIMEAudio
	}

	filename = os.path.basename(f)
	c_type, encoding = mimetypes.guess_type(f)
	if c_type is None or encoding is not None:
		c_type = "application/octet-stream"
	# There is arbitrary binary data
	main_type, sub_type = c_type.split("/", 1)
	with open(f, mode="rb" if main_type != "text" else "r") as fp:
		if main_type in attach_types:
			file = attach_types[main_type](fp.read(), _subtype=sub_type)
		else:
			file = MIMEBase(main_type, sub_type)
			file.set_payload(fp.read())
			encoders.encode_base64(file)
	file.add_header("Content-Disposition", "attachment", filename=filename)
	msg.attach(file)

from itsdangerous import URLSafeTimedSerializer
from decouple import config

import secrets

SECRET_KEY = config("SECRET_KEY")
SECRET_SALT = config("SECRET_SALT")


def generate_random_token(len_symbols: int):
    return str(secrets.token_urlsafe(len_symbols))


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECRET_SALT)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=SECRET_SALT,
            max_age=expiration
        )
    except Exception:
        return False
    return email

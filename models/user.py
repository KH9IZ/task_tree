# -*- coding: UTF-8 -*-
"""User model for interaction with database"""

# External imports
import hashlib
import hmac
import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

# Internal imports
from config import Config  # TODO: set app.config('SECRET_KEY') by default
from models import db


class User(db.Model):
    """User model for interaction with database"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, comment="Unique identifier of task")
    username = db.Column(db.String(32), nullable=False, comment="Name or username of user")
    password_hash = db.Column(db.String(128))
    photo = db.Column(db.String(128), nullable=True, comment="User's avatar")

    def __init__(self, username: str, password: str, photo: str = None):
        """User model for interaction with database
        :param username: Username or name of User
        :param password: Password of User
        :param photo: User's avatar (URL format)
        """
        self.username = username
        self.hash_password(password)
        self.photo = photo

    def hash_password(self, password: str):
        """Hash and load password to User"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """Return True/False for password validation

        :param password: string for check
        :type: str
        :return: true or False
        :rtype: bool
        """
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in: int = Config.TOKEN_PERIOD,
                            secret_key: str = Config.SECRET_KEY) -> str:
        """
        Generates self signed auth token

        :param expires_in: valid time in seconds
        :type: str
        :param secret_key: secret string for encoding
        :type: str
        :return: Token for session
        :rtype: str
        """
        t = jwt.encode({'id': self.id, 'exp': time.time() + expires_in}, secret_key)
        print("Generating auth_token: {}".format(t))
        return t

    @staticmethod
    def verify_auth_token(token, secret_key=Config.SECRET_KEY):
        """Checks is token valid or not

        :param token: string for validation
        :param secret_key: secret string for decode
        :return: Valid User object or None. When token is invalid - return None
        :rtype: User or None

        """
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
        except jwt.PyJWTError:
            return
        return User.query.get_or_404(data.get('id'))

    @staticmethod
    def check_tg_hash(data: dict, secret_key=Config.TG_TOKEN) -> bool:
        if 'hash' not in data or \
                'id' not in data or \
                (('username' not in data) and ('first_name' not in data)):
            return False
        data = dict(sorted(data.items(), key=lambda x: x[0]))
        tg_hash = data.pop('hash')
        validation_string = "\n".join(f"{i[0]}={i[1]}" for i in data.items()).encode("UTF-8")
        check_hash = hmac.new(key=secret_key.encode("UTF-8"),
                              msg=validation_string,
                              digestmod=hashlib.sha256).hexdigest()
        return check_hash == tg_hash

    def verify_tg(self, data: dict):
        return User.check_tg_hash(data) and self.verify_password(str(data.get('id')))

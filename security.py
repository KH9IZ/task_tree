from flask import g
from flask_httpauth import HTTPTokenAuth

from models.user import User

auth = HTTPTokenAuth()


@auth.verify_token
def verify_token(token):
    user = User.verify_auth_token(token)
    return user

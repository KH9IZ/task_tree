# -*- coding: UTF-8 -*-
"""Submodule with User API implementation"""

# External imports
from flask_restful import Resource, marshal_with, fields, reqparse, abort

# Internal imports
from models.user import User
from resources import api
from models import db
from security import auth

user_fields = {
    'id': fields.Integer,  # TODO remove
    'username': fields.String,
    'photo': fields.String,
}

# Configure arguments parser
user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, help="Username is just string")
user_parser.add_argument('password', type=str, help="Special string")  # TODO: set parameters for password
user_parser.add_argument('photo', type=str, help="URL of photo")  # TODO: implement avatars


@api.resource('/user', endpoint='user')
class UserAPI(Resource):
    """Resource representing User instance"""

    @auth.login_required
    @marshal_with(user_fields)
    def get(self) -> User:
        """Return user instance"""
        return auth.current_user()

    @marshal_with({'token': fields.String})
    def post(self) -> str:
        """Creates new user and return token"""
        args = user_parser.parse_args()
        if args['username'] is None or args['password'] is None:
            return abort(400, message="Username and password required.")
        # TODO: limit account creations and task per account
        new_user = User(args['username'], args['password'], args['photo'])
        db.session.add(new_user)
        db.session.commit()
        return new_user.generate_auth_token()


@api.resource('/user/get_token', endpoint='token')
class TokenAPI(Resource):
    """Auxiliary resource realising interact with **tokens**"""

    @marshal_with({'token': fields.String})
    def get(self) -> dict[str, str]:  # TODO: add 'expiration_period' field
        args = user_parser.parse_args()
        users = User.query.filter_by(username=args.get('username')).all()
        for u in users:
            if u.verify_password(args.get('password')):
                return {'token': u.generate_auth_token()}
        abort(401, error="Wrong username or password")

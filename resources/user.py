# -*- coding: UTF-8 -*-
"""Submodule with User API implementation"""

# External imports
from collections import defaultdict
from flask_restful import Resource, marshal_with, fields, abort
from flask import request

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


@api.resource('/user', endpoint='user')
class UserAPI(Resource):
    """Resource representing User instance"""

    @auth.login_required
    @marshal_with(user_fields)
    def get(self) -> User:
        """Return user instance"""
        return auth.current_user()

    @marshal_with({'token': fields.String})
    def post(self) -> dict[str, str]:
        """Creates new user and return token"""
        args = defaultdict(type(None), request.json)
        if not (args['username'] and args['password']):
            return abort(400, message="Username and password required.")
        # TODO: limit account creations and task per account
        # TODO: equal username and password
        new_user = User(args['username'], args['password'], args['photo'])
        db.session.add(new_user)
        db.session.commit()
        return {'token': new_user.generate_auth_token()}


@api.resource('/user/get_token', endpoint='token')
class TokenAPI(Resource):
    """Auxiliary resource realising interact with **tokens**"""

    @marshal_with({'token': fields.String})
    def get(self) -> dict[str, str]:  # TODO: add 'expiration_period' field
        args = dict(request.json or {})  # Immutable -> Mutable
        users = User.query.filter_by(username=args.get('username')).all()
        for u in users:
            if u.verify_tg(args) or u.verify_password(args.get('password', '')):
                return {'token': u.generate_auth_token()}
        if User.check_tg_hash(args):
            new_user = User(args.get('username') or args.get('first_name') + " " + (args.get('second_name') or ""),
                            str(args['id']), args.get('photo_url'))
            db.session.add(new_user)
            db.session.commit()
            return {'token': new_user.generate_auth_token()}

        abort(401, error="Wrong authentication data")

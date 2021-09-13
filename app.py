# -*- coding: UTF-8 -*-

# External dependencies
from flask import Flask

# Internal dependencies
from config import DevelopmentConfig
from resources import api, task, user  # import task and user is important
from models.task import db


app = Flask(__name__)  # Flask app object
app.config.from_object(DevelopmentConfig)

db.init_app(app)  # SQLAlchemy initialization
api.init_app(app)  # Flask_restful initialization


if __name__ == '__main__':
    app.run(debug=True)

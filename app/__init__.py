#!/usr/bin/env python
# -*- coding:utf-8 -*-


from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    from views import login_manage
    login_manage.init_app(app)
    register_blueprints(app)
    db.init_app(app)

    return app


def register_blueprints(app):
    from views import bp
    app.register_blueprint(bp)

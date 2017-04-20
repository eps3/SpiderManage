#!/usr/bin/env python
# -*- coding:utf-8 -*-


from flask import Flask
from views import bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    register_blueprints(app)
    return app


def register_blueprints(app):
    app.register_blueprint(bp)

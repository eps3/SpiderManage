#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, Response, url_for, request
from tasks import redis_client
from flask_login import LoginManager
from utils import md5
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('spider', __name__)

login_manage = LoginManager()
login_manage.login_view = 'login'


@bp.route('/', methods=['GET'])
def index():
    # 总任务数
    logging.info(request.headers.get('user-agent'))
    redis_client.keys('*')
    from model import User
    user = User(email='admin@admin.com')
    return render_template("index.html")


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        email = request.form.get('email', 'guest@guest.com')
        password = request.form.get('password', '')
        logger.info('email:%s, password:%s' % (email, password))
        return render_template("index.html")
    else:
        return 'not support'

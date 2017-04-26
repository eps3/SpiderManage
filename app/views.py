#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, Response, url_for
from tasks import redis_client
from utils import md5
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('spider', __name__)


@bp.route('/')
def index():
    # 总任务数
    redis_client.keys('*')
    return render_template("index.html")

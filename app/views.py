#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, Response, url_for

import logging
import traceback
import json
import requests

logger = logging.getLogger(__name__)

bp = Blueprint('spider', __name__)


@bp.route('/')
def index():
    return render_template("index.html")

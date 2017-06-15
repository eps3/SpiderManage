#!/usr/bin/env python
# -*- coding:utf-8 -*-

import redis
from utils import md5
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, PROJECT_NAME

# 设置redis客户端
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)


def get_user_all_task(user='system'):
    key = '.'.join([md5(PROJECT_NAME), md5(user), '*', 'status'])
    return key
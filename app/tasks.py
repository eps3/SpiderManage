#!/usr/bin/env python
# -*- coding:utf-8 -*-

import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

# 设置redis客户端
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)


def get_user_all_task():
    pass


class RedisQueue(object):
    def __init__(self, name, namespace='queue'):
        self.__db = redis_client
        self.key = '%s:%s' % (namespace, name)

    def qsize(self):
        return self.__db.llen(self.key)

    def empty(self):
        return self.qsize() == 0

    def put(self, item):
        self.__db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        if item:
            item = item[1]
        return item

    def get_nowait(self):
        return self.get(False)


class TaskManage(object):
    def __init__(self, name, namespace='queue', **redis_kwargs):
        self.__db = redis.Redis(**redis_kwargs)
        self.key = '%s:%s' % (namespace, name)


class Task(object):
    def __init__(self, queue_name, user_name='system'):
        self.queue_name = queue_name
        self.user_name = user_name

    def handler(self):
        pass

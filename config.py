#!/usr/bin/env python
# -*- coding:utf-8 -*-

SECRET_KEY = 'some secret key'
TEMPLATES_AUTO_RELOAD = True
PROJECT_NAME = 'SpiderManage'
# Redis Config
REDIS_HOST = '120.25.227.8'
REDIS_PORT = 6379
REDIS_PASSWORD = 'xuxinredis'
# SQLite
# SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Users/sheep3/workplace/SpiderManage/data.db'
# SQLALCHEMY_TRACK_MODIFICATIONS = True

# MYSQL
SQLALCHEMY_DATABASE_URI = 'mysql://root:xuxin.mysql@120.25.227.8:3306/spider_db?charset=utf8'
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
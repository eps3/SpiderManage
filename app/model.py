#!/usr/bin/env python
# -*- coding:utf-8 -*-

from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(128), nullable=False)
    tasks = db.relationship('Task', backref='user')


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    json_info = db.Column(db.Text, default='{}')
    status = db.Column(db.Integer, default=0)


class Task_status(db.Model):
    __tablename__ = 'task_status'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    time = db.Column(db.DateTime, index=True)
    error_count = db.Column(db.BigInteger)
    ok_count = db.Column(db.BigInteger)
    all_count = db.Column(db.BigInteger)

#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import render_template, Response, url_for, request, session, redirect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(128), nullable=False)
    tasks = db.relationship('Task', backref='user')

    @staticmethod
    def create_admin():
        user = User(email='admin@admin.com', username='admin', password_hash='admin', salt='admin')
        db.session.add(user)
        db.session.commit()


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    json_info = db.Column(db.Text, default='{}')
    status = db.Column(db.Integer, default=0)


class TaskStatus(db.Model):
    __tablename__ = 'task_status'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    time = db.Column(db.DateTime, index=True)
    error_count = db.Column(db.BigInteger)
    ok_count = db.Column(db.BigInteger)
    all_count = db.Column(db.BigInteger)


# ######################################################################################################

def login_require(func):
    @wraps(func)
    def decorator(*args,**kwargs):
        if 'email' in session:
            return func(*args, **kwargs)
        else:
            # 如果没有就重定向到登录页面
            return redirect("login")
    return decorator


# 主页
@app.route('/', methods=['GET'])
@login_require
def index():
    return render_template("index.html")


# 登陆页面
@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")


# 退出接口
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('email', None)
    return redirect(url_for('index'))


# 登陆接口
@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email, password_hash=password).first()
    if user:
        session['email'] = user.email
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


# 添加任务
@app.route('/add_task', methods=['GET'])
@login_require
def add_task():
    return render_template("add_task.html")


# 数据查看
@app.route('/data/<string:task>')
@login_require
def data(task):
    return render_template("data.html")


# 状态监控
@app.route('/status/<string:task>')
@login_require
def status(task):
    return render_template("status.html")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)

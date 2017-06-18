#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import render_template, Response, url_for, request, session, redirect
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import redis

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


# 用户
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(128), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy='dynamic')

    @staticmethod
    def create_admin():
        user = User(email='admin@admin.com', username='admin', password_hash='admin', salt='admin')
        db.session.add(user)
        db.session.commit()


# 任务
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    json_info = db.Column(db.Text, default='{}')
    status = db.Column(db.Integer, default=0)


# 任务状态
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
    def decorator(*args, **kwargs):
        if 'email' in session:
            return func(*args, **kwargs)
        else:
            # 如果没有就重定向到登录页面
            return redirect("login")

    return decorator


@app.context_processor
def get_all_task():
    if 'user_id' not in session:
        return dict(user=None)
    user_id = session['user_id']
    user = User.query.filter_by(id=user_id).first()
    return dict(user=user)


# 主页
@app.route('/', methods=['GET'])
@login_require
def index():
    
    return render_template("index.html")


# 登陆页面
@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")


# 添加任务
@app.route('/add_task', methods=['GET'])
@login_require
def add_task():
    return render_template("add_task.html")


# 数据查看
@app.route('/data/<string:task>')
@login_require
def data(task):
    task_data = {
        'head': ['id', 'content'],
        'data': [{
                'id': 550854066686,
                'content': u'HOME1HEILAN1官方旗舰店俏以男装纯棉男士t恤社会精神小伙潮yifu'
            },
            {
                'id': 548650726866,
                'content': u'短袖T恤男装社会精神小伙港仔文艺男bf风街头品牌折扣店男人'
            },
            {
                'id': 544532961017,
                'content': u'布先生 2017短袖t恤男潮流半袖男士圆领衣服男夏季黑色条纹半截袖'
            },
            {
                'id': 545554576907,
                'content': u'恒源祥男士袜子纯棉低帮夏季浅口隐形运动防滑防臭短袜薄款船袜男'
            },
            {
                'id': 547217618111,
                'content': u'夏季男裤男士休闲裤男直筒宽松裤韩版百搭修身长裤男裤子男薄款潮'
            },
            {
                'id': 548196807121,
                'content': u'男鞋夏季潮鞋新款运动鞋男士休闲鞋韩版透气板鞋男百搭跑步鞋网鞋'
            },
            {
                'id': 536639934013,
                'content': u'花花公子男鞋子夏季白鞋男士运动休闲鞋韩版潮流黑白色百搭板鞋男'
            },
            {
                'id': 535558170159,
                'content': u'七匹狼钱包 男士短款真皮软头层牛皮驾照皮夹子多功能驾驶证钱夹'
            },
            {
                'id': 546821717375,
                'content': u'男鞋潮鞋2017夏天男士休闲鞋真皮鞋子韩版百搭夏季透气英伦皮鞋男'
            },
            {
                'id': 545672339251,
                'content': u'七匹狼男装 中年男士短袖t恤纯棉圆领打底衫丝光条纹2017夏季新款'
            }
        ]
    }
    return render_template("data.html", task=task, task_data=task_data)


# 状态监控
@app.route('/status/<string:task>')
@login_require
def status(task):
    return render_template("status.html", task=task)


# 退出接口
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('email', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))


# 登陆接口
@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email, password_hash=password).first()
    if user:
        session['email'] = user.email
        session['user_id'] = user.id
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


# 添加任务接口
@app.route('/add_task', methods=['POST'])
def add_task_post():
    pass


if __name__ == '__main__':
    db.create_all()
    app.run(host='127.0.0.1', port=5001, debug=True)

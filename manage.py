#!/usr/bin/env python
# -*- coding:utf-8 -*-


from flask_script import Manager, Server
from app import create_app
from app import db
import logging

logger = logging.getLogger(__name__)
app = create_app()
manager = Manager(app)


@manager.option('-e', '--email', dest='email', default='admin@admin.com', help='Your email')
@manager.option('-p', '--password', dest='password', default='admin', help='Your password')
def init_db(email, password):
    print ('email: %s, password: %s' % (email, password))
    db.create_all()


manager.add_command("run",
                    Server(host='0.0.0.0',
                           port=5000,
                           use_debugger=False, threaded=True))

manager.add_command("debug",
                    Server(host='0.0.0.0',
                           port=5001,
                           use_debugger=True, threaded=True))

if __name__ == '__main__':
    manager.run()

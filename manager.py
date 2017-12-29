#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wuaiwow import db
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from celery_worker import app

# app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


@manager.command
def list_routes():
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, rule))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def init_db():
    from wuaiwow.utils.create_users import create_users
    create_users()


if __name__ == '__main__':
    manager.run()

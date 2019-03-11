#!/usr/bin/env python
# coding:utf-8

from wuaiwow import create_app, celery
app = create_app()
from wuaiwow import db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app.app_context().push()
migrate = Migrate(app, db)
manager = Manager(app)
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
def init_data():
    from wuaiwow.utils.default_data import add_default_data, add_test_data
    # add_default_data()
    add_test_data()


if __name__ == '__main__':
    manager.run()

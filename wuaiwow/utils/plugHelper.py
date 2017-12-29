# coding:utf-8

_blueprints = []


def add_blueprint(blueprint):
    _blueprints.append(blueprint)


def register_blueprints():
    # creates and registers blueprints
    import wuaiwow.controllers.home
    import wuaiwow.controllers.users
    import wuaiwow.controllers.gm
    import wuaiwow.controllers.player
    import wuaiwow.controllers.admin

    from wuaiwow import app
    for blueprint in _blueprints:
        app.register_blueprint(blueprint)


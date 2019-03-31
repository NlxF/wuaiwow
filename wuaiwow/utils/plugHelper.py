# coding:utf-8

_blueprints = []
_subdomain = ''


def add_blueprint(blueprint, subdomain=_subdomain):
    _blueprints.append((blueprint, subdomain))


def register_blueprints():
    from wuaiwow import app
    # creates and registers blueprints
    import wuaiwow.controllers.home
    import wuaiwow.controllers.users
    import wuaiwow.controllers.gm
    import wuaiwow.controllers.player
    import wuaiwow.controllers.admin

    for blueprint, subdomain in _blueprints:
        sd = str(subdomain) if subdomain else ''
        app.register_blueprint(blueprint, subdomain=sd)

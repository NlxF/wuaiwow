# coding:utf-8
import os
# import time
from uuid import uuid4
from flask import Flask, request, g, session, url_for, render_template
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_user import current_user
from utils import (init_email_error_handler,
                   init_mysql_handler,
                   configure_extensions, valid_uuid)
from utils.plugHelper import register_blueprints
from utils.onlineHelper import Online
from utils.factory import make_celery
from utils.mySqlalchemy import UnlockedReadAlchemy
from celery.utils.log import get_task_logger

# Initialize Flask app and db
app = Flask("wuaiwow")

db = None
csrf = None
logger = None
onlineHelper = None

celery = make_celery(app)
celery_logger = get_task_logger(__name__)       # celery logger


# @app.before_first_request
# def initialize_app_on_first_request():
#     """ Create users and roles tables on first HTTP request """
#     from utils.create_users import create_users
#     create_users()


@app.before_request
def online_setup():
    # if '/sign-out' in request.path:
    #     pass
    if '/static/' not in request.path:                          # 浏览网页时 更新在线状态
        from models.users import UserOnline                     # 登录用户更新最新在线时间
        if current_user.is_authenticated:
            nameless = session.get("_expires_name", None)
            if nameless:
                onlineHelper.make_user_offline(nameless)        # 如果用户登入前以游客身份在浏览,此时要将对应的游客设为离线,防止重复统计
            key = current_user.username
            user_last_activity = onlineHelper.get_user_last_activity(user_id=key)
            if user_last_activity:
                elapse_time = onlineHelper.get_valid_elapse_time(user_last_activity)
                if app.config['PAGE_REFRESH_MIN_TIME'] < elapse_time < app.config['PAGE_REFRESH_MAX_TIME']:  # 有效刷新
                    current_user.online_time += elapse_time     # 更新用户总在线时间(可能会升级!!!)
                    db.session.add(current_user)                # block
        else:                                                   # 游客更新最新在线时间
            key = session.get("_expires_name", None)
            if not key:
                key = str(uuid4())
                session["_expires_name"] = key

        onlineHelper.make_current_user_online(user_id=key)      # 设置为在线状态
        all_online_users = onlineHelper.get_online_users()      # 获取所有在线用户,包括游客
        visitor = [x for x in all_online_users if valid_uuid(x)]
        register = all_online_users - set(visitor)
        user_on = UserOnline(visitor=",".join(visitor),
                             register=",".join(register),
                             online_user_num=len(all_online_users))
        db.session.add(user_on)
        db.session.commit()

        max_online = UserOnline.query.order_by(UserOnline.online_user_num.desc(), UserOnline.occ_time.desc()).first()
        g.online_users_msg = {'all': len(all_online_users),
                              'register': len(register),
                              'visitor': len(visitor),
                              'max_num': max_online.online_user_num,
                              'occ_time': max_online.occ_time,
                              'time_zone': u"中国标准时间"}   # time.strftime("%z")}


# 实时更新资源文件
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


@app.errorhandler(CSRFError)
def csrf_error(error):
    return render_template('csrf_error.html', reason=error.description), 400


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


# configure app
def create_app(test=False):

    # app.config['DEBUG'] = debug

    # ***** Initialize app config settings *****
    app.config.from_object('wuaiwow.flask_user_settings')

    # Read environment-specific settings from file defined by OS environment variable 'ENV_SETTINGS_FILE'
    if app.debug:
        settings_file = 'develo_settings.py'
    else:
        settings_file = 'deploy_settings.py'
    env_settings = os.environ.get('ENV_SETTINGS_FILE', settings_file)
    app.config.from_pyfile(env_settings)

    if test:
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF checks while testing

    import logging
    # Setup an CRITICAL logger to send emails to app.config.ADMINS
    init_email_error_handler(app=app, level=logging.CRITICAL)

    # Mysql setting
    global  db
    db = UnlockedReadAlchemy(app, use_native_unicode='utf8')

    # onlineHelper setting
    global onlineHelper
    onlineHelper = Online(app=app)

    # add error below CRITICAL
    global logger
    logger = init_mysql_handler(app=app, level=logging.INFO)

    # Configure app extensions
    configure_extensions(app, db)

    # csrf setting
    global csrf
    csrf = CSRFProtect(app=app)

    # celery setting
    celery.conf.update(app.config)	 # 更新 celery 的配置

    # load blueprints
    register_blueprints()

    return app


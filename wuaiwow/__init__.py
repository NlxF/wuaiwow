# coding:utf-8
# from gevent import monkey; monkey.patch_all()
import os
import time
from datetime import datetime
from uuid import uuid4
from flask import Flask, request, g, session, url_for, render_template
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_user import current_user
from flask_cache import Cache
from utils import (init_email_error_handler,
                   init_mysql_handler,
                   configure_extensions)
from utils.plugHelper import register_blueprints
from utils.onlineHelper import Online
from utils.factory import make_celery
from utils.mySqlalchemy import UnlockedReadAlchemy, Model
from celery.utils.log import get_task_logger

# Initialize Flask app and db
app = Flask("wuaiwow")

db = None
csrf = None
cache = None
logger = None
onlineHelper = None
# celery = make_celery(app)
# celery_logger = get_task_logger(__name__)       # celery logger
max_online_user_num = -1
max_online_occ_time = None

# @app.before_first_request
# def initialize_app_on_first_request():
#     """ Create users and roles tables on first HTTP request """


@app.before_request
def online_setup():
    if '/static/' not in request.path:                          # 浏览网页时 更新在线状态
        from models.users import UserOnline                     # 登录用户更新最新在线时间
        if current_user.is_authenticated:
            nameless = session.get("_expires_name", None)
            if nameless:
                onlineHelper.make_visitor_offline(nameless)     # 如果用户登入前以游客身份在浏览,此时要将对应的游客设为离线,防止重复统计
                session.pop('_expires_name')
            key = current_user.username
            user_last_activity = onlineHelper.get_user_last_activity(key, False)
            if user_last_activity:
                # elapse_time = onlineHelper.get_valid_elapse_time(user_last_activity)
                elapse_time = time.time() - user_last_activity
                if app.config['ONLINE_PAGE_REFRESH_MIN'] < elapse_time < app.config['ONLINE_PAGE_REFRESH_MAX']:  # 有效刷新
                    current_user.online_time += elapse_time     # user_last_activity     # 更新用户总在线时间(可能会升级!!!)
                    db.session.add(current_user)                # will block

            onlineHelper.make_user_online(user_id=key)          # 设置会员为在线状态
        else:                                                   # 游客更新最新在线时间
            key = session.get("_expires_name", None)
            if not key:
                key = str(uuid4())
                session["_expires_name"] = key

            onlineHelper.make_visitor_online(user_id=key)       # 设置游客为在线状态

        # 获取（在线游客,在线会员,是否保存,数量,发生时间,成员）
        visitor, register, need_refresh, number, member, occ_time, interval = onlineHelper.get_online_users_record()
        all_online_users = visitor + register

        global max_online_user_num, max_online_occ_time
        if max_online_user_num < all_online_users:
            need_refresh = True

        if need_refresh:
            user_on = UserOnline(member=",".join(member),
                                 occ_time=datetime.fromtimestamp(int(occ_time)),
                                 interval=interval,
                                 online_user_num=number)
            db.session.add(user_on)
            db.session.commit()

        if need_refresh or max_online_user_num<0:
            max_online_record = UserOnline.query.order_by(UserOnline.online_user_num.desc(), UserOnline.occ_time.desc()).first()
            max_online_user_num = max_online_record.online_user_num
            max_online_occ_time = max_online_record.occ_time

        g.user = current_user
        g.online_users_msg = {'all': all_online_users,
                              'register' : register,
                              'visitor'  : visitor,
                              'max_num'  : max_online_user_num if max_online_user_num > 0 else register+visitor,
                              'occ_time' : max_online_occ_time if max_online_occ_time else datetime.fromtimestamp(int(occ_time)),
                              'time_zone': time.strftime("%z")}   #u"中国标准时间" }

        if '/admin/' in request.path or '/gm/' in request.path or '/user/' in request.path:
            from utils.modelHelper import get_user_new_messages_num
            g.unread_cnt = get_user_new_messages_num(current_user)


@app.after_request
def add_header(response):
    if '/static/' in request.path:
        response.cache_control.max_age = 15552000
    elif response.content_type == 'application/json':
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.cache_control.must_revalidate = True
    return response


# 实时更新资源文件
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(CSRFError)
def csrf_error(error):
    return render_template('error.html', reason=error.description), 400


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


# configure app
def create_app(need_default_data=False, test=False):

    # ***** Initialize app config settings *****
    app.config.from_object('wuaiwow.flask_settings')
    # print("debug mode: {}".format("YES" if app.debug else "NO"))
    
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

    # mysql setting
    global db
    db = UnlockedReadAlchemy(app, use_native_unicode='utf8')
    db.session.expire_on_commit = False

    # redis cache setting
    global cache
    cache = Cache(app)

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
    # celery.conf.update(app.config)	 # 更新 celery 的配置

    # load blueprints
    register_blueprints()

    if need_default_data:
        # init default data
        from utils.default_data import add_default_data
        add_default_data(app.config['PERMISSIONS'])

    return app


# -*- coding: utf-8 -*-

ADMINS = frozenset(['wuaiwow@gmail.com'])

DATABASE_NAME = 'wuaiwow_test_2'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'mysql://root:lxf@localhost/'+DATABASE_NAME
SQLALCHEMY_NATIVE_UNICODE = True

THREADS_PER_PAGE = 1

# Flask settings
SECRET_KEY = 'R\x8f@\x93\x9e\x08\xbe6+\x98\x7f^\xaf\xe4\x03\xb09jk>Hvn\xac'
# PLEASE USE A DIFFERENT KEY FOR PRODUCTION ENVIRONMENTS!

# Flask-Mail settings
MAIL_USERNAME = 'it1780@sina.com'
MAIL_PASSWORD = 'luxiaofei3517'
MAIL_DEFAULT_SENDER = '"吾爱魔兽" <it1780@sina.com>'
MAIL_SERVER = 'smtp.sina.com'
MAIL_PORT = 587       #25
# MAIL_USE_SSL = True  #465
MAIL_USE_TLS = True   #587


# mySQLHandler settings
DB = {'host': '127.0.0.1',
      'port': 3306,
      'dbuser': 'root',
      'dbpassword': 'lxf',
      'dbname': DATABASE_NAME}


# lserver setting
LSERVER_HOST = '192.168.1.101'
# LSERVER_HOST = '172.16.130.147'
# LSERVER_HOST = '192.168.1.138'
LSERVER_PORT = 8083

# 与lserver 通信是否需要加密
NEEDENCRYPTION = False

# toolbar setting
DEBUG_TB_INTERCEPT_REDIRECTS = False


# celery setting
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'db+mysql://root:lxf@localhost/celery_rst_test'
CELERY_TASK_RESULT_EXPIRES = 120

# WTF_CSRF_ENABLED = True
# WTF_CSRF_SECRET_KEY = "a!sd@adfg2~34^f%s&$#po45weqwe"

# RECAPTCHA_USE_SSL = False
# RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
# RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
# RECAPTCHA_OPTIONS = {'theme': 'white'}

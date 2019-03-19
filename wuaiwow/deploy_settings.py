# coding: utf-8

import os

_basedir = os.path.abspath(os.path.dirname(__file__))

ADMINS = frozenset(['wuaiwow@gmail.com'])

DATABASE_NAME = 'wuaiwow'
DB_PASSWORD = 'password2'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'mysql://root:'+DB_PASSWORD+'@www-database/'+DATABASE_NAME
SQLALCHEMY_NATIVE_UNICODE = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_TIMEOUT = 300

# Cache setting
# CACHE_TYPE = 'simple'
CACHE_TYPE                 = 'redis'
CACHE_KEY_PREFIX           = 'wuaiwow'
CACHE_REDIS_HOST           = 'localhost'
CACHE_REDIS_PORT           = 6379
CACHE_REDIS_DB             = 0
CACHE_REDIS_PASSWORD       = ""
CACHE_DEFAULT_TIMEOUT      = 60 * 15          # flask_cache  15分钟缓存失效

# OnlineHelper setting
ONLINE_DB = 1
# 在线状态持续间隔
ONLINE_LAST_MINUTES = 3
# 在线记录间隔
ONLINE_RECORD_INTERVAL = 30
# ONLINE_USER_PREFIX = ''
# ONLINE_VISITOR_PREFIX = ''
# ONLINE_ALL_USER_PREFIX = ''
# ONLINE_ALL_VISITOR_PREFIX = ''
# 两次刷新的有效时间间隔(秒)
ONLINE_PAGE_REFRESH_MIN = 30
ONLINE_PAGE_REFRESH_MAX = ONLINE_LAST_MINUTES * 60

# Flask settings                     # Generated with: import os; os.urandom(24)
SECRET_KEY = "\xcdG\xe8\xc0\x05\xfb\x87\x0f\xc6$o\xdb`k\n\x18\xebB\xeb\x0cm\xf6'\x92"
# PLEASE USE A DIFFERENT KEY FOR PRODUCTION ENVIRONMENTS!

# Flask-Mail settings
MAIL_USERNAME = 'it1780@sina.com' #'wuaiwow@gmail.com'
MAIL_PASSWORD = 'luxiaofei3517'
MAIL_DEFAULT_SENDER = '"吾爱魔兽" <it1780@sina.com>'
MAIL_SERVER = 'smtp.sina.com'
MAIL_PORT = 587       #25
#MAIL_USE_SSL = True  #465
MAIL_USE_TLS = True   #587


# mySQLHandler settings
DB = {'host': 'www-database',
      'port': 3306,
      'dbuser': 'root',
      'dbpassword': DB_PASSWORD,
      'dbname': DATABASE_NAME,
      'charset': 'utf8',
      'use_unicode': True
      }

# lserver setting
LSERVER_HOST = 'docker.for.mac.localhost'
LSERVER_PORT = 8083

# 与lserver 通信是否需要加密
NEEDENCRYPTION = False

# toolbar setting
DEBUG_TB_INTERCEPT_REDIRECTS = False

# celery setting
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'db+mysql://root:'+DB_PASSWORD+'@www-database/celery_rst_test'
CELERY_TASK_RESULT_EXPIRES = 120

#WTF_CSRF_ENABLED = True
#WTF_CSRF_SECRET_KEY = "a!sd@adfg2~34^f%s&$#po45weqwe"

#RECAPTCHA_USE_SSL = False
#RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
#RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
#RECAPTCHA_OPTIONS = {'theme': 'white'}

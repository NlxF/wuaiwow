# coding:utf-8

ADMINS = frozenset(['wuaiwow@gmail.com'])

DATABASE_NAME = 'wuaiwow_test_2'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'mysql://root:lxf@localhost/'+DATABASE_NAME
SQLALCHEMY_NATIVE_UNICODE = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

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
ONLINE_LAST_MINUTES = 5
# 在线记录间隔
ONLINE_RECORD_INTERVAL = 10
# ONLINE_USER_PREFIX = ''
# ONLINE_VISITOR_PREFIX = ''
# ONLINE_ALL_USER_PREFIX = ''
# ONLINE_ALL_VISITOR_PREFIX = ''
# 两次刷新的有效时间间隔(秒)
ONLINE_PAGE_REFRESH_MIN = 15
ONLINE_PAGE_REFRESH_MAX = ONLINE_LAST_MINUTES * 60


# Flask settings
SECRET_KEY = 'R\x8f@\x93\x9e\x08\xbe6+\x98\x7f^\xaf\xe4\x03\xb09jk>Hvn\xac'
# PLEASE USE A DIFFERENT KEY FOR PRODUCTION ENVIRONMENTS!

# Flask-Mail settings
MAIL_USERNAME = 'it1780@sina.com'
MAIL_PASSWORD = 'luffy,20170116!'
MAIL_DEFAULT_SENDER = '"吾爱魔兽" <it1780@sina.com>'
MAIL_SERVER = 'smtp.sina.com'
MAIL_PORT = 587        #25
# MAIL_USE_SSL = True  #465
MAIL_USE_TLS = True    #587


# mySQLHandler settings
DB = {'host': '127.0.0.1',
      'port': 3306,
      'dbuser': 'root',
      'dbpassword': 'lxf',
      'dbname': DATABASE_NAME,
      'charset':'utf8',
      'use_unicode':True
      }


# lserver setting
LSERVER_HOST = '127.0.0.1'
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

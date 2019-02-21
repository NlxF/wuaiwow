# coding: utf-8

import os

_basedir = os.path.abspath(os.path.dirname(__file__))

ADMINS = frozenset(['wuaiwow@gmail.com'])

DATABASE_NAME = 'wuaiwow'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'mysql://root:password@www-database/'+DATABASE_NAME
#SQLALCHEMY_NATIVE_UNICODE = False

THREADS_PER_PAGE = 8

# Flask settings                     # Generated with: import os; os.urandom(24)
SECRET_KEY = "\xcdG\xe8\xc0\x05\xfb\x87\x0f\xc6$o\xdb`k\n\x18\xebB\xeb\x0cm\xf6'\x92"
# PLEASE USE A DIFFERENT KEY FOR PRODUCTION ENVIRONMENTS!

# Flask-Mail settings
MAIL_USERNAME = 'it1780@sina.com' #'wuaiwow@gmail.com'
MAIL_PASSWORD = 'luxiaofei3517'
MAIL_DEFAULT_SENDER = '"wuaiWow" <it1780@sina.com>'
MAIL_SERVER = 'smtp.sina.com'
MAIL_PORT = 587       #25
#MAIL_USE_SSL = True  #465
MAIL_USE_TLS = True   #587


# mySQLHandler settings
DB = {'host': 'www-database',
      'port': 3306,
      'dbuser': 'root',
      'dbpassword': 'password',
      'dbname': DATABASE_NAME}

#WTF_CSRF_ENABLED = True
#WTF_CSRF_SECRET_KEY = "a!sd@adfg2~34^f%s&$#po45weqwe"

#RECAPTCHA_USE_SSL = False
#RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
#RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
#RECAPTCHA_OPTIONS = {'theme': 'white'}

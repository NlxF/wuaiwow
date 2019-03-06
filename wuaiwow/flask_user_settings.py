# coding: utf-8
import os


# Application settings
APP_NAME = "wuaiwow"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " System Error:"

# Flask settings
CSRF_ENABLED = True

# Flask-User Features settings
USER_APP_NAME = APP_NAME
USER_ENABLE_CHANGE_PASSWORD = True         # Allow users to change their password
USER_ENABLE_CHANGE_USERNAME = False        # Allow users to change their username
USER_ENABLE_CONFIRM_EMAIL = True           # Force users to confirm their email
USER_ENABLE_FORGOT_PASSWORD = True         # Allow users to reset their passwords
USER_ENABLE_EMAIL = True                   # Register with Email
USER_ENABLE_REGISTRATION = True            # Allow new users to register
USER_ENABLE_RETYPE_PASSWORD = True         # Prompt for `retype password` in:
USER_ENABLE_USERNAME = True                # Register and Login with username
USER_ENABLE_LOGIN_WITHOUT_CONFIRM = False  # Allow users to login without a confirmed email address Protect views using @confirm_email_required
USER_ENABLE_MULTIPLE_EMAILS = False        # Users may register multiple emails Requires USER_ENABLE_EMAIL=True
USER_CONFIRM_EMAIL_EXPIRATION = 1*24*3600  # 1 days
USER_INVITE_EXPIRATION = 7*24*3600         # 7 days
USER_RESET_PASSWORD_EXPIRATION = 1*24*3600 # 1 days
USER_ENABLE_INVITATION = True              # Allow users to invite Friends

USER_AFTER_LOGIN_ENDPOINT = 'wuaiwow.home_page'
USER_AFTER_LOGOUT_ENDPOINT = 'wuaiwow.home_page'
USER_AFTER_CONFIRM_ENDPOINT = 'wuaiwow.home_page'

# For i18n
BABEL_DEFAULT_LOCALE = 'zh_CN'

# roles, L1=player,L8=GM,L10=admin,
PERMISSIONS = [(10, 'CHRACE', u'变种族'), (15, 'CUSTOMIZE', u'性别'), (20, 'UPLEVEL', u'升级'),
               (25, 'GETMONEY', u'金币'), (30, 'GETITEMS', u'套装'), (35, 'PORTAL', u'传送门'), (40, 'MOUNTS', u'座机'),
               (98, 'GM', u'游戏管理员'),(99, 'UPGRADE', u'站点管理员'), (100, 'ADMIN', u'超级管理员')]


# IP 地址查询URL
URL_QUERY = 'http://api.map.baidu.com/location/ip?ak=MGe5iir7DLaKia6HgoFG9Pab2GweMQL9&ip='

# 职业
WOW_CLASS = [u'战士', u'潜行者', u'德鲁伊', u'法师', u'圣骑士', u'牧师', u'萨满', u'术士', u'猎人', u'死亡骑士']
WOW_CLASS_SX = ['ZS', 'DZ', 'XD', 'FS', 'QS', 'MS', 'SM', 'SS', 'LR', 'SQ']

# 种族
WOW_RACE_ALLIANCE = [u'人类', u'矮人', u'侏儒', u'暗夜精灵', u'德莱尼']
WOW_RACE_ALLIANCE_EN = ['Humans', 'Gnomes', 'Dwarves', 'Night-elves', 'Draenei', 'Worgen']
WOW_RACE_HORDE = [u'兽人', u'牛头人', u'巨魔', u'血精灵', u'亡灵']
WOW_RACE_HORDE_EN = ['Orcs', 'Tauren', 'Ogres', 'Blood elves', 'Goblins', 'Forsaken']

# 允许上传的文件类型
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# cache key
CACHE_TYPE = 'simple'

# socksPool的初始化数量
SOCKSPOOL_SIZE = 2

# 包头长度 byte
PACKAGE_HEAD_SIZE = 2


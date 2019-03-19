# coding: utf-8
# import __builtin__
# import timeit
import time
import math
import functools
from werkzeug.local import LocalProxy
from datetime import datetime, timedelta
from wuaiwow import db, app, cache
from wuaiwow.models import (News, Sidebar, Permission, User, Role, GuildInfo, Donate, Agreement,
                            PermissionRole, permission_has_role, role_is_admin)


# def memoize(ttl=timedelta(seconds=600)):
#     """
#         缓存结果ttl秒，默认10分钟
#         @param ttl 缓存秒数，如果为0，则永不过期；默认10分钟
#     """
#     def wrap(func):
#         cache = {}
#
#         @functools.wraps(func)
#         def wrapped(*args, **kwargs):
#             now = datetime.now()
#             key = func.__name__ + unicode(args) + unicode(kwargs)
#             if key not in cache or (ttl.seconds != 0 and now - cache[key][0] > ttl):
#                 value = func(*args, **kwargs)
#                 cache[key] = (now, value)
#                 # print('Cache miss for key:{}, with ttl:{}'.format(key, ttl.seconds))
#             else:
#                 pass
#                 # print('Cache get for key:{}, with ttl:{}'.format(key, ttl.seconds))
#             return cache[key][1]
#         return wrapped
#     return wrap


# def memoize(obj):
#     """
#         Local cache of the function return value
#     """
#     cache = obj.cache = {}
#
#     @functools.wraps(obj)
#     def memoizer(*args, **kwargs):
#         key = str(args) + str(kwargs)
#         if key not in cache:
#             cache[key] = obj(*args, **kwargs)
#         return cache[key]
#     return memoizer


# @memoize(ttl=LocalProxy(lambda: timedelta(seconds=0)))
def time_by_level(level):
    """
        根据当前等级,计算最小升级时间, H = 0.25 * L * ( L - 1 )
        @param level 当前等级
    """
    if level > 0:
        hour = 0.25 * level * (level - 1)
    else:
        hour = 0
    return hour


# @memoize(ttl=LocalProxy(lambda: timedelta(seconds=0)))
def level_by_time(hour):
    """
        根据在线时间(秒),返回对应的等级, H = 0.25 * L * ( L - 1 )
        @param hour 在线时间,单位时
    """
    if hour > 0:
        level = int((1 + math.sqrt(1 + 16 * hour)) / 2)
    else:
        level = 1
    return level


# @memoize(ttl=LocalProxy(lambda: timedelta(seconds=0)))
def permission_value_by_level(level):
    """
        根据等级,返回相应的权限值, P = 5 * (L + 1)
        @param level 等级
    """
    if level > 0:
        p_value = 5 * (level + 1)
    else:
        p_value = 10
    return p_value


# @memoize(ttl=LocalProxy(lambda: timedelta(seconds=0)))
def level_by_permission_value(value):
    """
        根据权限值返回当前的等级
        @param value 权限值
    """
    if 0 < value <= 100:
        level = int(value / 5) - 1
    else:
        level = 1
    return level


# @memoize(ttl=LocalProxy(lambda: timedelta(seconds=0)))
def get_permission_num():
    """
        返回能升级的permission数量(最高的三个权限不可直升)
    """
    num = Permission.query.count()
    return num - 3   # 最后三个权限不能直升


def get_all_permission(only_value=True):
    """
        返回当前所有有效权限
        @param only_value 只返回value,或者本身
    """

    num = get_permission_num()               # 有效(能升级的)的所有权限
    # noinspection PyBroadException
    try:
        # print(timeit.timeit('UserOnline.query.order_by(UserOnline.online_user_num.desc(),
        # UserOnline.occ_time.desc()).options(UserOnline.cache.from_cache('cache_key')).first()', number=1000))
        ps = Permission.query.order_by(Permission.value.asc()).limit(num).all()
        rst = (p.value for p in ps) if only_value else ps
    except Exception as e:
        rst = list()

    return list(rst)


def get_permission_by_value(value):
    """
        根据权限值,返回相应的权限
        @param value 权限值
    """
    # noinspection PyBroadException
    try:
        # ps = Permission.query.filter(Permission.value == value).options(Permission.cache.from_cache()).first()
        ps = Permission.query.filter(Permission.value == value).first()
    except Exception as e:
        ps = None

    return ps


def get_permission_by_id(permission_id):
    """
        根据id,返回相应的权限
        @param permission_id 权限id
    """
    # noinspection PyBroadException
    try:
        ps = Permission.query.filter(Permission.id == permission_id).first()
    except Exception as e:
        ps = None

    return ps


def get_permission_by_level(level):
    """
        返回等级对应的权限(10,15,20...)
        @param level 等级(1,2,3...)
    """
    if level > 0:
        num = get_permission_num()
        if level > num:
            return None

        value = permission_value_by_level(level)
        ps = get_permission_by_value(value=value)
        return ps
    return None


def get_role_by_name(role):  # need_update
    """
        根据role的name,查找Role实例
        @param role 权限名
    """
    if not role:
        return None
    # noinspection PyBroadException
    try:
        # role_obj = Role.query.filter(Role.role == role).options(Role.cache.from_cache()).first()
        role_obj = Role.query.filter(Role.role == role).first()
    except Exception as e:
        role_obj = None

    return role_obj


def create_role(role, label):
    """
        创建新的角色
        @param role role name
        @param label role label
    """

    role = Role(role=role, label=label)
    db.session.add(role)

    return role


def get_user_by_name(name):
    """
        根据用户名来获取对象
        @param name  用户名
    """
    if not name:
        return None
    # noinspection PyBroadException
    try:
        # user = User.query.filter_by(username=name).options(User.cache.from_cache()).first()
        user = User.query.filter_by(username=name).first()
    except Exception as e:
        user = None

    return user


# def get_permission_by_role(role):
#     """
#         根据给出的role, 查找相应的权限
#         @param role 权限名
#     """
#     role_obj = role
#     if isinstance(role_obj, basestring):
#         role_obj = get_role_by_name(role)
#
#     return role_obj.permission if role_obj else None


def change_permission_by_time(original, value):
    """
        @param original 初始时间
        @param value    当前时间
        根据在线时间(秒),返回对应的权限等级(permission)
        L      H         p
        1      0         10
        2      0.5       15
        3      1.5       20
        4      3.0       25
        5      5.0       30
        6      7.5       35
        7      10.5      40
        .      .
    """
    h1 = int(original) // 1800           # 当前最小分辨率为半小时,单位为半小时
    h2 = int(value) // 1800
    if h1 != h2:
        h1 /= 2.0
        h2 /= 2.0                        # 小时计算,单位为小时
        old_level = level_by_time(h1)
        new_level = level_by_time(h2)
        old_p = get_permission_by_level(old_level)  # 等级对应的权限值
        new_p = get_permission_by_level(new_level)
        if old_p and new_p and new_p != old_p:
            return True, new_p
        else:
            return False, old_p

    return False, None


def get_all_roles(exclude_gm=True):
    """
        返回所有角色
    """

    all_role = Role.query.order_by(Role.id.asc()).all()
    if exclude_gm:
        all_role = (role for role in all_role if not role_is_admin(role))

    return all_role

    # ps = get_all_permission(only_value=False)
    #
    # if need_label:
    #     rst = ((role.role, role.label, p.value) for p in ps for role in p.roles)
    # else:
    #     rst = ((role.role, p.value) for p in ps for role in p.roles)
    #
    # return list(rst)


def find_or_create_permission(value, need_created=False):
    """
        查找或新建权限
        @param need_created if need create new permission when not exist
        @param value Permission.value
    """

    p = get_permission_by_value(value=value)
    if not p and need_created:
        p = Permission(value=value)
        db.session.add(p)
        return True, p
    return False, p


def add_role_to_permission(ps, role):
    """
        添加角色到指定权限
        @param ps 指定权限
        @param role 要添加的角色
    """
    role_obj = role
    if isinstance(role, basestring):
        role_obj = get_role_by_name(role=role)

    if permission_has_role(ps, role_obj.role):
        return True, u"权限已有角色"

    if role_obj and ps:
        associate = PermissionRole()
        associate.role = role_obj
        ps.roles.append(associate)
        db.session.add(ps)
        return True, u"添加成功"

    return False, u"指定角色不存在"


def get_all_permission_role():
    return PermissionRole.query.join(Permission).order_by(Permission.value.desc()).all()


def get_permission_role_by_role_id(role_id):
    return PermissionRole.query.join(Permission).filter(PermissionRole.role_id == role_id).order_by(Permission.value.desc()).all()


def get_less_permission(value):
    """
        获取所有比给定权限值低的权限
        @param value 给定的权限值
    """
    if value <= 0:
        return None
    # noinspection PyBroadException
    try:
        # ps = Permission.query.filter(Permission.value < value).order_by(Permission.value.asc()).options(Permission.cache.from_cache()).all()
        ps = Permission.query.filter(Permission.value < value).order_by(Permission.value.asc()).all()
    except Exception as e:
        ps = None

    return ps


def get_less_permission_user(value):   # need_update
    """
        获取比给定权限值低的所有用户
        @param value 给定的权限值
    """
    if value <= 0:
        return None
    # noinspection PyBroadException
    try:
        # users = User.query.join(Permission).filter(Permission.value < value).order_by(User.confirmed_at.asc()).options(User.cache.from_cache()).all()
        users = User.query.join(Permission).filter(Permission.value < value).order_by(User.confirmed_at.asc()).all()
    except Exception as e:
        users = None

    return users


# def del_role_from_permission(role):
#     """将当前角色从当前权限中移除
#     @param role 将要移除的角色
#     """
#     ps = get_permission_by_role(role=role)
#     if ps:
#         ps.roles.
#
#         db.session.add(ps)
#         return True, ps
#
#     return False, 'Permission not exist'

# need update
def find_or_create_user(username, email, password, permission=10, need_create=True):
    """
        查找或新建用户
        @param username 用户名
        @param email 注册邮箱
        @param password PSD
        @param permission Permission.value
        @param need_create 如果不存在,是否创建新的
    """
    # noinspection PyBroadException
    try:
        # user = User.query.filter(User.email == email).options(User.cache.from_cache()).first()
        user = User.query.filter(User.email == email).first()
    except Exception as e:
        user = None

    if not user and need_create:
        user = User(email=email, username=username, password=app.user_manager.hash_password(password), active=True,
                    confirmed_at=datetime.utcnow())
        created, permission = find_or_create_permission(permission)
        user.permission_id = permission.id
        db.session.add(user)

    return user


def character_in_current_user(character):
    # for char in current_user.characters:
    #     if char.name == character:
    #         existing = True
    #         break
    # else:
    #     existing = False
    # return existing
    pass


# need_update
def find_or_create_news(title):
    """
        查找或新建新闻
        @param title 新闻标题
    """
    title = title.strip(' ')
    if not title:
        return None, False
    exist = True
    # noinspection PyBroadException
    try:
        # one_news = News.query.filter(News.title == title).options(News.cache.from_cache()).first()
        one_news = News.query.filter(News.title == title).first()
    except Exception as e:
        one_news = None

    if not one_news:
        exist = False
        one_news = News(title=title)
        db.session.add(one_news)

    return one_news, exist


def get_news_by_index_num(index=0, number=0):
    """
        返回按时间倒序的从index索引开始的number个news
    """
    if index < 0 or number < 0:
        return tuple()
    # noinspection PyBroadException
    try:
        # all_news = News.query.order_by(News.created.desc()).options(News.cache.from_cache()).all()
        if index == 0 and number == 0:
            all_news = News.query.order_by(News.created.desc()).all()
        else:
            all_news = News.query.order_by(News.created.desc()).all()[index:index+number]
    except Exception as e:
        all_news = tuple()

    return all_news


def get_news_by_id(key_id):
    """
        根据key_id返回news
    """
    if key_id < 0:
        return None
    # noinspection PyBroadException
    try:
        specify_news = News.query.filter_by(id=key_id).first()
    except Exception as e:
        specify_news = None

    return specify_news


def get_all_news_titles():
    """
        返回按时间排序的所有news's title
    """

    return (one.title for one in get_news_by_index_num())


# need update
def find_or_create_sidebar(name):
    """
        查找或新建侧边栏，新建
        @param name 侧边栏名称
    """
    name = name.strip(' ')
    if not name:
        return None
    # noinspection PyBroadException
    try:
        # sd = Sidebar.query.filter(Sidebar.name == name).options(Sidebar.cache.from_cache()).first()
        sd = Sidebar.query.filter(Sidebar.name == name).first()
    except Exception as e:
        sd = None

    if not sd:
        sd = Sidebar(name=name)
        db.session.add(sd)
    return sd


def get_all_sidebar():
    """
        返回所有的sidebar
    """
    return Sidebar.query.order_by(Sidebar.id.asc()).all()


# need_update
def create_guild_info(info):
    """
        新建游戏指南
        @param info 游戏指南
    """
    guild = GuildInfo(info=info)
    db.session.add(guild)

    return guild


def get_latest_guild_info():
    """
        获取最新的游戏指南
    """
    # noinspection PyBroadException
    try:
        # guild = GuildInfo.query.order_by(GuildInfo.date.desc()).options(GuildInfo.cache.from_cache()).first()
        guild = GuildInfo.query.order_by(GuildInfo.date.desc()).first()
    except Exception as e:
        guild = None

    return guild


def get_latest_donate_info():
    """
        获取最新的捐赠信息
    """
    # noinspection PyBroadException
    try:
        donate = Donate.query.order_by(Donate.date.desc()).first()
    except Exception as e:
        donate = None

    return donate


def get_latest_agreement_info():
    """
        获取最新的用户协议
    """
    # noinspection PyBroadException
    try:
        agreement = Agreement.query.order_by(Agreement.update.desc()).first()
    except Exception as e:
        agreement = None

    return agreement


def get_user_messages(user, index=0, number=0):
    """
        返回指定user按时间倒序的从index索引开始的number个message
    """
    if not user or user.is_anonymous or index < 0 or number < 0:
        return tuple()
    # noinspection PyBroadException
    try:
        if index == 0 and number == 0:
            all_message = user.messages.all()
        else:
            all_message = user.messages.all()[index:index+number]
    except Exception as e:
        all_message = tuple()

    return all_message


def get_user_new_messages_num(user):
    """
        返回用户未读消息数量
    """
    return len(list((new_msg for new_msg in get_user_messages(user) if not new_msg.has_read)))


# __builtin__.__dict__.update(locals())

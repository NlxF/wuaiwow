# coding:utf-8
# import StringIO
# from werkzeug.datastructures import FileStorage
from wuaiwow.models.news import News
from wuaiwow.utils.modelHelper import (find_or_create_permission, find_or_create_user, 
                                       get_role_by_name, create_role, db, add_role_to_permission, permission_has_role)


def create_all_permissions(permission_config):
    sorted(permission_config, key=lambda x: x[0])
    permissions = []
    for idx, role in enumerate(permission_config):
        role_obj = get_role_by_name(role=role[1])
        if not role_obj:
            role_obj = create_role(role=role[1], label=role[2])

        created, ps = find_or_create_permission(value=role[0], need_created=True)
        add_role_to_permission(ps, role_obj)             # 添加当前角色到权限
        for previous_role in permission_config[:idx]:    # 权限包含之前的角色
            role_obj = get_role_by_name(role=previous_role[1])
            add_role_to_permission(ps, role_obj)
        permissions.append(ps)
    return permissions


def init_users(permission_config):
    """ init default user """

    perms = create_all_permissions(permission_config)

    #  add default users，
    #  roles, L1=player,L8=GM,L10=admin
    user = find_or_create_user(u'luffy', u'wuaiwow@gmail.com', '1l2u3f4f5y6', perms[-1].value)
    user = find_or_create_user(u'gm', u'xxxxxx@qq.com', '12g3m456', perms[-3].value)
    user = find_or_create_user(u'Zoro', u'xxxxxx@sina.com', '1z2o3r4o56', perms[0].value)
    db.session.commit()


def init_news():
    """ init default news """
    pass


def add_default_data(permission_config):
    """ 初始化数据 """
    init_users(permission_config)
    init_news()


def add_test_data():
    """添加测试数据"""

    [db.session.add(News(title=u'标题:{}'.format(i), summary=u'概要:{}'.format(i), image_url='/static/images/default_title.jpg')) for i in range(10)]
    db.session.commit()

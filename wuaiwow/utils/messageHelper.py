# coding: utf-8
from flask import url_for
from wuaiwow import db
from wuaiwow.models import Message, UserMessage


def get_message_by_title(title):
    if not title:
        return None
    # noinspection PyBroadException
    try:
        msg = Message.query.filter(Message.title == title).first()
    except Exception as e:
        msg = None

    return msg


def create_message(title, content):
    if not title or not content:
        return None

    msg = Message(title=title, content=content)
    db.session.add(msg)

    return msg


def add_user_message(user, msgList):
    """
        添加消息到指定的用户
    """
    if not user or user.is_anonymous or not msgList:
        return False

    for msg in msgList:
        msg_obj = None
        if isinstance(msg, tuple) or isinstance(msg, list):
            msg_obj = create_message(msg[0], msg[-1])
        elif isinstance(msg, Message):
            msg_obj = msg

        if msg_obj:
            associate = UserMessage()
            associate.has_read = False
            associate.message = msg_obj
            user.messages.append(associate)

    db.session.add(user)


def add_new_register_message(user):
    title = u'注册成功'
    content = u"恭喜 {} 注册成功，现在可以开始畅玩游戏. 如需帮助请参考 <a target='_parent' href={}> 游戏指南 </a>".format(user.username, url_for('wuaiwow.tutorial'))
    add_user_message(user, [(title, content)])


def add_reset_password_message(user):
    title = u'重置成功'
    content = ""
    add_user_message(user, [(title, content)])


def add_change_password_message(user):
    title = u'修改成功'
    content = u"密码修改成功，如果不是本人操作的，请立即 <a target='_parent' href={}> 修改密码 </a>".format(url_for('users.change_password'))
    add_user_message(user, [(title, content)])


def add_upgrade_message(user):
    title = u'恭喜升级'
    content = u"{} 恭喜升级到 {}，现在你拥有 <span style='color:#4293ff'>{}</span> 权限. 更多权限请参考 <a target='_parent' href={}> 用户权限表 </a>".format(
        user.username,
        user.permission.value,
        " ".join((role.label for role in user.permission.roles)),
        url_for('player.permission_table'),)
    add_user_message(user, [(title, content)])

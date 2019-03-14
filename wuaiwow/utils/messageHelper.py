# coding: utf-8
from wuaiwow import db
from wuaiwow.models import User, Message, UserMessage


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
    content = u"恭喜 {} 注册成功，现在可以开始游玩游戏.".format(user.username)
    add_user_message(user, [(title, content)])


def add_reset_password_message(user):
    title = u'重置成功'
    content = ""
    add_user_message(user, [(title, content)])


def add_change_password_message(user):
    title = u'修改成功'
    content = ""
    add_user_message(user, [(title, content)])

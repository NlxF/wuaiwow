# coding:utf-8
from sqlalchemy import literal, desc
from sqlalchemy.orm import synonym
from flask_user import UserMixin
from wuaiwow import db, app


def _mapping_race(race):
    try:
        if race in app.config['WOW_RACE_ALLIANCE']:
            idx = app.config['WOW_RACE_ALLIANCE'].index(race)
            race_sx = (u'LM', app.config['WOW_RACE_ALLIANCE_EN'][idx])
        else:
            idx = app.config['WOW_RACE_HORDE'].index(race)
            race_sx = (u'BL', app.config['WOW_RACE_HORDE_EN'][idx])
    except:
        race_sx = (u'未知', u'Unknown')

    return race_sx


def _mapping_class(job):
    try:
        job = job.strip()
        idx = app.config['WOW_CLASS'].index(job)
        class_sx = app.config['WOW_CLASS_SX'][idx]
    except:
        class_sx = u'Unknown'

    return class_sx


# 登录IP表
class UserIp(db.Model):
    __tablename__ = 'user_ip'
    id = db.Column(db.Integer, primary_key=True)
    login_time = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    province = db.Column(db.Unicode(256))
    city = db.Column(db.Unicode(250))
    district = db.Column(db.Unicode(256))
    street = db.Column(db.Unicode(256))
    address = db.Column(db.String(255), default='')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    def __repr__(self):
        return "<UserIP: {0}>".format(self.address)


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)                          # for control
    label = db.Column(db.Unicode(50), nullable=False, default=u'')           # for display purposes
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id', ondelete='CASCADE'))   # one role to one perm

    def __repr__(self):
        return "<Role: {0}>".format(self.role)


class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False, unique=True)               # for @permission_required()
    roles = db.relationship('Role', backref='permission', lazy='dynamic')    # one permission have many role
    users = db.relationship('User', backref='permission', lazy='dynamic')    # one permission for many user

    def __lt__(self, other):  # 小于
        if isinstance(other, Permission):
            return self.value < other.value
        return NotImplemented

    def __eq__(self, other):  # 等于
        if isinstance(other, Permission):
            return self.value == other.value
        return NotImplemented

    def __gt__(self, other):  # 大于
        if isinstance(other, Permission):
            return self.value > other.value
        return NotImplemented

    def __ge__(self, other):  # 不小于
        result = self.__lt__(other)
        if result is NotImplemented:
            return result
        return not result

    def __ne__(self, other):  # 不等于
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self):
        return '<Permission: {0}>'.format(self.value)


class UserMessage(db.Model):
    """
        用户消息关系表
    """
    __tablename__ = 'user_message_association'
    id = db.Column(db.Integer, primary_key=True)
    is_read = db.Column('is_read', db.Boolean, nullable=False, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))

    message = db.relationship('Message', backref=db.backref('users_assocs'))

    def __repr__(self):
        return '<UserMessage: {0}>'.format(self.id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    reset_password_token = db.Column(db.String(100), nullable=False, default='')

    # User Email information
    email = db.Column(db.Unicode(255), nullable=False, default=u'', unique=True)
    confirmed_at = db.Column(db.DateTime())
    _online_time = db.Column(db.Integer, nullable=False, default=literal(10))            # 总在线时间 单位s
    update_time = db.Column(db.Integer, nullable=False, default=literal(10))             # 升级完后的在线时间

    # User Profile information
    active = db.Column('is_active', db.Boolean, nullable=False, default=literal(False))
    avatar = db.Column('avatar', db.String(255), nullable=False, default='/static/images/avatar/default.png')

    # 账户吾币,1RBM=100吾币, 1吾币=100G
    money = db.Column(db.Integer, nullable=False, default=literal(100))

    # user permission
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id', ondelete='CASCADE'))  # one user only one perm

    # user login information
    ips = db.relationship('UserIp', order_by=desc(UserIp.login_time), backref="user", lazy='dynamic')

    # user's messages
    messages = db.relationship('UserMessage', order_by=desc(UserMessage.message_id), backref=db.backref('user'), lazy='dynamic')

    @property
    def online_time(self):
        return self._online_time

    @online_time.setter
    def online_time(self, value):
        from wuaiwow.utils.modelHelper import change_permission_by_time
        elapse_time = value - self._online_time
        level_time = self.update_time if self.update_time else 0
        need_change, new_p = change_permission_by_time(level_time, level_time+elapse_time)
        if need_change and new_p > self.permission:
            self.change_user_permission(new_p)
            self.update_time = 0

            # 同步game server端的account-permission表
            from wuaiwow import tasks
            tasks.update_account_permission.delay([(self.username, new_p.value)])
        else:
            self.update_time += elapse_time
        self._online_time = value

    online_time = synonym('_online_time', descriptor=online_time)

    def change_user_permission(self, permission):
        """
            修改用户的权限
            @param permission 要变更到的权限
        """

        if permission:
            self.permission = permission    # 由Permission 反射而来的属性
            db.session.add(self)

    def is_active(self):
        return self.active

    def has_permission(self, permission):
        """
            如果当前满足权限值要求则返回True
            @param permission 操作要求的权限值
        """
        if hasattr(self, 'permission'):
            value = self.permission.value
        else:
            if hasattr(self, 'user_profile') and hasattr(self.user_profile, 'permission'):
                value = self.user_profile.permission.value
            else:
                value = 0

        return True if value >= permission.value else False

    # @property
    # def is_gm(self):
    #     return self.has_permission(permission=98)
    #
    # @property
    # def is_admin(self):
    #     return self.has_permission(permission=100)

    def _role(self, need_string):
        if need_string:
            if self.permission.value < 98:
                role_name = 'player'  # u'玩家'
            elif self.permission.value < 100:
                role_name = 'GM'  # u'游戏管理员'
            else:
                role_name = 'admin'  # u'超级管理员'
        else:
            role_name = self.permission.value
        return role_name

    @property
    def role_string(self):
        return self._role(True)

    @property
    def role_name(self):
        return self._role(False)

    @property
    def last_login(self):
        ips = self.ips.all()
        return ips[0].login_time if ips else u'未知'

    @property
    def online_time_by_hour(self):
        day = self.online_time / (3600*24)
        hour = self.online_time / 3600.0
        return u"%s天%s小时" % (day, int(round(hour)))

    def __repr__(self):
        return '<User %r>' % self.username


class Message(db.Model):
    """
        消息类
    """
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(512), nullable=False, default=u'无题')
    content = db.Column(db.Text, nullable=True)
    created = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return '<Message %r>' % self.title


class UserOnline(db.Model):
    """
        用户在线信息
    """
    __tablename__ = 'user_online'
    id = db.Column(db.Integer, primary_key=True)
    visitor = db.Column(db.Text, default='')
    register = db.Column(db.Text, default='')
    online_user_num = db.Column(db.Integer, default=literal(0))
    occ_time = db.Column(db.DateTime, default=db.func.now())


# 角色信息
class Characters(db.Model):
    __tablename__ = 'character'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.Integer, unique=True)
    name = db.Column(db.Unicode(255), nullable=False, default=u' ')
    level = db.Column(db.Integer, nullable=False, default=literal(0))
    _race = db.Column(db.Unicode(255), nullable=False, default=u' ')
    race_id = db.Column(db.String(50), nullable=False, default=' ')
    _job = db.Column(db.Unicode(255), nullable=False, default=u' ')
    side = db.Column(db.String(40), default=u'')
    gender = db.Column(db.Unicode(255), nullable=False, default=u'')
    last_login = db.Column(db.DateTime, default=db.func.now())
    played_time = db.Column(db.String(100), nullable=False,  default='0h')
    money = db.Column(db.String(256), nullable=False, default='0g0s0c')
    alive = db.Column(db.Boolean, default=False)
    update = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    isSuccess = db.Column(db.Boolean, nullable=False, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    def to_json(self):
        return {"guid": self.guid,
                "name": self.name,
                "level": self.level,
                "race": self._race,
                "race_id": self.race_id,
                "job": self._job,
                "side": self.side,
                "gender": self.gender,
                "last_login": self.last_login,
                "played_time": self.played_time,
                "money": self.money,
                "alive": self.alive}

    @property
    def race(self):
        return self._race

    @race.setter
    def race(self, value):
        self.side, self.race_id = _mapping_race(value)
        self._race = value

    @property
    def job(self):
        return self._job

    @job.setter
    def job(self, value):
        self._job = _mapping_class(value)

    job = synonym('_job', descriptor=job)
    race = synonym('_race', descriptor=race)

    def __repr__(self):
        return '<Characters %r>' % self.name


class UserInvitation(db.Model):
    """队友招募

     Attributes:
         token-标记
         recruiter-招募者
         recruited-被招募者
    """
    __tablename__ = 'recruit'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.Unicode(40), nullable=False, default=u'')
    # recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    # recruited_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))


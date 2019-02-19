# coding:utf-8
from wuaiwow import db


class Donate(db.Model):
    """
        捐赠信息
    """
    __tablename__ = 'info_donate'
    id = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=db.func.now())


class GuildInfo(db.Model):
    """
        游戏指南信息
    """
    __tablename__ = 'info_guild'
    id = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, default=db.func.now())   # onupdate=db.func.now())


class Agreement(db.Model):
    """
        用户协议
    """
    __tablename__ = 'user_agreement'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    update = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
# coding:utf-8
from wuaiwow import db


class News(db.Model):
    """主页新闻

    """
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(256), nullable=False, default=u'我是标题')
    summary = db.Column(db.Unicode(256), nullable=False, default=u'新闻概要')
    image_url = db.Column(db.String(256), nullable=False, default='')
    content = db.Column(db.Text, nullable=True)
    created = db.Column(db.DateTime, default=db.func.now())
    update = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class Sidebar(db.Model):
    """侧边栏

    """
    __tablename__ = 'sidebar'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(250), nullable=False, default=u'')
    image_url = db.Column(db.String(256), nullable=False, default='')
    content = db.Column(db.Text, nullable=True)
    created = db.Column(db.DateTime, default=db.func.now())
    update = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


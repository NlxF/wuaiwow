# coding:utf-8
from wuaiwow import db


class AlivePrompt(db.Model):
    """存活提示语

    """
    __tablename__ = 'prompt_alive'
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Unicode(256), nullable=False, default=u'')
    alive = db.Column(db.Boolean, nullable=False, default=False)

    def to_json(self):
        return {"prompt": self.prompt, "alive": self.alive}

    @classmethod
    def class_id(cls):
        return 'alive'

    @classmethod
    def title(cls):
        return u'存活提示语'

    def __repr__(self):
        return u'存活提示语'


class LevelPrompt(db.Model):
    """等级提示语

    """
    __tablename__ = 'prompt_level'
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Unicode(256), nullable=False, default=u'')

    def to_json(self):
        return {"prompt": self.prompt}

    @classmethod
    def class_id(cls):
        return 'level'

    @classmethod
    def title(cls):
        return u'等级提示语'

    def __repr__(self):
        return u'等级提示语'


class RacePrompt(db.Model):
    """种族提示语

    """
    __tablename__ = 'prompt_race'
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Unicode(256), nullable=False, default=u'')

    def to_json(self):
        return {"prompt": self.prompt}

    @classmethod
    def class_id(cls):
        return 'race'

    @classmethod
    def title(cls):
        return u'种族提示语'

    def __repr__(self):
        return u'种族提示语'


class JobPrompt(db.Model):
    """职业提示语

    """
    __tablename__ = 'prompt_job'
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Unicode(256), nullable=False, default=u'')

    def to_json(self):
        return {"prompt": self.prompt}

    @classmethod
    def class_id(cls):
        return 'job'

    @classmethod
    def title(cls):
        return u'职业提示语'

    def __repr__(self):
        return u'职业提示语'


class GenderPrompt(db.Model):
    """性别提示语

    """
    __tablename__ = 'prompt_gender'
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Unicode(256), nullable=False, default=u'')

    def to_json(self):
        return {"prompt": self.prompt}

    @classmethod
    def class_id(cls):
        return 'gender'

    @classmethod
    def title(cls):
        return u'性别提示语'

    def __repr__(self):
        return u'性别提示语'


class MoneyPrompt(db.Model):
    """money提示语

    """
    __tablename__ = 'prompt_money'
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Unicode(256), nullable=False, default=u'')

    def to_json(self):
        return {"prompt": self.prompt}

    @classmethod
    def class_id(cls):
        return 'money'

    @classmethod
    def title(cls):
        return u'money提示语'

    def __repr__(self):
        return u'money提示语'

# coding: utf-8
import time
from redis import Redis
from datetime import datetime


class Online(object):
    def __init__(self, app, host='localhost', port=6379, db=0, **kwargs):
        self.app = app
        self.last_min = app.config.get('ONLINE_LAST_MINUTES', 5)
        self.redis = Redis(host=host, port=port, db=db, **kwargs)
        self.user_prefix = "user-activity"
        self.all_users_prefix = "online-users"

    def _make_online(self, user_id):
        now = int(time.time())
        expires = now + self.last_min * 60 + 3
        all_users_key = "{0}/{1:d}".format(self.all_users_prefix, (now // 60))
        user_key = "{0}/{1}".format(self.user_prefix, user_id)
        p = self.redis.pipeline()
        p.sadd(all_users_key, user_id)
        p.set(user_key, now)
        p.expireat(all_users_key, expires)
        p.expireat(user_key, expires)
        p.execute()

    def _make_offline(self, user_id):
        last = self.get_user_last_activity(user_id)
        if last:
            minutes = xrange(self.last_min)
            all_users_keys = ["{0}/{1:d}".format(self.all_users_prefix, (last // 60 - x)) for x in minutes]
            p = self.redis.pipeline()
            [p.srem(all_users_key, user_id) for all_users_key in all_users_keys]
            p.execute()
            self.redis.delete("{0}/{1}".format(self.user_prefix, user_id))

    def get_user_last_activity(self, user_id):
        last_active = self.redis.get("{0}/{1}".format(self.user_prefix, user_id))
        if last_active is None:
            return None
        return int(last_active)
        # return datetime.fromtimestamp(int(last_active))
        # return datetime.utcfromtimestamp(int(last_active))

    def get_online_users(self):
        current = int(time.time()) // 60
        minutes = xrange(self.last_min)
        l = ["{0}/{1:d}".format(self.all_users_prefix, (current - x)) for x in minutes]
        return self.redis.sunion(l)

    def get_valid_elapse_time(self, last_activity):
        elapse_time = time.time() - last_activity
        if elapse_time > self.app.config.get('ONLINE_LAST_MINUTES', 5) * 60 + 3:
            return 0
        else:
            return elapse_time

    def make_current_user_online(self, user_id):
        self._make_online(user_id)

    def make_user_offline(self, user_id):
        self._make_offline(user_id=user_id)


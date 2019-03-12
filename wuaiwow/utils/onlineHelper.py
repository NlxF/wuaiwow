# coding: utf-8
import re
import time
from redis import Redis


def valid_uuid(uuid):
    regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
    match = regex.match(uuid)
    return bool(match)


class Online(object):
    def __init__(self, app):
        self.app = app
        host = app.config.get('CACHE_REDIS_HOST', 'localhost')
        port = app.config.get('CACHE_REDIS_PORT', 6379)
        password = app.config.get('CACHE_REDIS_PASSWORD', None)
        db = app.config.get('ONLINE_DB', 1)
        kwargs = {}
        self.redis = Redis(host=host, port=port, password=password, db=db, **kwargs)
        self.online_interval = app.config.get('ONLINE_LAST_MINUTES', 5)
        self.record_interval = app.config.get('ONLINE_RECORD_INTERVAL', 10)
        self.user_prefix = app.config.get('ONLINE_USER_PREFIX', "online-user-alive")
        self.visitor_prefix = app.config.get('ONLINE_VISITOR_PREFIX', "online-visitor-alive")
        self.user_collection_prefix = app.config.get('ONLINE_ALL_USER_PREFIX', "online-user-collection-at")
        self.visitor_collection_prefix = app.config.get('ONLINE_ALL_VISITOR_PREFIX', "online-visitor-collection-at")
        self.online_record_flag = "online-record-flag"

    def _suitable_prefix(self, visitor, in_set):
        if in_set:
            return self.visitor_collection_prefix if visitor else self.user_collection_prefix
        else:
            return self.visitor_prefix if visitor else self.user_prefix

    def _make_online(self, user_id, visitor):
        now = int(time.time())
        # expires = now + self.online_interval * 60
        expires = now + self.record_interval * 60
        user_collection_key = "{0}:{1:d}".format(self._suitable_prefix(visitor, True), (now // 60))
        user_online_key = "{0}:{1}".format(self._suitable_prefix(visitor, False), user_id)
        with self.redis.pipeline(transaction=False) as pipe:
            pipe.sadd(user_collection_key, user_id)
            pipe.set(user_online_key, now)
            pipe.expireat(user_collection_key, expires)
            pipe.expireat(user_online_key, expires)
            pipe.execute()

    def _make_offline(self, user_id, visitor):
        last = self.get_user_last_activity(user_id, visitor)
        if last:
            # minutes = xrange(self.online_interval)
            interval = xrange(self.record_interval)
            user_collection_keys = ("{}:{:d}".format(self._suitable_prefix(visitor, True), (last // 60 - x)) for x in interval)
            with self.redis.pipeline(transaction=False) as pipe:
                [pipe.srem(users_collection_key, user_id) for users_collection_key in user_collection_keys]
                pipe.delete("{0}:{1}".format(self.user_prefix, user_id))
                pipe.execute()

    def get_user_last_activity(self, user_id, visitor):
        last_active = self.redis.get("{0}:{1}".format(self._suitable_prefix(visitor, False), user_id))
        return int(last_active) if last_active and int(last_active) > 0 else None

    def get_online_users_record(self):
        """
            返回所有在线用户,包括游客
            @return（游客在线，会员在线）
        """
        current_second = time.time()
        current = int(current_second) // 60
        # minutes = xrange(self.online_interval)
        interval = xrange(self.online_interval)
        user_collection_keys = ("{0}:{1:d}".format(self._suitable_prefix(False, True), (current - x)) for x in interval)
        all_online_users = self.redis.sunion(user_collection_keys)
        visitor_collection_keys = ("{0}:{1:d}".format(self._suitable_prefix(True, True), (current - x)) for x in interval)
        all_online_visitors = self.redis.sunion(visitor_collection_keys)

        online_visitors = len(all_online_visitors)
        online_users = len(all_online_users)
        total_online = online_visitors + online_users

        # 更新在线用户统计信息
        need_refresh = False
        exist = self.redis.get(self.online_record_flag)
        if not exist:
            need_refresh = True
            self.redis.set(self.online_record_flag, 1, ex=self.record_interval * 60)  # 每30分钟保存一次

        interval = xrange(self.record_interval)
        user_collection_keys = ("{0}:{1:d}".format(self._suitable_prefix(False, True), (current - x)) for x in interval)
        all_record_users = self.redis.sunion(user_collection_keys)
        visitor_collection_keys = ("{0}:{1:d}".format(self._suitable_prefix(True, True), (current - x)) for x in interval)
        all_record_visitors = self.redis.sunion(visitor_collection_keys)
        member = all_record_users | all_record_visitors
        number = len(member)

        return online_visitors, online_users, need_refresh, number, member, current_second, self.record_interval

    def make_user_online(self, user_id):
        self._make_online(user_id, False)

    def make_user_offline(self, user_id):
        self._make_offline(user_id, False)

    def make_visitor_online(self, user_id):
        self._make_online(user_id, True)

    def make_visitor_offline(self, user_id):
        self._make_offline(user_id, True)



    # def get_valid_elapse_time(self, last_activity):
    #     elapse_time = time.time() - last_activity
    #     if elapse_time > self.last_min * 60 + 1:
    #         return 0
    #     else:
    #         return elapse_time

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
        self.last_min = app.config.get('ONLINE_LAST_MINUTES', 5)
        self.user_prefix = app.config.get('ONLINE_USER_PREFIX', "user-activity")
        self.visitor_prefix = app.config.get('ONLINE_VISITOR_PREFIX', "visitor-activity")
        self.all_users_prefix = app.config.get('ONLINE_ALL_USER_PREFIX', "online-users")
        self.all_visitor_prefix = app.config.get('ONLINE_ALL_VISITOR_PREFIX', "online-visitors")
        self.online_max_flag = "online-max-flag"
        self.online_max_number = "online-max-number"
        self.online_max_member = "online-max-member"
        self.online_max_online_occ_time = "online-max-occ-time"

    def _suitable_prefix(self, visitor, in_set):
        if in_set:
            return self.all_visitor_prefix if visitor else self.all_users_prefix
        else:
            return self.visitor_prefix if visitor else self.user_prefix

    def _make_online(self, user_id, visitor):
        now = int(time.time())
        expires = now + self.last_min * 60 + 1
        all_users_key = "{0}:{1:d}".format(self._suitable_prefix(visitor, True), (now // 60))
        user_key = "{0}:{1}".format(self._suitable_prefix(visitor, False), user_id)
        with self.redis.pipeline(transaction=False) as pipe:
            pipe.sadd(all_users_key, user_id)
            pipe.set(user_key, now)
            pipe.expireat(all_users_key, expires)
            pipe.expireat(user_key, expires)
            pipe.execute()

    def _make_offline(self, user_id, visitor):
        last = self.get_user_last_activity(user_id)
        if last:
            minutes = xrange(self.last_min)
            all_users_keys = ["{}:{:d}".format(self._suitable_prefix(visitor, True), (last // 60 - x)) for x in minutes]
            with self.redis.pipeline(transaction=False) as pipe:
                [pipe.srem(all_users_key, user_id) for all_users_key in all_users_keys]
                pipe.delete("{0}:{1}".format(self.user_prefix, user_id))
                pipe.execute()

    def get_user_last_activity(self, user_id):
        last_active = self.redis.get("{0}:{1}".format(self._suitable_prefix(False, False), user_id))
        return int(last_active) if last_active and int(last_active) > 0 else None

    def get_online_users_record(self):
        """
            返回所有在线用户,包括游客
            @return（游客在线，会员在线）
        """
        current = int(time.time()) // 60
        minutes = xrange(self.last_min)
        user_keys = ("{0}:{1:d}".format(self._suitable_prefix(False, True), (current - x)) for x in minutes)
        all_online_users = self.redis.sunion(user_keys)
        visitor_keys = ("{0}:{1:d}".format(self._suitable_prefix(True, True), (current - x)) for x in minutes)
        all_online_visitors = self.redis.sunion(visitor_keys)

        online_visitors = len(all_online_visitors)
        online_users = len(all_online_users)
        total_online = online_visitors + online_users

        # 更新在线用户统计信息
        number = 0
        member = []
        occ_time = 0
        need_refresh = False
        exist_flag = self.redis.get(self.online_max_flag)
        if exist_flag:
            need_refresh = True
            self.redis.set(self.online_max_flag, 1, ex=30 * 60)  # 每30分钟保存一次
            self.redis.set(self.online_max_number, 0)
        else:
            with self.redis.pipeline() as pipe:
                number = pipe.get(self.online_max_number)
                if number < total_online:
                    pipe.multi()
                    pipe.set(self.online_max_number, total_online)
                    member = all_online_visitors + all_online_users
                    pipe.sadd(self.online_max_member, member)
                    occ_time = time.time()
                    pipe.set(self.online_max_online_occ_time, occ_time)
                    pipe.execute()
                    number = total_online
                else:
                    member = self.redis.get(self.online_max_member)
                    occ_time = self.redis.get(self.online_max_online_occ_time)

        return online_visitors, online_users, need_refresh, number, occ_time, member

    def make_user_online(self, user_id):
        self._make_online(user_id, False)

    def make_user_offline(self, user_id):
        self._make_offline(user_id, False)

    def make_visitor_online(self, user_id):
        self._make_online(user_id, True)

    def make_visitor_offline(self, user_id):
        self._make_online(user_id, True)



    # def get_valid_elapse_time(self, last_activity):
    #     elapse_time = time.time() - last_activity
    #     if elapse_time > self.last_min * 60 + 1:
    #         return 0
    #     else:
    #         return elapse_time

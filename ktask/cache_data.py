# -*- coding: utf-8 -*-
from ktask import redis_client, e_log
from contextlib import contextmanager
import time

try:
    import ujson as json
except:
    from flask import json


class HashContainer(object):
    """哈希管理器，使用redis哈希存储类型"""

    def __init__(self, pattern, fetch_func=None, redis_cli=redis_client):
        self.pattern = pattern
        self.redis_cli = redis_cli

    def set(self, key, field, value):
        return self.redis_cli.hset("%s:%s" % (self.pattern, key), field, value)

    def hmset(self, key, mapping):
        return self.redis_cli.hmset("%s:%s" % (self.pattern, key), mapping)

        # def get(self, key, field):
        #     obj = self.redis_cli.hget("%s:%s" % (self.pattern, key), field)
        #     return obj
        # if obj is None and self.fetch_func is not None:
        #     obj = self.fetch_func(field)
        #     self.redis_cli.hset("%s:%s" % (self.pattern, key), field, obj)
        # if obj:
        #     return int(obj)
        # else:
        #     return 0

    def hget(self, key, field):
        return self.redis_cli.hget("%s:%s" % (self.pattern, key), field)

    def delete(self, key):
        self.redis_cli.delete("%s:%s" % (self.pattern, key))

    def hdel(self, key, field):
        return self.redis_cli.hdel("%s:%s" % (self.pattern, key), field)

    def getall(self, key):
        return self.redis_cli.hgetall("%s:%s" % (self.pattern, key))

    def incr(self, key, field):
        return self.redis_cli.hincrby("%s:%s" % (self.pattern, key), field)

    def get_key_by_val(self, key, val):
        keys = self.redis_cli.hkeys("%s:%s" % (self.pattern, key))
        vals = self.redis_cli.hvals("%s:%s" % (self.pattern, key))
        for i, v in enumerate(vals):
            if v == val:
                return keys[i]
        return 0

    def get_sum_of_val(self, key):
        vals = self.redis_cli.hvals("%s:%s" % (self.pattern, key))
        sum = 0
        for v in vals:
            sum += int(v)
        return sum

    def expire(self, key, seconds):
        self.redis_cli.expire("%s:%s" % (self.pattern, key), seconds)

    def mset(self, key, _dict):
        self.redis_cli.hmset("%s:%s" % (self.pattern, key), _dict)

    def exists(self, key):
        return self.redis_cli.exists("%s:%s" % (self.pattern, key))


class ObjContainer(object):
    """
    对象管理器，使用redis的string作为存储类型，value可以是int string list dict
    """

    def __init__(self, prefix, redis_cli=redis_client, is_str=0):
        self.redis_cli = redis_cli
        self.prefix = prefix
        self.is_str = is_str

    def get(self, key):
        raw_data = self.redis_cli.get('%s:%s' % (self.prefix, key))
        if raw_data is None:
            return None
        if self.is_str:
            return raw_data
        try:
            data = json.loads(raw_data)
            return data
        except:
            return raw_data

    def set(self, key, obj):
        self.redis_cli.set('%s:%s' % (self.prefix, key), json.dumps(obj))

    def delete(self, key):
        self.redis_cli.delete('%s:%s' % (self.prefix, key))

    def expire(self, key, seconds):
        self.redis_cli.expire('%s:%s' % (self.prefix, key), seconds)

    def incr(self, key):
        return self.redis_cli.incr('%s:%s' % (self.prefix, key))


class RedisLock():
    """使用redis的setnx实现分布式的锁"""

    def __init__(self, prefix, lock_expire=None, wait_sleep=None, redis_cli=redis_client):
        self.prefix = prefix
        self.client = redis_cli
        self.lock_expire = lock_expire or 15
        self.wait_sleep = wait_sleep or 0.03

    @contextmanager
    def dist_lock(self, key):
        """
        获得锁和自动释放锁：使用方法：
        with my_redis_lock.dist_lock():
            time.sleep(20)
        """
        expire_at = None
        try:
            expire_at = self._acquire_lock(key)
            yield expire_at
        finally:
            if expire_at and time.time() < expire_at:
                self._release_lock(key)
            else:
                e_log.error('【超时后删除锁】--%s,%s' % (self.prefix, key))

    def _acquire_lock(self, key):
        """获得锁"""
        while 1:
            if self.client.setnx('%s:%s' % (self.prefix, key), 1):
                expire_at = int(time.time() + self.lock_expire)
                self.client.expireat('%s:%s' % (self.prefix, key), expire_at)
                return expire_at
            time.sleep(self.wait_sleep)
        return 0

    def _release_lock(self, key):
        """释放锁"""
        self.client.delete('%s:%s' % (self.prefix, key))


def get_expire():
    """获取到当天网上的秒数"""
    from datetime import datetime, time, timedelta
    dt = datetime.now()
    day_end = dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return int((day_end - dt).seconds)


sessions = ObjContainer('session', is_str=1)  # 保存所有帐号的session_id，以session_id为key，value是user_id,有效期1个月
user_cache = HashContainer("user")  # 保存用户信息的缓存
id_container = ObjContainer('number')
auth_cache = ObjContainer('auth_cache')  # 管理后台用户权限
manage_sessions = ObjContainer('manage_session', is_str=1)  # 保存所有帐号的session_id，以session_id为key，value是user_id
wechat_at_cache = ObjContainer('wechat_at_cache', is_str=0)  # 保存微信的access token信息
wrong_coupon_cnt_cache = ObjContainer('wrong_coupon_cnt_cache', is_str=0)  # 使用错误消费券的次数
project_pv_cache = ObjContainer('project_pv_cache', is_str=0)  # 项目PV
project_buy_cache = ObjContainer('project_buy_cache', is_str=0)  # 购买项目，如果不够钱，记录到cache，充值成功后，直接购买
wrong_pwd_cnt_cache = ObjContainer('wrong_coupon_cnt_cache', is_str=0)  # 管理后台密码错误次数
reply_lock = RedisLock('reply_lock')  # 回复的锁

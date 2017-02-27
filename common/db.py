#coding:utf-8
#created by chen @2016/9/19 1:48 

import motor
import tornadis
from tornado import gen

class MongoDB(object):
    _cofing = {}
    _conns = {}

    @staticmethod
    def config(config):
        MongoDB._cofing.update(config)

    @staticmethod
    def load():
        for name, config in MongoDB._cofing.items():
            MongoDB._conns[name] = motor.MotorClient(max_pool_size=128, tz_aware=True, **config)

    def __init__(self, db_alias="default"):
        self._db_alias = db_alias
        self._conn = None

    def __getattr__(self, item):
        if self._conn is None:
            self._conn = self._conns[self._db_alias]
        db = self._conn[item]
        setattr(self, item, db)
        return db


class RedisDB(object):
    _config = {}
    _client = None

    @classmethod
    def config(cls, config):
        cls._config = config

    @classmethod
    def load(cls):
        cls._client = tornadis.Client(host=cls._config["host"])

    def __init__(self, db_name, prefix=None):
        self.db_name = "%s:%s" % (prefix or self._config["prefix"], db_name)

    @gen.coroutine
    def mget(self, *keys):
        keys = ["%s:%s" % (self.db_name, key) for key in keys]
        res = yield self._client.call("MGET", *keys)
        raise gen.Return(res)

    @gen.coroutine
    def set(self, key, value):
        key = "%s:%s"%(self.db_name, key)
        yield self._client.call("SET", key, value)

if __name__ == "__main__":
    from tornado import ioloop
    from tornadis import Client
    io_loop = ioloop.IOLoop.current()
    from setting import CACHE
    RedisDB.config(CACHE)
    RedisDB.load()
    cache = RedisDB("test")

    @gen.coroutine
    def run():
        client = Client()
        res = yield client.call("SET", "wwww", 1233)
        res = yield cache.set("wwww", 1233)
        print res
    io_loop.run_sync(run)

#coding:utf-8
#created by chen @2016/9/19 1:48 

import motor


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


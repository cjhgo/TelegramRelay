#coding: utf-8
#created at 17-3-7 18:02

from tornado import gen
from common.db import MongoDB
import setting


class Service(object):
    name = ''
    services = {}
    db_name = setting.message_collectionname
    db = MongoDB()[db_name]
    collection_name = ''

    def __init__(self, collection_name=None, db_name=setting.message_collectionname):
        self.collection_name = collection_name or self.collection_name
        self.db_name = db_name

    @staticmethod
    def get_message_id(message_id):
        return tuple(map(int, message_id.split(':')))

    @gen.coroutine
    def handler(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def register_service(cls, service):
        cls.services[service.name] = service

    @classmethod
    def get_service(cls, name, *args, **kwargs):
        service_cls = cls.services.get(name, None)
        return service_cls(*args, **kwargs)


def register_service(cls):
    Service.register_service(cls)
    return cls
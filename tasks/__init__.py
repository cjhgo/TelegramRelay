#coding: utf-8
#created at 16-12-15 17:23

from tornado import gen
from common.db import MongoDB
import setting


class DatagramHandler(object):
    db = MongoDB()
    db_name = setting.message_collectionname
    collection_name = ''

    def __init__(self, collection_name, db_name=setting.message_collectionname):
        self.collection_name = collection_name
        self.db_name = db_name

    @gen.coroutine
    def handler(self, *args, **kwargs):
        raise NotImplementedError

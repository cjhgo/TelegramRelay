#coding:utf-8
#created by chen @2016/9/17 17:10

from tornado import gen
from tornado.web import asynchronous
from tornado.web import  HTTPError
from common.db import MongoDB
from base import RequestHandler


class MessageRequestHandler(RequestHandler):
    db = MongoDB()
    @gen.coroutine
    def get(self):
        pass
        cursor = self.db.test.chen.find({}, {"_id": 0})
        list = yield cursor.to_list(None)
        raise gen.Return({"test": list})
        raise HTTPError(log_message="hhhh")


    # @gen.coroutine
    # def get(self):
    #     res = yield self.gg()
    #     self.write(res)
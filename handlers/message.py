#coding:utf-8
#created by chen @2016/9/17 17:10

from tornado import gen
from base import RequestHandler


class MessageRequestHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        self.write('ahhh')

#coding:utf-8
#created by chen @2016/9/17 16:51

from tornado.web import Application
from common.db import MongoDB

class Applicaton(Application):
    def start(self):
        self.load()

    def load(self):
        MongoDB.load()

    def stop(self):
        self.handlers = []
        self.named_handlers = {}
        # self.add_handlers(".*$", self._wait_handler)

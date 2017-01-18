#coding:utf-8
#created by chen @2016/9/17 16:51

import setting
from tornado.web import Application as TApplicaton
from common.db import MongoDB


class Applicaton(TApplicaton):
    def __init__(self, *args, **kwargs):
        super(Applicaton, self).__init__(*args, **kwargs)
        self.settings = {
            "cookie_secret": setting.cookie_secret
        }

    def start(self):
        self.load()

    def load(self):
        MongoDB.load()

    def stop(self):
        self.handlers = []
        self.named_handlers = {}
        # self.add_handlers(".*$", self._wait_handler)

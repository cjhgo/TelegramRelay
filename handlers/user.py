#coding: utf-8
#created at 17-1-18 17:10

import hashlib
import random
import string
from tornado import gen
from base import RequestHandler, ForbiddenError


class UserRequestHandler(RequestHandler):
    @gen.coroutine
    def post(self):
        code = self.get_body_argument("code")
        if code == "3201328":
            acookie = hashlib.sha1("".join([random.choice(string.printable) for i in range(24)])).hexdigest()
            self.set_secure_cookie("acookie", acookie)
            raise gen.Return()
        else:
            raise ForbiddenError(u"值错误")
#coding:utf-8

import tornado
from handlers import message, user
from handlers import vps


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

urls = (
    # (r"/api/telegram/vocabulary$", message.MessageRequestHandler),
    # (r"/v1/telegram/getUpdate$", message.MessageRequestHandler),
    (r"/", MainHandler),
    (r"/v1/gettitles$", message.TitleRequestHandler),
    (r"/v1/login/$", user.UserRequestHandler),
    (r"/v1/getblogs/$", message.BlogRequestHandler),
    (r"/v1/getnotes/$", message.NotesRequestHandler),
    (r"/v1/getlinks/$", message.ToReadLinkRequestHandler),
    (r"/v1/getkeywords/$", message.KeywordRequestHandler),
    (r"/v1/gettodo/$", message.ToDoRequestHandler),
    (r"/v1/open$", vps.VpsRequestHandler)
)

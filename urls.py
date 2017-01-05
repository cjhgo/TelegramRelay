#coding:utf-8

from handlers import message
from handlers import vps

urls = (
    (r"/api/telegram/vocabulary$", message.MessageRequestHandler),
    (r"/v1/telegram/getUpdate$", message.MessageRequestHandler),
    (r"/v1/open/", vps.VpsRequestHandler)
)

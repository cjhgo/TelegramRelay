#coding:utf-8

from handlers import message

urls = (
    (r"/api/telegram/vocabulary$", message.MessageRequestHandler),
    (r"/v1/telegram/getUpdate$", message.MessageRequestHandler)
)
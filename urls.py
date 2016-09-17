#coding:utf-8

from handlers import message

urls = (
    (r"/api/telegram/vocabulary$", message.MessageRequestHandler),
)
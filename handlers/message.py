#coding:utf-8
#created by chen @2016/9/17 17:10
import json
import logging
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.httpclient import  HTTPRequest
from tornado.web import  HTTPError
from common.db import MongoDB
from base import RequestHandler
import setting


class ResourceRequestHandler(RequestHandler):
    db = MongoDB()
    collection_name = ''

    @gen.coroutine
    def get(self):
        cursor = self.db.queue[self.collection_name].find({}, {"_id": 0, "message_id": 0, "submessage_id": 0})
        res = yield cursor.to_list(None)
        raise gen.Return(res)


class BlogRequestHandler(ResourceRequestHandler):
    collection_name = 'blog'


class ToReadLinkRequestHandler(ResourceRequestHandler):
    collection_name = 'toreadlink'


class KeywordRequestHandler(ResourceRequestHandler):
    collection_name = 'research'


class ToDoRequestHandler(ResourceRequestHandler):
    collection_name = 'todo'


class NotesRequestHandler(ResourceRequestHandler):
    collection_name = 'notes'
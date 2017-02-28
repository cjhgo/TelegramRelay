#coding:utf-8
#created by chen @2016/9/17 17:10
import json
import logging
from tornadis import TornadisException
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.httpclient import  HTTPRequest
from tornado.web import  HTTPError
from common.db import MongoDB, RedisDB
from base import RequestHandler
from tasks.TelegramBot import url_queue
import setting


class ResourceRequestHandler(RequestHandler):
    db = MongoDB()
    db_name = setting.message_collectionname
    collection_name = ''

    @gen.coroutine
    def get(self):
        cursor = self.db[self.db_name][self.collection_name].find({}, {"_id": 0, "message_id": 0, "submessage_id": 0})
        res = yield cursor.sort("crts", -1).to_list(None)
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


class TitleRequestHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        cache = RedisDB("url")
        urls = self.get_query_arguments("url")
        res = yield cache.mget(*urls)
        for i, item in enumerate(res):
            if item is None:
                yield url_queue.put(urls[i])
        raise gen.Return(res)

    @gen.coroutine
    def post(self):
        cache = RedisDB("url")
        urls = self.get_body_arguments("url")

        res = yield cache.mget(*urls)
        if isinstance(res, TornadisException):
            raise HTTPError(status_code=500, log_message="wrong")
        for i, item in enumerate(res):
            if item is None:
                yield url_queue.put(urls[i])
        raise gen.Return(res)
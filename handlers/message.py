#coding:utf-8
#created by chen @2016/9/17 17:10
import json
import pycurl
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.web import asynchronous
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.web import  HTTPError
from common.db import MongoDB
from tasks import getupdate

from base import RequestHandler
# from tornado.web import RequestHandler
import setting




class MessageRequestHandler(RequestHandler):
    db = MongoDB()

    @gen.coroutine
    def getupdate(self, update_id):
        url = setting.TelegarmApiUrl
        url += "/getUpdates?timeout=5&offset=" + str(update_id + 1)


        http_client = CurlAsyncHTTPClient()
        request = HTTPRequest(url, proxy_host='127.0.0.1', proxy_port=8123)
        import logging
        try:
            response = yield http_client.fetch(request)
        except Exception as e:
            print 'here', e
            IOLoop.current().add_callback(getupdate, update_id)
        else:
            data = json.loads(response.body)

            if len(data["result"]) > 0:
                try:
                    update_id = data["result"][-1].get("update_id")
                    print 'hehe', data["result"]
                except:
                    pass
        finally:
            print 'wrong!'
            IOLoop.current().add_callback(getupdate, update_id)

    @gen.coroutine
    def get(self, update_id=77583600):
        yield self.getupdate(update_id)
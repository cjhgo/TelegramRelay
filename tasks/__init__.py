#coding: utf-8
#created at 16-12-15 17:23
from tornado.ioloop import IOLoop
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.web import asynchronous
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import setting
import json

@gen.coroutine
def getupdate(update_id):
    url = setting.TelegarmApiUrl
    url += "/getUpdates?timeout=5&offset=" + str(update_id + 1)
    print url

    http_client = CurlAsyncHTTPClient()
    request = HTTPRequest(url, proxy_host='127.0.0.1', proxy_port=8123)
    import logging
    try:
        response = yield http_client.fetch(request)
    except Exception as e:
        print e
    else:
        data = json.loads(response.body)

        if len(data["result"]) > 0:
            try:
                update_id = data["result"][-1].get("update_id")
                print data["result"]
            except:
                pass
        IOLoop.current().add_callback(getupdate, update_id)

#coding: utf-8
#created at 17-1-5 15:32

import json
from tornado import gen
from tornado.httpclient import HTTPRequest
from tornado.web import HTTPError
from common.mytornado.client import _CurlAsyncHTTPClient as AsyncHTTPClient
from base import RequestHandler

class VpsRequestHandler(RequestHandler):

    @gen.coroutine
    def get(self):
        url = "https://api.64clouds.com/v1/resetRootPassword?veid=277112&api_key=private_gThkVoctF4ZCQRuIPP8d7JxX"
        request = HTTPRequest(url)
        httpclient = AsyncHTTPClient()
        respone = yield httpclient.fetch(request)
        body = json.loads(respone.body)
        if body["error"] == 0:
            raise gen.Return(body["password"])
        else:
            raise HTTPError(log_message="something is wrong!")


#coding: utf-8
#created at 16-12-16 17:27
import logging
from tornado.curl_httpclient import curl_log
from tornado.curl_httpclient import CurlAsyncHTTPClient

curl_log.setLevel(logging.CRITICAL)
class _CurlAsyncHTTPClient(CurlAsyncHTTPClient):
    pass
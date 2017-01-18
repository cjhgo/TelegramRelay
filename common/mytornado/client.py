#coding: utf-8
#created at 16-12-16 17:27
import logging
try:
    from tornado.curl_httpclient import CurlAsyncHTTPClient
    from tornado.curl_httpclient import curl_log
    curl_log.setLevel(logging.CRITICAL)
except:
    from tornado.httpclient import AsyncHTTPClient as CurlAsyncHTTPClient
# from tornado.curl_httpclient import curl_log
# from tornado.curl_httpclient import CurlAsyncHTTPClient
#
# curl_log.setLevel(logging.CRITICAL)
# class _CurlAsyncHTTPClient(CurlAsyncHTTPClient):
#     pass
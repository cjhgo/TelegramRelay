#coding: utf-8
#created at 17-1-10 18:16


#https://github.com/tornadoweb/tornado/blob/master/demos/webspider/webspider.py

import urlparse
import logging
import random
import time
from datetime import timedelta
from bs4 import BeautifulSoup
try:
    from HTMLParser import HTMLParser
    from urlparse import urljoin, urldefrag
except ImportError:
    from html.parser import HTMLParser
    from urllib.parse import urljoin, urldefrag

from tornado.httpclient import HTTPRequest
from tornado import httpclient, gen, ioloop
from common.mytornado.client import CurlAsyncHTTPClient


@gen.coroutine
def get_title(url):
    USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
                   'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
                   'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
                   ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) '
                    'Chrome/19.0.1084.46 Safari/536.5'),
                   ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46'
                    'Safari/536.5'),)

    http_client = CurlAsyncHTTPClient()

    request = HTTPRequest(url, validate_cert=False, headers={'User-Agent': random.choice(USER_AGENTS)},
                          proxy_host='127.0.0.1', proxy_port=8123)
    try:
        try:
            response = yield http_client.fetch(request)
        except NotImplementedError as e:
            request = HTTPRequest(url, validate_cert=False, headers={'User-Agent': random.choice(USER_AGENTS)})
            response = yield http_client.fetch(request)
    except Exception as e:
        logging.debug("something is wrong, %s %s", type(e), e)
        title = None
    else:
        try:
            doc = BeautifulSoup(response.body, 'lxml')
            title = doc.title.string
        except AttributeError as e:
            title = None
    path, query = urlparse.urlparse(url).path, urlparse.urlparse(url).query
    raise gen.Return(title or (path if path != '/' else query) or url)


@gen.coroutine
def run(url_queue, cache):
    while True:
        item = yield url_queue.get()
        try:
            title = yield get_title(item)
            yield cache.set(item, title)
            logging.debug("gettitle: %s : %s", item, title)
        finally:
            url_queue.task_done()
if __name__ == '__main__':
    import logging
    logging.basicConfig()
    io_loop = ioloop.IOLoop.current()
    test_url = "http://mp.weixin.qq.com/s?__biz=MzI4NjYwMjcxOQ=="
    from functools import partial
    get_title = partial(get_title, test_url)
    io_loop.run_sync(get_title)

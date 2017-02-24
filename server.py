#coding:utf-8



from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
import setting
from tasks.TelegramBot import run, fetch_title
from application import Applicaton
from urls import urls


application = None
server = None
ioloop = None

def start():
    global application, server, ioloop
    application = Applicaton(urls, debug=setting.DEBUG, autoreload=setting.AUTORELOAD)
    server = HTTPServer(application)
    server.bind(5000)
    server.start()
    ioloop = IOLoop.instance()
    ioloop.add_callback(run)
    ioloop.add_callback(fetch_title)
    ioloop.add_callback(application.start)
    ioloop.start()

def stop():
    global application, server, ioloop
    ioloop = IOLoop.current()
    def _():
        application.stop()
        server.stop()
        ioloop.stop()
    ioloop.add_callback(_)
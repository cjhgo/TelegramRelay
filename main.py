# coding:utf-8

import sys
from common import vtraceback as traceback
sys.modules["traceback"]=traceback
from logging import config
import logging
import signal
import setting
import server

def exit_handler(signum,frame):
    server.stop()

if __name__ == "__main__":
    signal.signal(signal.SIGHUP, exit_handler)
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)
    logging.basicConfig(level=logging.DEBUG)
    config.dictConfig(setting.LOG)
    server.start()
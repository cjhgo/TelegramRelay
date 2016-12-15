#coding:utf-8
#created by chen @2016/9/17 17:29


import os
from common.db import MongoDB

TelegarmApiUrl = "https://api.telegram.org/bot253258803:AAHsAYENENmKkqNDfxTMimhYuKq5lPbu-dc"
DEBUG = True
AUTORELOAD = True

Mongo_DB = {
    "default": {
        "host": "127.0.0.1"
    }
}


from .log import *

API_ENV = os.getenv("API_ENV","local")

if API_ENV == "local":
    from local import *
elif API_ENV == "production":
    from production import *


MongoDB.config(Mongo_DB)

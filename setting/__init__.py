#coding:utf-8
#created by chen @2016/9/17 17:29


import os
from common.db import MongoDB, RedisDB

# TelegarmApiUrl = "https://api.telegram.org/bot253258803:AAHsAYENENmKkqNDfxTMimhYuKq5lPbu-dc"
DEBUG = True
AUTORELOAD = True

Mongo_DATABASE = {
    "default": {
        "host": "127.0.0.1"
    }
}

CACHE = {
    "host": "127.0.0.1",
    "prefix": "api"
}

cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"

from .log import *

API_ENV = os.getenv("API_ENV", "local")


if API_ENV == "local":
    from local import *
elif API_ENV == "production":
    from production import *


MongoDB.config(Mongo_DATABASE)
RedisDB.config(CACHE)

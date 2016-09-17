#coding:utf-8
#created by chen @2016/9/17 17:29

import os

DEBUG = True
AUTORELOAD = True

MongoDB = {
    "default":{
        "host": "127.0.0.1"
    }
}

API_ENV = os.getenv("API_ENV","local")

if API_ENV == "local":
    from local import *
elif API_ENV == "production":
    from production import *


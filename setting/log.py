#coding: utf-8
#created at 16-12-15 15:16

import os

LOG_PATH=os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))+os.sep+"logs"+os.sep+"api")

LOG={
    "version":1,
}

LOG["formatters"]={
    "console":{
        "fmt":'%(color)s%(asctime)s %(process)d %(levelname)s%(end_color)s %(message)s',
        "datefmt":None,
        "()":"tornado.log.LogFormatter",
    },
    "main":{
        "fmt":'%(color)s%(asctime)s %(process)d %(levelname)s%(end_color)s %(message)s',
        "datefmt":None,
        "color":False,
        "()":"tornado.log.LogFormatter",
    }
}

LOG["handlers"]={
    "console":{
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'console',
    },
    "debug":{
        'level': 'DEBUG',
        'class': 'common.logger.TimedRotatingFileHandler',
        'formatter': 'main',
        'filename':os.path.join(LOG_PATH,"debug.log"),
        "when":"MIDNIGHT",
    },
    "error":{
        'level': 'ERROR',
        'class': 'common.logger.RotatingFileHandler',
        'formatter': 'main',
        'filename':os.path.join(LOG_PATH,"error.log"),
        'maxBytes':1024*1024*1024,
        "backupCount":5,
    },
}

if os.getenv("API_ENV","local")=="local":
    LOG["loggers"]={
        "":{
            'handlers': ['console','debug',"error"],
            'level': 'DEBUG'
        },
        "tornado.access":{
            'handlers': ['console','debug',"error"],
            'level': 'DEBUG'
        },
        "tornado.application":{
            'handlers': ['console','debug',"error"],
            'level': 'DEBUG'
        },
        "tornado.general":{
            'handlers': ['console','debug',"error"],
            'level': 'DEBUG'
        },
    }
else:
    LOG["loggers"]={
        "":{
            'handlers': ['debug',"error"],
            'level': 'DEBUG'
        },
        "tornado.access":{
            'handlers': ['debug',"error"],
            'level': 'DEBUG'
        },
         "tornado.application":{
            'handlers': ['debug',"error"],
            'level': 'DEBUG'
        },
        "tornado.general":{
            'handlers': ['debug',"error"],
            'level': 'DEBUG'
        },
    }
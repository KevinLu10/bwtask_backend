# -*- coding: utf-8 -*-
import logging
import sys

import redis
from flask import Flask
# from flask.ext.cache import Cache
# from flask_cache import Cache
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy

import config

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config.from_object(config)
# cache = Cache(app)

db = SQLAlchemy(app)

redis_client = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT,
                           password=config.REDIS_PASSWORD,db=config.REDIS_DB)
# mongo_client = pymongo.MongoClient(host=config.MONGO_HOST, port=config.MONGO_PORT)[config.MONGO_DB]

from ktask.scheduler import my_scheduler
# 初始化scheduler
sche = APScheduler(scheduler=my_scheduler, app=app)

#初始化所有logger
from ktask import utils
for logger in config.LOGGERS:
    utils.allot_logger(*logger)

c_log=logging.getLogger("common")
a_log=logging.getLogger("access")
e_log=logging.getLogger("error")
pay_log=logging.getLogger("pay")
listed_log=logging.getLogger("listed_log")

from ktask.biz.web import *
# from ktask.manage.bak.web import *


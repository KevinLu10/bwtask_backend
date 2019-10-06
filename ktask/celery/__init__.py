# -*- coding: utf-8 -*-
import logging
from celery import Celery, platforms
from ktask import app
from ktask.celery import config
from functools import wraps
platforms.C_FORCE_ROOT = True#解决linux不用在root用户启动
# from four.model import Cost
error_logger = logging.getLogger('error_log')


def init_celery(app):
    #    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
    celery = Celery(app.import_name, broker=config.CELERY_BROKER_URL)
    # celery.conf.update(app.config)
    celery.config_from_object(config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = init_celery(app)

from ktask.celery.common import *

# def check_db(f):
#     """检查db的连接是否过期"""
#
#     @wraps(f)
#     def _wrapper(*args, **kwargs):
#         try:
#             Cost.query.filter(Cost.key == 1).first()
#         except Exception, e:
#             from sleep import db
#             db.session.rollback()
#             print u'celery check db error (%s) (%s) (%s) (%s)' % (f.__name__, e, args, kwargs)
#         return f(*args, **kwargs)
#
#     return _wrapper

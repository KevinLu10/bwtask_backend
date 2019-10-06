# -*- coding: utf-8 -*-
#########################celery配置

CELERY_REDIS = {
    'host': 'localhost',
    'port': 16379,
    'db': 1,
    'pwd': 'XXXXXXXX',
}

CELERY_BROKER_URL = "redis://:%(pwd)s@%(host)s:%(port)d/%(db)d" % CELERY_REDIS
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24
CELERY_MAX_CACHED_RESULTS = 5000  # default5000，存放多少条结果
CELERYD_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
CELERYD_TASK_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] \n [%(task_name)s(%(task_id)s)] %(message)s'
CELERYD_MAX_TASKS_PER_CHILD = 5
CELERYD_PREFETCH_MULTIPLIER = 4  # 1次接收多少个任务，默认为4，取值为并发数大小最佳

# encoding=utf8
from flask import request
from ktask import config
from ktask import app
from ktask.utils import *
from ktask import utils
from ktask import exception as ext
from ktask.biz.clz.task_clz import task_mgr
from ktask.biz.clz.attend_clz import attend_mgr
from ktask.biz.clz.user_clz import user_mgr
from ktask.model import Task


@app.route('/ktask/v1/attend', methods=['POST', ])
@logmsg
@must_login
@check_response
def add_attend():
    """获取任务"""
    user_id = user_mgr.get_cur_user_id(1)
    to_id = utils.form_get('to_id', type=str, must=1)

    return attend_mgr.add_attend(user_id, to_id)

if __name__ == '__main__':
    pass

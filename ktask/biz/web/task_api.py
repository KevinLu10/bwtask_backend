# encoding=utf8
from flask import request
from ktask import config
from ktask import app
from ktask.utils import *
from ktask import utils
from ktask import exception as ext
from ktask.biz.clz.task_clz import task_mgr
from ktask.biz.clz.user_clz import user_mgr
from ktask.model import Task
from ktask.cache_data import reply_lock

@app.route('/ktask/v1/task', methods=['GET', ])
@logmsg
@must_login
@check_response
def get_task():
    """获取任务"""
    user_id = user_mgr.get_cur_user_id(1)
    task_id = utils.args_get('task_id', type=str, must=1)
    pwd = utils.args_get('pwd', type=str, must=1)
    return task_mgr.get_task(task_id, user_id, pwd)


@app.route('/ktask/v1/task', methods=['POST', ])
@logmsg
@must_login
@check_response
def add_task():
    """发任务"""
    user_id = user_mgr.get_cur_user_id(1)
    title = utils.form_get('title', type=str, must=1)
    c_type = utils.form_get('c_type', type=int, must=1)
    content = utils.form_get('content', type=str, must=1)
    img_uri = utils.form_get('img_uri', type=str, must=1)
    audio_uri = utils.form_get('audio_uri', type=str, must=1)
    ddl = utils.form_get('ddl', type=int, must=1)
    type_ = utils.form_get('type', type=int, must=1)
    if type_ not in Task.ALL_TYPE:
        raise ext.ParamError(u'invalid type')
    return task_mgr.add_task(user_id, type_, title, c_type, content, img_uri, audio_uri, ddl)


@app.route('/ktask/v1/read', methods=['POST', ])
@logmsg
@must_login
@check_response
def add_read():
    """已读"""
    user_id = user_mgr.get_cur_user_id(1)
    task_id = utils.form_get('task_id', type=str, must=1)
    pwd = utils.form_get('pwd', type=str, must=1)

    return task_mgr.read(user_id, task_id, pwd)


@app.route('/ktask/v1/reply', methods=['POST', ])
@logmsg
@must_login
@check_response
def add_reply():
    """回复"""
    user_id = user_mgr.get_cur_user_id(1)
    task_id = utils.form_get('task_id', type=str, must=1)
    pwd = utils.form_get('pwd', type=str, must=1)
    c_type = utils.form_get('c_type', type=int, must=1)
    content = utils.form_get('content', type=str, must=1)
    img_uri = utils.form_get('img_uri', type=str, must=1)
    audio_uri = utils.form_get('audio_uri', type=str, must=1)
    with reply_lock.dist_lock(user_id):
        time.sleep(1)
        return task_mgr.reply(user_id, c_type, content, img_uri, audio_uri, task_id, pwd)


@app.route('/ktask/v1/tasklist', methods=['GET', ])
@logmsg
@must_login
@check_response
def get_task_list():
    """获取任务列表"""
    user_id = user_mgr.get_cur_user_id(1)

    data = [task_mgr.get_sin_task_dict(task) for task in task_mgr.get_my_attend_task(user_id)]
    return dict(data=data)
    # return task_mgr.get_task_list(user_id)


@app.route('/ktask/v1/task/my_index', methods=['GET', ])
@logmsg
@must_login
@check_response
def get_my_task_index():
    """获取我的列表"""
    user_id = user_mgr.get_cur_user_id(1)

    return task_mgr.get_my_task_index(user_id)


@app.route('/ktask/v1/task/del', methods=['POST', ])
@logmsg
@must_login
@check_response
def del_task():
    """删除任务"""
    user_id = user_mgr.get_cur_user_id(1)
    task_id = utils.form_get('task_id', type=int, must=1)
    pwd = utils.form_get('pwd', type=str, must=1)
    return task_mgr.del_task(user_id, task_id, pwd)


@app.route('/ktask/v1/reply/del', methods=['POST', ])
@logmsg
@must_login
@check_response
def del_reply():
    """删除接龙"""
    user_id = user_mgr.get_cur_user_id(1)
    reply_id = utils.form_get('reply_id', type=int, must=1)
    task_id = utils.form_get('task_id', type=int, must=1)
    pwd = utils.form_get('pwd', type=str, must=1)
    return task_mgr.del_reply(user_id, task_id, pwd, reply_id)


if __name__ == '__main__':
    pass

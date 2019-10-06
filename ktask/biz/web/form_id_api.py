# encoding=utf8
from flask import request
from ktask import config
from ktask import app
from ktask.utils import *
from ktask import utils
from ktask import exception as ext
from ktask.biz.clz.user_clz import user_mgr
from ktask.biz.clz.form_id_clz import form_id_mgr


@app.route('/ktask/v1/formid/add', methods=['POST', ])
@logmsg
@must_login
@check_response
def add_form_id():
    """提交form_id"""
    form_id = utils.form_get("form_id", '', type=str)
    user_id = user_mgr.get_cur_user_id(1)
    form_id_mgr.add_form_id(user_id, form_id)
    return dict()


def f(param):
    user_id,req_data=param
    import copy
    req_data=copy.deepcopy(req_data)
    ret = form_id_mgr.get_form_id(user_id)
    req_data['user_id']=ret[0].user_id
    req_data['form_id']=ret[0].form_id
    print ret[0].user_id,ret[0].form_id,req_data
    from ktask import db
    db.session.remove()


# @app.route('/ktask/v1/formid/test', methods=['POST', ])
# @logmsg
# @check_response
# def add_form_idtest():
#     """提交form_id"""
#     req_data={}
#     data=[[7,req_data],[8,req_data]]
#     form_id_mgr.multi_thread(f,data)
#     return '1'


if __name__ == '__main__':
    pass

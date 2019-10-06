# encoding=utf8
from ktask import app
from ktask.utils import *
from ktask import utils
from ktask import exception as ext
from ktask.biz.clz.user_clz import user_mgr


@app.route('/ktask/v1/login', methods=['POST', ])
@logmsg
@check_response
def login():
    username = utils.json_get("username")
    password = utils.json_get("password")
    if username is None:
        raise ext.ParamError(u'username不能为空')
    if password is None:
        raise ext.ParamError(u'password不能为空')
    return user_mgr.login(username, password)


if __name__ == '__main__':
    pass

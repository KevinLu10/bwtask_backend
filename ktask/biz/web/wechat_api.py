# encoding=utf8
from flask import request
from ktask import config
from ktask import app
from ktask.utils import *
from ktask import utils
from ktask import exception as ext
from ktask.biz.clz.wetchat_clz import wechat_mgr


@app.route('/ktask/v1/wetchat/js-sign', methods=['GET', ])
@logmsg
@must_login
@check_response
def get_wetchat_js_sign():
    """获取微信JSAPI的注册信息"""
    url = request.args.get("url", type=str)

    return wechat_mgr.get_js_jdk_sign(url)


if __name__ == '__main__':
    pass

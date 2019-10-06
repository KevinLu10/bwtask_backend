# encoding=utf8
from flask import request, render_template
from ktask import config
import hashlib
from ktask import app
from ktask.utils import *

from ktask import wx_utils


@app.route('/ktask/html/apps/<name1>/<name2>', methods=['GET', ])
@html_logmsg
# @wx_utils.debug_info
@wx_utils.detail_info
def get_front_page(name1, name2):
    """获取前端的页面"""
    if name1.startswith("{{") or name2.startswith("{{"):
        return ''
    path = os.path.join(config.LOCAL_ROOT, 'front', 'html', 'apps', name1, name2)
    if not os.path.exists(path):
        return make_response('',404)
    with open(path, 'r') as f:
        return f.read()

@app.route('/ktask/html/component/<name1>', methods=['GET', ])
def get_front_component_page(name1):
    """获取前端组件的页面"""
    if name1.startswith("{{") :
        return ''
    path = os.path.join(config.LOCAL_ROOT, 'front', 'html', 'component', name1)
    with open(path, 'r') as f:
        return f.read()


@app.route('/ktask/v1/html/apps/test', methods=['GET', ])
@html_logmsg
# @wx_utils.debug_info
@wx_utils.detail_info
def get_front_page_test():
    """获取前端的页面"""
    from flask import g
    return str(g.user_id)
    return render_template('html/apps/asset/assets.html')
    return "aaabbb"



@app.route('/ktask', methods=['GET', ])
def check_weixin_token():
    """获取前端的页面"""
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    echostr = request.args.get("echostr")
    sign_list = [timestamp, nonce, 'TTSharing_DaMi']
    sign_list.sort()
    sign_str = "".join(sign_list)
    # sha1加密
    sign = hashlib.sha1(sign_str).hexdigest()
    return echostr if sign == signature else  'sign fail'

@app.route('/ktask/v1/qiniu/up', methods=['GET', ])
def get_qiniu_upload_token():
    """获取七牛的上传token"""
    from qiniu import Auth
    a=Auth(config.QINIU_ACCESS_KEY,config.QINIU_SECRET_KEY)
    token=a.upload_token("ktask")
    return json.dumps(dict(
        uptoken=token,
        token=token,
        t=int(time.time()+3600),
        status=1
    ))




if __name__ == '__main__':
    pass

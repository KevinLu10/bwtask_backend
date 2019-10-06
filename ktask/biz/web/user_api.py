# encoding=utf8
from flask import request
from ktask import config
from ktask import app
from ktask.utils import *
from ktask import utils
from ktask import exception as ext
from ktask.biz.clz.user_clz import user_mgr
from ktask.biz.clz.img_clz import img_mgr


@app.route('/ktask/v1/user/wxa/login', methods=['POST', ])
@logmsg
@check_response
def user_wxa_login():
    """小程序，登录"""
    code = utils.form_get('code', type=str)
    nickname = utils.form_get('nickname', type=str)
    img_url = utils.form_get('img_url', type=str)

    if code is None:
        raise ext.ParamError(u'invalid code')

    return user_mgr.wxa_login(code, nickname, img_url)


@app.route('/ktask/v1/upload', methods=['POST', ])
@logmsg
@must_login
@check_response
def upload():
    """文件上传"""
    file_path = request.headers.get('FILEPATH')
    if file_path is None :
        raise ext.ParamError(U'上传文件错误')
    suffix=file_path.split('.')[-1]
    if suffix not in ('png','jpg','jpeg','mp3','silk'):
        raise ext.ParamError(U'不支持该文件格式')
    # mtype = 'mp3' if suffix == 'mp3' else "image/jpeg"

    f = request.files['file']
    data = f.read()
    print 'data len',len(data)
    key = img_mgr.upload_file_online1('', data, suffix)
    return key

if __name__ == '__main__':
    pass

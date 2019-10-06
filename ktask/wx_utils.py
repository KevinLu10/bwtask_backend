# encoding=utf-8
__author__ = 'kevinlu1010@qq.com'
import ast,requests
import urllib
import copy
import urllib, urllib2
from ktask import config
from functools import wraps
from flask import request, redirect, g,make_response
import traceback
from ktask.biz.clz.user_clz import user_mgr
from ktask.biz.clz.session_clz import session_mgr
from ktask import utils,e_log
from ktask import exception as ext
import time
'''
微信专用工具模块
'''
# ###############################
# 获取用户信息相关
# ###############################
open_id = 'test'
open_id = 'xxx-xxx'  # wo
# open_id = 'o7VmGt1Y07bPnfgwSjZa-IjuTYww' #jizai
common_kwargs = {
    'openid': open_id,
    'user_id': open_id,
    'info': {'openid': open_id, 'nickname': '', 'headimgurl': ''}

}
DEBUG = True
DEBUG = False


def get_redirect_url(uri, is_info=0, state=''):
    '''
    获取url，改url可以访问微信的网址，然后会重定向回来我们的网址，而且附带访问的微信用户的信息
    uri 需要跳转到的uri  如/cherrs

    is_info 是否获取详细信息，如果为1，就获取用户的详细信息，包括名字，图片，否则就获取基本信息，只有open_id
    param state的内容
    返回 url
    '''
    pre_url = config.LOCAL_HOST
    appid = config.APPID
    scope = 'snsapi_userinfo' if is_info else 'snsapi_base'
    # data = {'redirect_uri': pre_url + uri,
    # 'appid': appid,
    # 'response_type': 'code',
    # 'scope': scope,
    #
    # }
    # state='123'
    # urlencode = urllib.urlencode(data)
    # wei_url = 'https://open.weixin.qq.com/connect/oauth2/authorize?' + urlencode + '&state=%s#wechat_redirect' % state
    # return wei_url
    redirect_uri_str = urllib.urlencode({'redirect_uri': pre_url + uri})
    state=int(time.time())
    str_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&%s&response_type=code&scope=%s&state=%s#wechat_redirect"
    wx_url = str_url % (appid, redirect_uri_str, scope,state)
    return wx_url


def get_base_info(code):
    '''
    通过获取的code，访问微信的api，获取用户基本信息(只有openid)
    return 用户的open id
    '''

    if not code: return ''
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    try:
        data = {'appid': config.APPID, 'secret': config.SECRET, 'code': code, 'grant_type': 'authorization_code'}
        post_body = urllib.urlencode(data)
        f = urllib2.urlopen(url, post_body).read()
        r = ast.literal_eval(f)  # 字符串转换成字典
        # print r
        # r['user_id'] = r['openid']
        return r
    except:
        return {}


# def get_detail_info(code):
#     '''
#     获取用户的详细信息
#     return dict {'userID':'','nickname':''m',headimgurl':''}
#     '''
#     ret = {'user_id': '', 'nick_name': '', 'head_url': ''}
#     url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
#     try:
#         data = {'appid': config.APPID, 'secret': config.SECRET, 'code': code, 'grant_type': 'authorization_code'}
#         post_body = urllib.urlencode(data)
#         f = urllib2.urlopen(url, post_body).read()
#         r = ast.literal_eval(f)  # 字符串转换成字典
#         from four import e_log
#         e_log.error(u'微信详细信息1：%s',r)
#         # 获取用户详细信息
#         # access_token = r['access_token']
#         access_token = r.get('access_token')
#         ret['user_id'] = r.get('openid')
#         url = 'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN' % (
#             access_token, ret['user_id'])
#         f = urllib2.urlopen(url).read()
#         r = ast.literal_eval(f)  # 字符串转换成字典
#         print r
#         ret['nick_name'] = urllib.unquote(r.get('nickname', ''))
#         ret['head_url'] = urllib.unquote(r.get('headimgurl', '').replace('\\', ''))
#     except urllib2.URLError, e:
#         print traceback.print_exc()
#         return ret
#     return ret
def get_detail_info_step2_v1(access_token, openid):
    url = 'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN' % (access_token, openid)
    ret2 = requests.get(url)
    e_log.info(u"微信详细信息2(v1)，ret :%s ret content:%s", ret2.status_code, ret2.content)
    ret2_json = ret2.json()
    if 'errcode' in ret2_json:
        raise Exception(u'调用微信详细信息2(v1)接口失败')
    return ret2_json


def get_detail_info_step2_v2(access_token, openid):
    """根据openid和access_token获取用户的基本信息，包含unionID的版本
    返回结果
    {
       "subscribe": 1, 
       "openid": "o6_bmjrPTlm6_2sgVt7hMZOPfL2M", 
       "nickname": "Band", 
       "sex": 1, 
       "language": "zh_CN", 
       "city": "广州", 
       "province": "广东", 
       "country": "中国", 
       "headimgurl":  "http://wx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4
    
    eMsv84eavHiaiceqxibJxCfHe/0",
    
      "subscribe_time": 1382694957,
      "unionid": " o6_bmasdasdsad6_2sgVt7hMZOPfL"
      "remark": "",
      "groupid": 0,
    
      "tagid_list":[128,2]
    
    }
    """
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN' % (access_token, openid)
    ret2 = requests.get(url)
    e_log.info(u"微信详细信息2(v2)，ret :%s ret content:%s", ret2.status_code, ret2.content)
    ret2_json = ret2.json()
    return ret2_json

def get_detail_info_app(access_token, openid):
    """根据openid和access_token获取用户的基本信息，包含unionID的版本,app版本
    """
    url = 'https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN' % (access_token, openid)
    ret2 = requests.get(url)
    e_log.info(u"微信详细信息2(app)，ret :%s ret content:%s", ret2.status_code, ret2.content)
    ret2_json = ret2.json()
    return ret2_json

def get_detail_info_wxa(code):
    """根据openid和access_token获取用户的基本信息，包含unionID的版本,小程序版本
    """
    data=dict(
        appid=config.WEIXIN_WXA_APPID,
        secret=config.WEIXIN_WXA_SECRET,
        grant_type='authorization_code',
        js_code=code
    )
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    ret2 = requests.get(url,params=data)
    e_log.info(u"微信详细信息2(wxa)，ret :%s ret content:%s", ret2.status_code, ret2.content)
    ret2_json = ret2.json()
    return ret2_json

def get_detail_info(code):
    '''
    获取用户的详细信息
    return dict {'userID':'','nickname':''m',headimgurl':''}
    '''
    url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    try:
        # raise
        data = dict(
            appid=config.APPID,
            secret=config.SECRET,
            code=code,
            grant_type='authorization_code'
        )
        ret1 = requests.post(url, data=data)
        e_log.info(u"微信详细信息1，ret :%s ret content:%s code:%s",ret1.status_code,ret1.content,code)
        ret1_json = ret1.json()
        from ktask.biz.clz.wetchat_clz import wechat_mgr
        at=wechat_mgr.get_new_at()['access_token']
        ret3_json = get_detail_info_step2_v2(at, ret1_json['openid'])# unionid 版本
        ret2_json = get_detail_info_step2_v1(ret1_json['access_token'], ret1_json['openid']) #普通的公众号版本
        return dict(
            # nick_name=u'\xe5\x81\xa5\xe6\x98\x9f'
            nick_name=ret2_json.get('nickname','') ,#.encode('unicode-escape').decode('string_escape'),
            head_url=ret2_json.get('headimgurl','').replace('\\', ''),
            user_id=ret3_json['openid'],
            unionid=ret3_json['unionid'],
        )
    except:
        print traceback.format_exc()
        e_log.error("获取微信详细信息失败，code:%s", code)
        e_log.error(traceback.format_exc())
        return None


def base_info(func):
    '''
    装饰器，获取用户的基本信息
    通过 kwargs['openid']访问用户的openid
    '''

    @wraps(func)
    def _f(*args, **kwargs):
        # if DEBUG:
        #     kwargs.update(common_kwargs)
        #     return func(*args, **kwargs)
        code = request.args.get('code')
        print 'CODE', code
        if not code:
            wx_url = get_redirect_url(kwargs.get('uri') or request.path, '')
            print wx_url
            return redirect(wx_url)
        else:
            info = get_base_info(code)
            kwargs.update(info)
            if 'user_id' not in kwargs:
                kwargs['user_id'] = kwargs.get('openid')
            return func(*args, **kwargs)

    return _f


def get_wx_raw_url():
    """获取去除code和state两个参数的url"""
    args = copy.copy(dict(request.args.to_dict()))
    for key in ['code','state']:
        if key in args:
            args.pop(key)
    return '%s?%s' % (request.path, urllib.urlencode(args))



def detail_info(func):
    '''
    装饰器，获取用户的详细信息
    kwargs['uri']  调用函数需要指定uri
    通过kwargs['info']访问用户的详细信息 ,有openid,nickname,headimgurl这些key，info的格式是字典
    如果用户不通过授权，info为{}
    '''

    @wraps(func)
    def _f(*args, **kwargs):
        if config.HTML_DEBUG:
            tpl=func(*args, **kwargs)
            resp=make_response(tpl)
            resp.set_cookie('user_id','10000')
            return resp
        session = request.cookies.get('session')
        if session:
            user_id = session_mgr.check_session(session)
            if user_id:  # 如果用户已登录
                g.user_id = user_id
                tpl=func(*args, **kwargs)
                resp=make_response(tpl)
                return resp
        # 如果用户没有登陆，跳转到微信的url，获取用户信息
        code = request.args.get('code')
        if not code:
            state = request.args.get('state')
            wx_url = get_redirect_url(kwargs.get('uri') or request.full_path, 1, state)
            # return wx_url
            return redirect(wx_url)
        else:
            if code == 'authdeny':
                kwargs['info'] = {}
                kwargs['state'] = ''
                return utils.return_error(ext.MustLoginError)
            else:
                info = get_detail_info(code)
                # save_info_to_sql(info)
                if info is None:
                    return redirect(get_wx_raw_url())
                    # return utils.return_error(ext.LoginError)
                user = user_mgr.login_unionid(info['unionid'], info['nick_name'], info['head_url'],info['user_id'])
                if user is False:
                    return utils.return_error(ext.LoginError)
                g.user_id = user['user_id']
                tpl=func(*args, **kwargs)
                resp=make_response(tpl)
                resp.set_cookie('session',user['session_id'])
                resp.set_cookie('user_id',str(user['user_id']))
                return resp
    return _f


def debug_info(func):
    '''
    装饰器，调试使用
    通过 kwargs['openid']访问用户的openid
    '''

    def _f(*args, **kwargs):
        kwargs.update(common_kwargs)
        return func(*args, **kwargs)

    return _f


if __name__ == '__main__':
    pass

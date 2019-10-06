# encoding=utf-8
__author__ = 'kevinlu1010@qq.com'
import time
import traceback
from ktask import config
from ktask import e_log
import requests
from ktask.cache_data import wechat_at_cache
from ktask import exception as ext
import hashlib
from ktask import utils


class WechatMgr():
    '''
    微信信息的管理
    '''
    ACCESS_TOKEN_KEY = 'access_token'
    JS_TICKET_KEY = 'js_ticket'
    WXA_ACCESS_TOKEN_KEY = 'wxa_access_token'

    def __init__(self, name, **kwargs):
        self.name = name
        self.e_log = e_log

    def get_new_at(self):
        '''
        获取新的access token
        '''
        try:
            url = config.WEIXIN_ACCESS_TOKEN_URL
            data = dict(
                appid=config.APPID,
                secret=config.SECRET,
                grant_type='client_credential'
            )
            result = requests.get(url, params=data, timeout=10)
            if result.status_code == 200:
                ret = result.json()
                at_data = dict(
                    access_token=ret['access_token'],
                    expires_in=ret['expires_in'],
                    get_time=int(time.time()),
                )
                wechat_at_cache.set(self.ACCESS_TOKEN_KEY, at_data)
                return at_data

        except:
            self.e_log.error(traceback.format_exc())
            self.e_log.error(u'【获取at】失败')
            raise ext.OtherError(u'获取微信access_token失败')
        raise ext.OtherError(u'获取微信access_token失败')

    def is_data_expire(self, at_data):
        """检查access_token是否过期"""
        expires_in = int(at_data['expires_in'])
        get_time = int(at_data['get_time'])
        return time.time() >= get_time + expires_in

    def get_at(self):
        '''
        获取可用的access token
        '''
        at_data = wechat_at_cache.get(self.ACCESS_TOKEN_KEY)
        if not at_data or self.is_data_expire(at_data):
            at_data = self.get_new_at()
        return at_data['access_token']

    def get_new_js_ticket(self):
        '''
        获取新的jsapi_ticket
        '''
        # print 'get_new_js_ticket'
        try:
            at = self.get_at()
            url = '%s?access_token=%s&type=jsapi' % (config.JS_API_TICKET_URL, at)
            result = requests.get(url, timeout=10)
            if result.status_code == 200:
                ret = result.json()
                at_data = dict(
                    ticket=ret['ticket'],
                    expires_in=ret['expires_in'],
                    get_time=int(time.time()),
                )
                wechat_at_cache.set(self.JS_TICKET_KEY, at_data)
                return at_data
        except:
            self.e_log.error(traceback.format_exc())
            self.e_log.error(u'【获取at】失败')
            raise ext.OtherError(u'获取微信access_token失败')
        raise ext.OtherError(u'获取微信access_token失败')

    def get_js_ticket(self):
        '''
        获取可用的jsapi_ticket
        '''
        data = wechat_at_cache.get(self.JS_TICKET_KEY)
        if not data or self.is_data_expire(data):
            data = self.get_new_js_ticket()
        return data['ticket']

    def get_sign(self, params, type='sha1'):
        '''
        对参数进行排序然后加密
        :param params:dict
        :return: str
        '''
        params_tuple = params.items()
        params_tuple = [(x[0].lower(), x[1]) for x in params_tuple if x[1]]
        params_tuple.sort(key=lambda x: x[0])
        params_tuple = ['='.join(x) for x in params_tuple]
        params_str = '&'.join(params_tuple)
        # print params_str
        if type == 'sha1':
            sign = hashlib.sha1(params_str).hexdigest()
        else:
            sign = hashlib.md5(params_str).hexdigest()
        return sign

    def get_js_jdk_sign(self, url):
        '''
        获取签名，用于js api认证
        :param url: 调用jsapi的url，
        :param ticket: 可用的ticket 通过at_man获取
        :return:{'url':url,'ticket':ticket,'timestamp':str(int(time.time())),'noncestr':noncestr,'sign':sign}
        '''

        ticket=self.get_js_ticket()
        noncestr = utils.rand_str(20)
        url = url.split('#')[0]
        params = {
            'url': url, 'jsapi_ticket': ticket,
            'timestamp': str(int(time.time())),
            'noncestr': noncestr}
        params['sign'] = self.get_sign(params)
        params['appid'] = config.APPID
        return params


    def get_wxa_new_at(self):
        '''
        获取小程序新的access token
        '''
        try:
            url = config.WEIXIN_ACCESS_TOKEN_URL
            data = dict(
                appid=config.WEIXIN_WXA_APPID,
                secret=config.WEIXIN_WXA_SECRET,
                grant_type='client_credential'
            )
            result = requests.get(url, params=data, timeout=10)
            if result.status_code == 200:
                ret = result.json()
                at_data = dict(
                    access_token=ret['access_token'],
                    expires_in=ret['expires_in'],
                    get_time=int(time.time()),
                )
                wechat_at_cache.set(self.WXA_ACCESS_TOKEN_KEY, at_data)
                return at_data

        except:
            self.e_log.error(traceback.format_exc())
            self.e_log.error(u'【获取wxa at】失败')
            raise ext.OtherError(u'获取微信wxa access_token失败')
        raise ext.OtherError(u'获取微信wxa access_token失败')
    def get_wxa_at(self):
        '''
        获取小程序可用的access token
        '''
        at_data = wechat_at_cache.get(self.WXA_ACCESS_TOKEN_KEY)
        if not at_data or self.is_data_expire(at_data):
            at_data = self.get_wxa_new_at()
        return at_data['access_token']

wechat_mgr = WechatMgr('WechatMgr')

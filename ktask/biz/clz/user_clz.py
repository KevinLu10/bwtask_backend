# encoding=utf8
# -*- coding: utf-8 -*-
from datetime import datetime

import requests

from ktask import config
from ktask import db, utils, e_log
from ktask import exception as ext
from ktask.biz.clz.id_clz import id_mgr
from ktask.biz.clz.session_clz import session_mgr
from ktask.cache_data import user_cache,get_expire
from ktask.model import User

class UserMgr(object):
    # 用户管理类
    def __init__(self, name, **kwargs):
        self.name = name
        self.e_log = e_log

    def _get_user(self, user_id):
        """从数据库获取用户信息"""
        user = User.query.filter(User.id == user_id).first()
        if not user:
            raise ext.NotExistsError(u'用户不存在')
        return dict(
            nickname=user.nickname,
            # img_url=img_mgr.get_url(user.img_url),
            img_url=user.img_url,
            wxa_openid=user.wxa_openid,
            # money=user.money,
        )

    def get_cache(self, user_id):
        """获取用户cache"""
        if user_cache.exists(user_id):
            return user_cache.getall(user_id)
        else:
            cache = self._get_user(user_id)
            user_cache.mset(user_id, cache)
            user_cache.expire(user_id,get_expire())
            return cache

    def login(self, openid, nickname, img_url):
        """登录"""
        if len(openid)<5:
            raise ext.OtherError(u'获取OPENID失败')
        user = User.query.filter(User.wxa_openid == openid).first()
        if not user:
            user = User(wxa_openid=openid, nickname=nickname, img_url=img_url)
            db.session.add(user)
        user.last_login = datetime.now()
        user.nickname = nickname
        user.img_url = img_url
        log_msg = u'【登陆】入库失败，openid:%s,nickname:%s' % (openid, nickname)
        if not utils.commit_db(db, self.e_log, log_msg):
            return False
        return session_mgr.set_new_session(user.id)
        # return user

    def login_unionid(self, unionid, nickname, img_url, openid='',wxa_openid=''):
        """登录 unionid版本"""
        if len(unionid) < 5:
            raise ext.OtherError(u'获取unionid失败')
        user = User.query.filter(User.unionid == unionid).first()
        if not user:
            user = User(openid=unionid, unionid=unionid, nickname=nickname, img_url=img_url)
            db.session.add(user)
        user.last_login = datetime.now()
        user.nickname = nickname
        # self.e_log.error('nickname %s',repr(nickname))
        user.img_url = img_url
        if len(openid) > 5: #小程序和js支付都需要用到openid，所以要更新openid
            user.openid = openid
        if len(wxa_openid) > 5: #小程序和js支付都需要用到openid，所以要更新openid
            user.wxa_openid = wxa_openid

        log_msg = u'【登陆】入库失败，unionid:%s,nickname:%s' % (unionid, nickname)
        if not utils.commit_db(db, self.e_log, log_msg):
            return False
        return session_mgr.set_new_session(user.key)
        # return user

    def get_cur_user_id(self, is_must):
        """获取当前状态的用户ID"""
        from flask import g
        # user_id1 = request.args.get('user_id')
        # user_id2 = request.form.get('user_id')
        user_id = g.get("user_id", None)
        # if config.HTML_DEBUG:
        #     user_id = 10237
        print 'user_id',user_id
        if is_must and user_id is None:
            raise ext.NotLoginError
        return int(user_id)

    def get_user_asset_num(self, user_id):
        """获取用户拥有资产的数量，也就是消费券的数量"""
        result = db.session.query(func.sum(Asset.count)).filter(Asset.user_id == user_id, Asset.status == 1).first()
        return result[0] if result else 0
    def get_user_freeze_asset_num(self, user_id):
        """获取用户拥有冻结资产的数量"""
        result = db.session.query(func.sum(Asset.freeze_count)).filter(Asset.user_id == user_id, Asset.status == 1).first()
        return result[0] if result else 0

    def get_user_stock(self, user_id):
        """获取用户拥有的已转换未股权的资产的数量"""
        result = db.session.query(func.count(Asset.asset_id)).filter(Asset.user_id == user_id, Asset.stock > 0,
                                                                     Asset.status == 1).first()
        return result[0] if result else 0

    def get_index(self, user_id):
        """获取用户首页的数据"""
        cache = self.get_cache(user_id)
        return dict(
            nickname='%s(%s)'%(cache['nickname'],user_id),
            img_url=cache['img_url'],
            stock_num=self.get_user_stock(user_id) or 0,
            asset_num=self.get_user_asset_num(user_id) or 0,
            freeze_asset_num=self.get_user_freeze_asset_num(user_id),
            money=cache['money'],
            nickname_wxa=cache['nickname'],
            user_id=user_id,
        )

    def add_bill(self, user_id, amount, bill_type):
        """添加账单"""
        bill_id = id_mgr.next_bill_id()
        bill = Bill(
            user_id=user_id,
            bill_id=bill_id,
            amount=amount,
            type=bill_type
        )
        db.session.add(bill)

    def change_money(self, user_id, amount, bill_type):
        """金钱的变更"""
        user = User.query.filter(User.key == user_id).first()
        if not user:
            raise ext.NotExistsError(u'用户不存在')
        if user.money + amount < 0:
            raise ext.NoMoneyError(None, abs(user.money + amount))
        modify = User.query.filter(User.key == user_id, User.money == user.money).update({
            User.money: user.money + amount
        })
        if not utils.check_modify(db, modify, self.e_log, u'【修改用户余额】并发操作，user_id:%s' % (user_id)):
            return False
        self.add_bill(user_id, amount, bill_type)
        user_cache.delete(user_id)
        return True

    def add_money(self, user_id, amount, bill_type):
        """增加金钱"""
        if amount <= 0:
            raise ext.MoneyError
        return self.change_money(user_id, amount, bill_type)

    def des_money(self, user_id, amount, bill_type):
        """减少金钱"""
        if amount >= 0:
            raise ext.MoneyError
        return self.change_money(user_id, amount, bill_type)
    def verify_wechat(self, openid, access_token):
        """验证微信登录"""
        url = 'https://api.weixin.qq.com/sns/auth?access_token=%s&openid=%s'%(access_token, openid)

        ret = requests.get(url, verify=False)
        if ret.status_code == 200:
            result = ret.json()
            errcode = result['errcode']

            if errcode == 0:
                return True
        return False

    def app_login(self, openid, access_token, nickname, img_url):
        """安卓或者ios端，登录"""
        # try:
        #     from four.wx_utils import get_detail_info_app
        #     ret=get_detail_info_app(access_token,openid)
        #     unionid=ret['unionid']
        # except:
        #     raise ext.OtherError(u'微信登录异常')

        unionid = openid
        # if not self.verify_wechat(openid, access_token):
        #     raise ext.OtherError(u'微信登录异常')
        return self.login_unionid(unionid, nickname, img_url)

    def wxa_login(self, code, nickname, img_url):
        """小程序登录"""
        from ktask.wx_utils import get_detail_info_wxa
        ret = get_detail_info_wxa(code)
        #ret=dict(openid=code,) #TODO
        if 'openid' not in ret:
            raise ext.OtherError(u'登陆失败')
        return self.login(ret['openid'], nickname, img_url)

user_mgr = UserMgr('UserMgr')

if __name__ == '__main__':
    pass

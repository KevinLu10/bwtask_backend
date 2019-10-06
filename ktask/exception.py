# -*- coding: utf-8 -*-


class Error(Exception):
    def __init__(self, message=None):
        if message:
            self.message = message


class ParamError(Error):
    """输入参数非法"""
    code = 10000
    message = u'输入参数非法'


class NotExistsError(Error):
    """查询的对象不存在"""
    code = 10001
    message = u'查询的对象不存在'


class PwdWrongError(Error):
    """查密码错误"""
    code = 10002
    message = u'密码错误'


class NotLoginError(Error):
    """没有登陆错误"""
    code = 10003
    message = u'没有登陆'


class OtherError(Error):
    """其他错误"""
    code = 10004
    message = u'未知错误'


class DbUpdateError(Error):
    """数据库更新错误"""
    code = 10005
    message = u'数据库更新错误'


class AssetError(Error):
    """资产数量错误"""
    code = 10006
    message = u'资产数量错误'


class UnknowObjTypeError(Error):
    """未知对象类型错误"""
    code = 10007
    message = u'未知对象类型错误'


class NotEnoughCouponError(Error):
    """消费券不够错误"""
    code = 10008
    message = u'消费券不足够'


class NotEnoughNumError(Error):
    """数量不够错误"""
    code = 10009
    message = u'商品数量不足够'

class OrderError(Error):
    """生成订单失败错误"""
    code = 10010
    message = u'生成订单失败'

class NotEnoughAssetError(Error):
    """资产数量不足够"""
    code = 10011
    message = u'消费券不足够'

class AddScheError(Error):
    """添加定时任务异常"""
    code = 10012
    message = u'添加定时任务异常'

class LoginError(Error):
    """登陆异常"""
    code = 10013
    message = u'登陆异常'
class MustLoginError(Error):
    """提示用户必须登陆"""
    code = 10014
    message = u'必须点击同意哦~'
class WXSignError(Error):
    """微信加密验证失败"""
    code = 10015
    message = u'微信加密验证失败~'
class RefundTooMoreError(Error):
    """退款金额过多"""
    code = 10016
    message = u'退款金额过多~'
class ExistsError(Error):
    """对象已存在"""
    code = 10017
    message = u'对象已存在'
class NoMoneyError(Error):
    """余额不足"""
    code = 10018
    message = u'余额不足'
    need_money = 0

    def __init__(self, msg, need_money):
        """
        
        :param msg: 
        :param need_money: 差多少钱
        """
        self.need_money = need_money
        Error.__init__(self, msg)

class InvalidClzError(Error):
    """不可用的行业分类"""
    code = 10019
    message = u'不可用的行业分类'
class InvalidCityError(Error):
    """不可用的城市分类"""
    code = 10020
    message = u'不可用的城市分类'
class CouponNotAuthError(Error):
    """没有权限使用该消费券"""
    code = 10021
    message = u'没有权限使用该消费券'
class PWDWrongError(Error):
    """密码错误"""
    code = 10022
    message = u'密码错误'


class MngNoAuthError(Error):
    """没有权限访问"""
    code = 10023
    message = u'没有权限访问'




class ExperationError(Error):
    """会话过期"""
    code = 10101
    message = u'会话过期'







# l=globals()
# print l
# kv=[]
# for key,c in l.items():
#
#     try:
#         kk=c()
#     except:
#         continue
#     # print kk,isinstance(kk,Error)
#     if isinstance(kk,Error):
#         try:
#             kv.append((kk.code,kk.message))
#             # kv[kk.code]=kk.message
#             # print kk.code,kk.message
#         except:
#             continue
# for k,v in sorted(kv,key=lambda k:k[0]):
#     print "| %s|   %s	| "%(k,v)
# def __main__():
#     l=globals()
#     print l

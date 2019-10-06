# -*- coding: utf-8 -*-

import random
from ktask.cache_data import id_container
import datetime
import time

class IdMgr(object):
    """ID管理者"""
    #BIZ_ID 用于v2版本的id
    BIZ_ID_ORDER='8'

    def __init__(self, name):
        self.name = name

    def get_serial_by_incr(self, number):
        a = random.randint(111111, 999999)
        b = random.randint(111111, 999999)
        s = "%s%s%s"%(a, number, b)
        _serial = int(s)
        return "%018d"%_serial

    def next_id(self,id_key):
        now = datetime.datetime.now()
        today = now.strftime("%Y%m%d")
        serial = id_container.incr('%s:%s'%(id_key,today))
        if serial <= 1:
            id_container.delete('%s:%s'%(id_key,(now + datetime.timedelta(days=-1)).strftime("%Y%m%d")))

        return "%s%s"%(now.strftime("%Y%m%d%H%M%S"), self.get_serial_by_incr(serial))

    def next_id_v2(self,biz_id):
        """版本2的id"""
        # user_id_k='{:0>6}'.format(user_id)[-4:]
        t_str="{:d}".format(int(time.time()*1000))[1:13]
        return '{}{}{:0>2}'.format(biz_id, t_str, random.randint(0, 99))

    def next_coupon_id(self):
        """获取下一个消费券ID"""
        return self.next_id("coupon_id")
    def next_asset_id(self):
        """获取下一个资产ID"""
        return self.next_id("asset_id")
    def next_asset_bill_id(self):
        """获取下一个资产流水ID"""
        return self.next_id("asset_bill_id")
    def next_order_id(self):
        """获取下一个orderID"""
        return self.next_id("order_id")
    def next_listed_id(self):
        """获取下一个挂牌ID"""
        return self.next_id("listed_id")
    def next_reach_listed_id(self):
        """获取下一个挂牌成交ID"""
        return self.next_id("reach_listed_id")
    def next_refund_id(self):
        """获取下一个退款ID"""
        return self.next_id("refund_id")
    def next_transfer_id(self):
        """获取下一个付款ID"""
        return self.next_id("transfer_id")

    def next_bill_id(self):
        """获取下一个账单ID"""
        return self.next_id("bill_id")

    def next_goods_order_id(self):
        """获取下一个商品账单ID"""
        return self.next_id_v2(self.BIZ_ID_ORDER)

id_mgr = IdMgr('serial_number_manager')


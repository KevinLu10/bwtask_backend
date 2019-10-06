# encoding=utf8
# -*- coding: utf-8 -*-
import hashlib
import uuid, time
from flask import g
import traceback
from ktask import db, e_log
from ktask.model import FormId
from datetime import datetime, timedelta
from ktask.biz.clz.user_clz import user_mgr
from ktask import utils
import requests
from ktask.biz.clz.wetchat_clz import wechat_mgr
from ktask.utils import json
import copy

class FormIdMgr(object):
    # 小程序的formid管理
    def __init__(self, name, **kwargs):
        self.name = name
        self.e_log = e_log

    def add_form_id(self, user_id, form_id):
        """新增form_id"""
        if len(form_id) < 1:
            return
        cache = user_mgr.get_cache(user_id)
        ddl = datetime.now() + timedelta(days=7)
        form_id = FormId(
            user_id=user_id,
            openid=cache['wxa_openid'],
            ddl=ddl,
            form_id=form_id
        )
        db.session.add(form_id)
        utils.commit_db(db, self.e_log, u'【新增form_id】入库失败')

    def get_form_id(self, user_id):
        """获取可用的form_id"""
        form_ids = FormId.query.filter(FormId.user_id == user_id, FormId.ddl > datetime.now(),
                                       FormId.status == FormId.STATUS_UNUSE).limit(10).all()
        return form_ids

    def request_tml_msg(self, data):
        """发送http请求给微信"""
        url = 'https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token=%s' % wechat_mgr.get_wxa_at()
        log_ret = ''
        try:
            # print 'Json', json.dumps(data)
            ret = requests.post(url, data=json.dumps(data))
            log_ret = ret.content
            ret_json = ret.json()
            errcode = int(ret_json['errcode'])
            # print 'errcode', errcode, type(errcode), log_ret
            if errcode == 0:
                return 1
            elif errcode in (41028, 41029):
                return -1
            else:
                raise Exception(u'访问微信服务器异常')
        except:
            self.e_log.error(traceback.format_exc())
            self.e_log.error(u'【发送模板消息】失败，url:%s data:%s,ret:%s' % (url, data, log_ret))

    def send_tml_msg_to_user(self, param):
        """向用户发送模板消息"""
        user_id, req_data = param
        req_data = copy.deepcopy(req_data)
        form_ids = self.get_form_id(user_id)

        for form_id in form_ids:
            req_data['touser'] = form_id.openid
            req_data['form_id'] = form_id.form_id
            ret = self.request_tml_msg(req_data)
            # print ret, 'RET', requests
            if ret == 1:
                form_id.status = FormId.STATUS_USE
                e_log.error(u'【向用户发送模板消息】成功，user_id:%s,req_data:%s' % (user_id, req_data))
                break
            elif ret == -1:
                form_id.status = FormId.STATUS_INVALID
        else:
            self.e_log.error(u'【向用户发送模板消息】用户没有可用的form_id，user_id:%s,req_data:%s' % (user_id, req_data))

        utils.commit_db(db, self.e_log, u'【发送通知关注人提醒通知】入库失败，user_id：%s' % (user_id))
        db.session.remove()

    def get_attend_req_data(self, task):
        """获取 通知关注人 模板消息的请求数据"""
        tmp_id = '6sNS2I2y_DRUUwtdfdE0cBZo2zMX1pRULfIf03XTFOQ'
        c = '#000000'
        data = dict(
            template_id=tmp_id,
            page='pages/task/task?task_id=%s&pwd=%s' % (task.id, task.pwd),
            data=dict(
                keyword1=dict(value=task.title, color=c),
                keyword2=dict(value=task.nickname, color=c),
                keyword3=dict(value=task.ddl.strftime('%Y-%m-%d %X'), color=c),

            )
        )
        return data

    def multi_thread(self, func, data):
        from multiprocessing.dummy import Pool as ThreadPool
        pool = ThreadPool(20)  # 线程池的大小，总并发数

        ret = pool.map(func, data)
        return ret

    def send_attend_msg(self, task, attends):
        """发送 通知关注人 提醒通知"""
        print 'task', task.id, 'attend', [attend.from_id for attend in attends]
        data = self.get_attend_req_data(task)
        data=[[attend.from_id, data] for attend in attends]
        self.multi_thread(self.send_tml_msg_to_user,data)
        # for attend in attends:
        #     self.send_tml_msg_to_user(attend.from_id, data)
        utils.commit_db(db, self.e_log, u'【发送通知关注人提醒通知】入库失败，task_id：%s' % (task.id))


form_id_mgr = FormIdMgr('FormIdMgr')

if __name__ == '__main__':
    pass

# encoding=utf8
# -*- coding: utf-8 -*-
from datetime import datetime

import requests
from sqlalchemy import func

from ktask import config
from ktask import db, utils, e_log
from ktask import exception as ext
from ktask.biz.clz.id_clz import id_mgr
from ktask.biz.clz.session_clz import session_mgr
from ktask.cache_data import user_cache, get_expire
from ktask.model import Task
from ktask.biz.clz.user_clz import user_mgr
from ktask.model import Attend
from ktask.biz.clz.user_clz import user_mgr


class AttendMgr(object):
    """关注"""

    def __init__(self, name, **kwargs):
        self.name = name
        self.e_log = e_log

    def get_attended(self, to_id):
        """获取关注我的所有用户"""
        attends = Attend.query.filter(Attend.to_id == to_id).all()
        return attends

    def get_attend(self, from_id):
        attends = Attend.query.filter(Attend.from_id == from_id).all()
        return attends

    def is_attend_exist(self, from_id, to_id):
        a = Attend.query.filter(Attend.from_id == from_id, Attend.to_id == to_id).first()
        return 1 if a else 0

    def add_attend(self, user_id, to_id):
        """关注"""
        cache = user_mgr.get_cache(to_id)
        if self.is_attend_exist(user_id, to_id):
            raise ext.OtherError(U'您已关注TA')
        a = Attend(from_id=user_id, to_id=to_id)
        db.session.add(a)
        utils.commit_db(db, e_log, u'【关注】user_id:%s' % user_id)
        return dict()

attend_mgr = AttendMgr('AttendMgr')

if __name__ == '__main__':
    pass

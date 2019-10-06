# encoding=utf8
# -*- coding: utf-8 -*-
import uuid, time
from ktask import config
from datetime import datetime, timedelta
from flask import abort, request
from ktask.cache_data import sessions


class SessionMgr(object):
    # 该类负责session_id的增，删，查找等操作
    def __init__(self, name, **kwargs):
        # 初始化
        self.name = name
        self.expire_time = 60 * 60 * 24 * 1

    def get_new_id(self):
        """创建新的sessionID"""
        return uuid.uuid4().get_hex()

    def set_new_session(self, user_id):
        session_id = self.get_new_id()
        sessions.set(session_id, user_id)
        sessions.expire(session_id, self.expire_time)
        return dict(
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.now().strftime('%Y-%m-%d %X')
        )

    def check_session(self, app_session):
        """检查session是否有效，如果有效，返回用户的ID"""
        user_id = sessions.get(app_session)
        return user_id

    def delete_session(self, session_id):
        sessions.delete(session_id)
    def get_user_id(self,app_session):
        user_id = sessions.get(app_session)
        return user_id

session_mgr = SessionMgr('SessionMaker')

if __name__ == '__main__':
    pass

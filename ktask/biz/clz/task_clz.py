# encoding=utf8
# -*- coding: utf-8 -*-

import requests
from sqlalchemy import func
from datetime import datetime, timedelta
from ktask import config
from ktask import db, utils, e_log
from ktask import exception as ext
from ktask.biz.clz.session_clz import session_mgr
from ktask.cache_data import user_cache, get_expire
from ktask.model import Task, TaskList, Read, Reply, Attend
from ktask.biz.clz.user_clz import user_mgr
from ktask.biz.clz.attend_clz import attend_mgr
from ktask.biz.clz.img_clz import img_mgr


class TaskMgr(object):
    # 用户管理类
    def __init__(self, name, **kwargs):
        self.name = name
        self.e_log = e_log

    def get_db_task(self, task_id, pwd):
        task = Task.query.filter(Task.id == task_id, Task.pwd == pwd).first()
        if not task:
            raise ext.NotExistsError(u'任务不存在')
        if task.status != Task.STATUS_ON:
            raise ext.NotExistsError(u'任务已被删除')
        return task

    def get_reads(self, task_id):
        reads = Read.query.filter(Read.task_id == task_id).all()
        return reads

    def get_replys(self, task_id):
        replys = Reply.query.filter(Reply.task_id == task_id, Reply.status == Reply.STATUS_ON).all()
        return replys

    def get_task_dict(self, task):
        return dict(
            title=task.title,
            content=task.content,
            c_type=task.c_type,
            type=task.type,
            c_img_url=img_mgr.get_url(task.img_uri),
            audio_uri=img_mgr.get_url(task.audio_uri),
            nickname=task.nickname,
            img_url=task.img_url,
            pwd=task.pwd,
            user_id=task.user_id,
            task_type_str=Task.TYPE_MAP.get(task.type, u'未知'),
            ddl=task.ddl.strftime('%m月%d日%H时')
        )

    def get_read_dict(self, read):
        return dict(
            user_id=read.user_id,
            img_url=read.img_url,
            nickname=read.nickname
        )

    def get_reply_dict(self, reply):
        return dict(
            user_id=reply.user_id,
            content=reply.content,
            c_type=reply.c_type,
            img_uri=img_mgr.get_url(reply.img_uri),
            audio_uri=img_mgr.get_url(reply.audio_uri),
            nickname=reply.nickname,
            img_url=reply.img_url,
            reply_id=reply.id
        )

    def has_user_reply(self, task_id, user_id):
        r = Reply.query.filter(Reply.task_id == task_id, Reply.user_id == user_id,
                               Reply.status == Reply.STATUS_ON).first()
        return 1 if r else 0

    def get_task_reply_type(self, task, user_id):
        if task.type != Task.TYPE_REPLY:
            return Reply.REPLY_TYPE_NOT_NEED
        else:
            if self.has_user_reply(task.id, user_id):
                return Reply.REPLY_TYPE_REPLY
            else:
                return Reply.REPLY_TYPE_UNREPLY

    def get_task(self, task_id, user_id, pwd):
        """获取任务"""
        task = self.get_db_task(task_id, pwd)
        reads = self.get_reads(task_id)
        replys = self.get_replys(task_id) if task.type == Task.TYPE_REPLY else []
        task_ret = self.get_task_dict(task)
        task_ret['read'] = [self.get_read_dict(read) for read in reads]  # *20
        task_ret['replys'] = [self.get_reply_dict(reply) for reply in replys]  # *20
        task_ret['reply_type'] = self.get_task_reply_type(task, user_id)
        task_ret['reply_type_str'] = Reply.REPLY_TYPE_MAP.get(task_ret['reply_type'], u'未知')
        task_ret['is_attend'] = attend_mgr.is_attend_exist(user_id, task.user_id)
        return task_ret

    def check_content(self, c_type, content, img_uri, audio_uri):
        if c_type == Task.C_TYPE_IMG and img_uri == '':
            raise ext.ParamError(U'图片URI不能为空')
        if c_type == Task.C_TYPE_AUDIO and audio_uri == '':
            raise ext.ParamError(U'音频片URI不能为空')
        if c_type not in Task.ALL_C_TYPE:
            raise ext.ParamError(U'c_type错误')
            # if c_type==Task.C_TYPE_IMG and img_uri=='':
            #     raise ext.ParamError(U'图片URI不能为空')

    def get_ddl(self, ddl_type):
        if ddl_type == 0:
            ddl = datetime.now() + timedelta(1)
        elif ddl_type == 1:
            ddl = datetime.now() + timedelta(7)
        elif ddl_type == 2:
            ddl = datetime.now() + timedelta(30)
        else:
            raise ext.ParamError(u'未知的超时时间')
        return ddl

    def init_task(self, user_id, type_, title, c_type, content, img_uri, audio_uri, user_info, ddl):
        ddl = self.get_ddl(ddl)
        task = Task(
            user_id=user_id,
            title=title,
            c_type=c_type,
            content=content,
            img_uri=img_uri,
            audio_uri=audio_uri,
            type=type_,
            ddl=ddl,
            nickname=user_info['nickname'],
            img_url=user_info['img_url'],
            pwd=utils.rand_str(8)
        )
        db.session.add(task)
        db.session.flush()
        return task

    def init_task_list(self, task, user_id):
        tl = TaskList(
            user_id=user_id,
            task_id=task.id,
            title=task.title,
            task_type=task.type,
            pwd=task.pwd,
            img_url=task.img_url,
            nickname=task.nickname,
            is_read=0
        )
        db.session.add(tl)
        return tl

    def add_task_list(self, task, user_id):
        attends = attend_mgr.get_attended(user_id)
        tls = [self.init_task_list(task, a.from_id) for a in attends]
        from ktask.biz.clz.form_id_clz import form_id_mgr
        form_id_mgr.send_attend_msg(task, attends)
        return tls

    def add_task(self, user_id, type_, title, c_type, content, img_uri, audio_uri, ddl):
        """发布任务"""
        self.check_content(c_type, content, img_uri, audio_uri)
        user_info = user_mgr.get_cache(user_id)
        task = self.init_task(user_id, type_, title, c_type, content, img_uri, audio_uri, user_info, ddl)
        tls = self.add_task_list(task, user_id)
        utils.commit_db(db, e_log, u'【发布任务】user_id:%s' % user_id)
        return dict(task_id=task.id, pwd=task.pwd)

    def read(self, user_id, task_id, pwd):
        """已读"""
        task = self.get_db_task(task_id, pwd)
        if user_id == task.user_id:
            return dict()
            raise ext.OtherError(u'本人不能已读')
        user_info = user_mgr.get_cache(user_id)
        r = Read.query.filter(Read.user_id == user_id, Read.task_id == task_id).first()
        if r:
            return dict()
        r = Read(user_id=user_id, task_id=task_id, img_url=user_info['img_url'], nickname=user_info['nickname'])
        db.session.add(r)
        utils.commit_db(db, e_log, u'【已读】user_id：%s' % user_id)
        return dict(read_suc=1)

    def reply(self, user_id, c_type, content, img_uri, audio_uri, task_id, pwd):
        """回复"""
        self.check_content(c_type, content, img_uri, audio_uri)
        task = self.get_db_task(task_id, pwd)
        if datetime.now() > task.ddl:
            raise ext.ParamError(u'任务已过期')
        # if user_id == task.user_id:
        #     raise ext.OtherError(u'本人不能操作')
        if task.type != Task.TYPE_REPLY:
            raise ext.OtherError(U'不允许接龙')
        r = Reply.query.filter(Reply.user_id == user_id, Reply.task_id == task_id,
                               Reply.status == Reply.STATUS_ON).first()
        if r:
            raise ext.OtherError(u'您已经接龙了')
        user_cache = user_mgr.get_cache(user_id)
        r = Reply(
            user_id=user_id,
            c_type=c_type,
            content=content,
            img_uri=img_uri,
            audio_uri=audio_uri,
            task_id=task_id,
            img_url=user_cache['img_url'],
            nickname=user_cache['nickname']
        )
        db.session.add(r)
        utils.commit_db(db, e_log, u'【回复】user_id：%s' % user_id)
        return dict()

    def get_task_list_dict(self, task_list):
        return dict(
            pwd=task_list.pwd,
            task_id=task_list.task_id,
            img_url=task_list.img_url,
            title=task_list.title,
            is_read=task_list.is_read,
            nickname=task_list.nickname,
            task_type_str=Task.TYPE_MAP.get(task_list.task_type, u'未知')
        )

    def get_task_list(self, user_id):
        tasklists = TaskList.query.filter(TaskList.user_id == user_id).limit(100).all()
        return dict(data=[self.get_task_list_dict(t) for t in tasklists])

    def get_my_attend_task(self, user_id):
        tasks = db.session.query(Task).filter(Attend.from_id == user_id, Attend.to_id == Task.user_id,
                                              Attend.status == 1, Task.ddl > datetime.now(),
                                              Task.status == Task.STATUS_ON).order_by(
            Task.id.desc()).limit(1000).all()
        return tasks

    def get_my_add_task(self, user_id):
        """获取我发布的任务"""
        return Task.query.filter(Task.user_id == user_id, Task.ddl > datetime.now(),
                                 Task.status == Task.STATUS_ON).order_by(Task.id.desc()).limit(
            1000).all()

    def get_my_reply_task(self, user_id):
        tasks = db.session.query(Task).filter(Task.id == Reply.task_id, Reply.user_id == user_id,
                                              Task.status == Task.STATUS_ON, Reply.status == Reply.STATUS_ON).order_by(
            Task.id.desc()).limit(1000).all()
        return tasks

    def get_sin_task_dict(self, task):
        return dict(
            img_url=task.img_url,
            task_id=task.id,
            nickname=task.nickname,
            pwd=task.pwd,
            title=task.title,
            task_type_str=Task.TYPE_MAP.get(task.type, u'未知')

        )

    def get_my_task_index(self, user_id):
        return dict(
            attend=[self.get_sin_task_dict(task) for task in self.get_my_attend_task(user_id)],
            add=[self.get_sin_task_dict(task) for task in self.get_my_add_task(user_id)],
            reply=[self.get_sin_task_dict(task) for task in self.get_my_reply_task(user_id)],
        )

    def del_task(self, user_id, task_id, pwd):
        """删除任务"""
        task = self.get_db_task(task_id, pwd)
        if task.user_id != user_id:
            raise ext.ParamError(u'没有权限')
        if task.ddl < datetime.now():
            raise ext.ParamError(u'过期任务不能删除')
        task.status = Task.STATUS_DEL
        utils.commit_db(db, e_log, u'【删除任务】task_id：%s' % task_id)
        return dict()

    def del_reply(self, user_id, task_id, pwd, reply_id):
        """删除接龙"""
        task = self.get_db_task(task_id, pwd)
        if task.ddl < datetime.now():
            raise ext.ParamError(u'过期任务不能删除')
        reply = Reply.query.filter(Reply.id == reply_id).first()
        if not reply:
            raise ext.NotExistsError(u'接龙不存在')
        if reply.status != reply.STATUS_ON:
            raise ext.NotExistsError(U'接龙已删除')
        if task.id != reply.task_id:
            raise ext.NotExistsError(u'id异常')
        if reply.user_id != user_id:
            raise ext.ParamError(u'没有权限')
        reply.status = Reply.STATUS_DEL
        utils.commit_db(db, e_log, u'【删除任务】task_id：%s' % task_id)
        return dict()


task_mgr = TaskMgr('TaskMgr')

if __name__ == '__main__':
    pass

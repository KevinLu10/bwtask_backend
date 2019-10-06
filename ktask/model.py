# encoding=utf8
from ktask import db
from sqlalchemy import func, Index, func, UniqueConstraint
from decimal import Decimal, ROUND_UP, ROUND_HALF_EVEN
from datetime import datetime


class User(db.Model):
    """用户表"""
    __tablename__ = "user"
    # username password nickname atd_num praise_num
    id = db.Column(db.Integer, primary_key=True)  # 主键
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())
    last_login = db.Column(db.TIMESTAMP, nullable=False)  # 最后登录时间
    wxa_openid = db.Column(db.Unicode(32), nullable=False, default='')  # 微信小程序的openid
    nickname = db.Column(db.Unicode(32))  # 用户昵称
    img_url = db.Column(db.TEXT())  # 用户头像的url
    __table_args__ = (
        Index('User_wxa_openid', wxa_openid),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
        },
    )


class Task(db.Model):
    """任务表"""
    __tablename__ = "task"
    C_TYPE_TXT = 0  # 文本内容
    C_TYPE_IMG = 1  # 图片内容
    C_TYPE_AUDIO = 2  # 音频内容
    ALL_C_TYPE=[C_TYPE_TXT,C_TYPE_IMG,C_TYPE_AUDIO]
    TYPE_WORK = 0  # 作业
    TYPE_NOTICE = 1  # 通知
    TYPE_REPLY = 2  # 接龙
    ALL_TYPE=[TYPE_WORK,TYPE_NOTICE,TYPE_REPLY]
    TYPE_MAP={
        TYPE_WORK:u'作业',
        TYPE_NOTICE:u'通知',
        TYPE_REPLY:u'接龙',
    }
    # statsu
    STATUS_ON = 1
    STATUS_DEL = 0
    id = db.Column(db.Integer, primary_key=True)  # 主键
    user_id = db.Column(db.Integer, nullable=False)  # 发布人ID
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())  # 最后登录时间
    ddl = db.Column(db.TIMESTAMP, nullable=False,)  # 过期时间
    type = db.Column(db.SmallInteger, nullable=False, default=C_TYPE_TXT)  # 任务类型
    title = db.Column(db.Unicode(32))  # 标题
    content = db.Column(db.Unicode(32), nullable=False, default='')  # 文本内容
    c_type = db.Column(db.SmallInteger, nullable=False, default=C_TYPE_TXT)  # 内容
    img_uri = db.Column(db.Unicode(255), nullable=False, default='')  # 图片内容
    audio_uri = db.Column(db.Unicode(255), nullable=False, default='')  # 音频内容
    img_url = db.Column(db.TEXT())  # 用户头像
    nickname = db.Column(db.Unicode(32))  # 用户昵称
    pwd = db.Column(db.Unicode(32))  # 密码
    status = db.Column(db.SmallInteger, nullable=False, default=1)  # 状态
    __table_args__ = (
        # Index('Teamate_project_id', project_id),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
        },
    )


class Read(db.Model):
    """已读表"""
    __tablename__ = "readed"

    id = db.Column(db.Integer, primary_key=True)  # 主键
    task_id = db.Column(db.Integer, nullable=False)  #
    user_id = db.Column(db.Integer, nullable=False)  #
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())  # 最后登录时间
    img_url = db.Column(db.TEXT())  # 用户头像
    nickname = db.Column(db.Unicode(32))  # 用户昵称

    status = db.Column(db.SmallInteger, nullable=False, default=1)  # 状态
    __table_args__ = (
        # Index('Teamate_project_id', project_id),
        UniqueConstraint(task_id, user_id),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
        },
    )


class Reply(db.Model):
    """回复表"""
    __tablename__ = "reply"
    REPLY_TYPE_NOT_NEED=0#不需要回复
    REPLY_TYPE_UNREPLY=1#未回复
    REPLY_TYPE_REPLY=2#已回复
    REPLY_TYPE_MAP={
        REPLY_TYPE_NOT_NEED:u'',
        REPLY_TYPE_UNREPLY:u'参与',
        REPLY_TYPE_REPLY:u'已参与',
    }
    C_TYPE_TXT = 0  # 文本内容
    C_TYPE_IMG = 1  # 图片内容
    C_TYPE_AUDIO = 2  # 音频内容
    # statsu
    STATUS_ON = 1
    STATUS_DEL = 0
    id = db.Column(db.Integer, primary_key=True)  # 主键
    task_id = db.Column(db.Integer, nullable=False)  #
    user_id = db.Column(db.Integer, nullable=False)  #
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())  # 最后登录时间
    content = db.Column(db.Unicode(32), nullable=False, default='')  # 文本内容
    c_type = db.Column(db.SmallInteger, nullable=False, default=C_TYPE_TXT)  # 内容
    img_uri = db.Column(db.Unicode(255), nullable=False, default='')  # 图片内容
    audio_uri = db.Column(db.Unicode(255), nullable=False, default='')  # 音频内容

    img_url = db.Column(db.TEXT())  # 用户头像
    nickname = db.Column(db.Unicode(32))  # 用户昵称

    status = db.Column(db.SmallInteger, nullable=False, default=1)  # 状态
    __table_args__ = (
        # Index('Teamate_project_id', project_id),
        UniqueConstraint(task_id, user_id),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
        },
    )


class Attend(db.Model):
    """关注表"""
    __tablename__ = "attend"

    id = db.Column(db.Integer, primary_key=True)  # 主键
    from_id = db.Column(db.Integer, nullable=False)  # 关注人
    to_id = db.Column(db.Integer, nullable=False)  # 被关注人
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())  # 最后登录时间

    status = db.Column(db.SmallInteger, nullable=False, default=1)  # 状态
    __table_args__ = (
        Index('Attend_from_id', from_id),
        Index('Attend_to_id', to_id),
        UniqueConstraint(from_id, to_id),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
        },
    )


class TaskList(db.Model):
    """任务列表"""
    __tablename__ = "task_list"

    id = db.Column(db.Integer, primary_key=True)  # 主键
    user_id = db.Column(db.Integer, nullable=False)  # 关注人
    task_id = db.Column(db.Integer, nullable=False)  # 被关注人
    task_type = db.Column(db.SmallInteger, nullable=False)  # 任务类型
    is_read = db.Column(db.SmallInteger, nullable=False)  # 已读
    title = db.Column(db.Unicode(32))  # 标题
    pwd = db.Column(db.Unicode(32))  # 密码
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())  # 最后登录时间
    img_url = db.Column(db.TEXT())  # 用户头像
    nickname = db.Column(db.Unicode(32))  # 用户昵称

    status = db.Column(db.SmallInteger, nullable=False, default=1)  # 状态
    __table_args__ = (
        Index('TaskList_user_id_created_at', user_id, created_at),
        Index('TaskList_user_id_task_id', user_id, task_id),
        UniqueConstraint(user_id, created_at),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
        },
    )


class FormId(db.Model):
    __tablename__ = 'form_id'
    """
    微信小程序的form_id
    """
    STATUS_UNUSE = 1  # 未使用
    STATUS_USE = 0  # 已使用
    STATUS_INVALID = 2  # 不可用
    key = db.Column(db.BigInteger, autoincrement=True, primary_key=True)  # 用户ID
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=func.now())  # 创建时间
    user_id = db.Column(db.BigInteger, nullable=False)  # 用户ID
    openid = db.Column(db.String(255), nullable=False)  # 用户的open_id
    form_id = db.Column(db.String(255), nullable=False)  # 用户的form_id
    ddl = db.Column(db.TIMESTAMP, nullable=False, )  # 超时时间

    status = db.Column(db.SmallInteger, nullable=False, default=STATUS_UNUSE)  # 状态
    __table_args__ = (
        Index("FormId_user_id_ddl", user_id, ddl),
        {
            'mysql_engine': 'InnoDB',
            'mysql_charset': 'utf8',
        },
    )


if __name__ == '__main__':
    pass

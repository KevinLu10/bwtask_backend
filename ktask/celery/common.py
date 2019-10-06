# -*- coding: utf-8 -*-

from ktask.celery import celery


@celery.task(name='task.test')
def test(arg):
    """测试"""

    return arg

@celery.task(name='task.buy_project_send_tmp_msg')
def buy_project_send_tmp_msg(user_id, group_id, red_pk_id, cur_price, amount,gorder_id):
    """发送模板消息"""
    from ktask.biz.clz.form_id_clz import form_id_mgr
    ret = form_id_mgr.buy_project_send_tmp_msg(user_id, group_id, red_pk_id, cur_price, amount, gorder_id)
    return ret

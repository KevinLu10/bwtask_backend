# encoding=utf-8
__author__ = 'kevinlu1010@qq.com'
import requests
import json
import hashlib

"""调试后端接口"""

HOST = "http://www.ktask_test.com"
# HOST = "http://api.ktask.cn"
# HOST = "http://www.ktask_test.com/fourtest-bxYwsE7o"

COOKIES = dict(session="")  # 10001


# COOKIES=dict(session='de9b10d9013c462e81ca6f8651745ef6')#10007
# HOST="http://114.215.91.203:9097" #sche的
def get_url(uri):
    return "%s%s" % (HOST, uri)


def request(method, uri, data):
    url = get_url(uri)
    cookies = dict(session_id="8b5fe2c997874bbe9c57d96900f3277a")
    if method == "GET":
        # print 'data,',data
        result = requests.get(url, params=data, cookies=COOKIES)
    elif method == "POST":
        result = requests.post(url, data=data, cookies=COOKIES)
    print method, url, result.status_code
    print result.headers
    if result.status_code == 200:
        # print result.content
        return result.json()
    else:
        try:
            return result.json()
        except:
            print '转换JSON失败'
            print result.content


def get(uri, data):
    return request("GET", uri, data)


def post(uri, data):
    return request("POST", uri, data)


def p(d):
    print json.dumps(d, ensure_ascii=False, indent=4)


def get_user_index():
    data = {

    }
    print get('four/v1/user/index', data)


def get_asset_list():
    data = dict(
        # user_id=10001,
        type=3,
        page_index=0,
        page_size=1

    )
    p(get('four/v1/asset/list', data))


def add_task():
    """发任务"""
    data = dict(
        title="852375683762108",
        c_type="2",
        type="1",
        content="1",
        img_uri="aaa.png",
        audio_uri="bbb.png",
        ddl=2,
    )
    p(post('/ktask/v1/task', data))


def user_wxa_login():
    """"""
    id = 2
    data = dict(
        # code="openid4", #3
        # code="852375683762109", #2
        # code="the code is a mock one", #2
        code="openid%s" % id,  # 2
        nickname="nickname%s" % id,
        img_url="https://ktask.oss-cn-beijing.aliyuncs.com/%s.jpg" % id,
    )
    p(post('/ktask/v1/user/wxa/login', data))


def add_attend():
    """"""
    data = dict(
        to_id="2",

    )
    p(post('/ktask/v1/attend', data))


def get_task():
    """获取任务"""
    data = dict(
        task_id="12",
        pwd="UgqPt7x6",

    )
    p(get('/ktask/v1/task', data))


def add_read():
    """已读"""
    data = dict(
        task_id="12",
        pwd="UgqPt7x6",

    )
    p(post('/ktask/v1/read', data))


def add_reply():
    """已读"""
    data = dict(
        task_id="12",
        pwd="UgqPt7x6",
        c_type="2",
        content="content1",
        img_uri="img_uri11",
        audio_uri="audio_uri11",

    )
    p(post('/ktask/v1/reply', data))


def get_task_list():
    """获取任务列表"""
    data = dict(
    )
    p(get('/ktask/v1/tasklist', data))


def add_form_id():
    """提交form_id"""
    data = dict(
        form_id='aaaa'
    )
    p(post('/ktask/v1/formid/add', data))


def get_my_task_index():
    """获取我的列表"""
    data = dict(
    )
    p(get('/ktask/v1/task/my_index', data))


def add_form_idtest():
    """"""
    data = dict(
    )
    p(post('/ktask/v1/formid/test', data))


def del_task():
    """删除任务"""
    data = dict(
        task_id='13',
        pwd='NpzJu0AV'
    )
    p(post('/ktask/v1/task/del', data))


def del_reply():
    """删除接龙"""
    data = dict(
        task_id='12',
        pwd='UgqPt7x6',
        reply_id='5'
    )
    p(post('/ktask/v1/reply/del', data))


if __name__ == '__main__':
    pass
    # COOKIES['session']='97d38bcefb5344288aa328e2c0c45700' #2
    # COOKIES['session']='97d38bcefb5344288aa328e2c0c45700'
    # COOKIES['session']='08486c9ffa62434887de53ca7a0fd491' #3
    COOKIES['session']='session2' #4
    # add_task()
    # add_form_id()
    # get_task()
    # add_read()
    # add_reply()
    # add_attend()
    get_my_task_index()
    # user_wxa_login()
    # add_form_idtest()
    # del_task()
    # del_reply()
    # get_task_list()

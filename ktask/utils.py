# encoding=utf8
import os
import sys
import time
import traceback
from datetime import datetime
from functools import wraps
from signal import SIGTERM

import flask

try:
    import ujson as json
except:
    from flask import json
import logging
import random, string
from flask import request, make_response
from decimal import Decimal
import xlrd
from ktask import exception as ext
from ktask import config
a_log = logging.getLogger('access')
e_log = logging.getLogger('error')


def allot_logger(name, filename, level=None, format=None):
    '''
    初始化一个logger
    :param name: logger名称
    :param filename: 日志文件路径
    :param format: 日志格式
    :param level: 日志的严重程度
    :return:
    '''
    if level == None:
        level = logging.DEBUG
    if format == None:
        format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s'
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
    handler = logging.FileHandler(filename)
    handler.setFormatter(
        logging.Formatter(format))
    logger.handlers = [handler]


def logmsg(f):
    """记录被装饰函数的访问信息
    :param f:
    :return:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        input_str = json.dumps(args or kwargs)
        args_htr = json.dumps(request.args) if request.args else ''
        form_htr = json.dumps(request.form) if request.form else ''
        ip = request.environ.get('HTTP_X_FORWARDED_FOR')
        form_htr=form_htr[0:1000]
        msg = "%s %s (%s) (%s) (%s) (%s)" % (ip, f.__name__, input_str, request.data, args_htr, form_htr)
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            user_id = flask.g.get('user_id', None)
            # output_str = json.dumps(result.data)
            output_str = json.dumps(getattr(result, 'data', ''))
            msg = "%.2f %s %s %s" % (time.time() - start_time, user_id, msg, output_str)
            a_log.info(msg)
            return result
        except:
            user_id = flask.g.get('user_id', None)
            e_log = logging.getLogger('error')
            msg = "%.2f %s %s" % (time.time() - start_time, user_id, msg)
            e_log.error(msg)
            e_log.error(traceback.format_exc())
            a_log.error(msg)
            a_log.error(traceback.format_exc())
            raise

    return wrapper


def html_logmsg(f):
    """记录返回html页面的接口
    :param f:
    :return:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        args_htr = json.dumps(request.args) if request.args else ''
        ip = request.environ.get('HTTP_X_FORWARDED_FOR')
        path = request.path
        msg = "%s %s %s (%s) (%s)" % (ip, f.__name__, path, request.data, args_htr)
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            status_code = getattr(result, 'status_code', '')
            msg = "%.2f %s %s" % (time.time() - start_time, msg, status_code)
            a_log.info(msg)
            return result
        except:
            e_log = logging.getLogger('error')
            msg = "%.2f %s" % (time.time() - start_time, msg)
            e_log.error(msg)
            e_log.error(traceback.format_exc())
            a_log.error(msg)
            a_log.error(traceback.format_exc())
            raise

    return wrapper


def login(f):
    """记录被装饰函数的访问信息
    :param f:
    :return:
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
        # TODO 写登陆的逻辑

    return wrapper


class ResposeData(object):
    code = 0
    data = None

    def __init__(self, code=0, data=None, success=None):
        self.code = 0
        if success is not None:
            self.data = {'result': success and 'success' or 'fail'}
        else:
            self.data = data


def return_error(error):
    resp = {
        'name': '',
        'code': error.code,
        'msg': error.message,
        'data': '',
    }
    if config.HTML_DEBUG:
        resp['track']=traceback.format_exc()
    if isinstance(error, ext.NoMoneyError):
        resp['need_money'] = error.need_money
    http_status_code = 400
    resp_ = make_response(json.dumps(resp, ensure_ascii=False), http_status_code)
    return resp_


def check_response(f):
    """对程序处理的结果进行包裹处理"""

    @wraps(f)
    def _wrapper(*args, **kwargs):
        try:
            # 需要根据http请求的method类型来输出不同的http状态码
            http_status_code = 200
            result = f(*args, **kwargs)
            if isinstance(result, bool):
                if result is False:
                    http_status_code = 500
                ret = ResposeData(success=result)
            else:
                ret = ResposeData(data=result)
            resp_ = make_response(json.dumps(ret, ensure_ascii=False), http_status_code)


        except ext.Error, e:
            resp_ = return_error(e)
        # resp_.headers['Content-Type']='Content-Type: application/json; encoding=utf-8'
        return resp_

    return _wrapper


def get_param(key, default=None, type=None):
    """通用版的获取请求参数"""
    if request.method == 'GET':
        return request.args.get(key, default, type)
    else:
        return json_get(key, default, type)


def get_header_session():
    """获取请求头的session"""
    return request.headers.get('SESSION')


def must_login(f):
    """检验用户是否登录"""

    @wraps(f)
    def _wrapper(*args, **kwargs):
        from ktask import config
        from ktask.biz.clz.session_clz import session_mgr
        from flask import g
        # if config.HTML_DEBUG:
        #     return f(*args, **kwargs)
        session = request.cookies.get('session') or get_header_session()
        if session:
            user_id = session_mgr.check_session(session)
            if user_id:  # 如果用户已登录
                g.user_id = user_id
                return f(*args, **kwargs)
        return return_error(ext.NotLoginError)

    return _wrapper


def mng_must_login(f):
    """管理后台检验用户是否登录"""

    @wraps(f)
    def _wrapper(*args, **kwargs):
        # if config.HTML_DEBUG:
        #     from flask import g
        #     g.mng_user_id = 1
        #     return  f(*args, **kwargs)
        session_id = request.cookies.get('session_id')
        if not session_id:
            return return_error(ext.NotLoginError)
        from ktask.manage.bak.clz import mng_session_mgr
        user_id = mng_session_mgr.check_session(session_id)
        if not user_id:
            return return_error(ext.NotLoginError)
        from flask import g
        g.mng_user_id = user_id
        return f(*args, **kwargs)

    return _wrapper


def get_cur_user():
    """获取当前登录的user_id"""
    from ktask.biz.clz.session_clz import session_mgr
    user_id = None
    session = request.headers.get('X-Session-ID', None)
    if session:
        user_id = session_mgr.get_user_id(session)
    return user_id if user_id else None


def get_cur_manager_user():
    """获取当前登录的管理用户的user_id"""
    from flask import g
    return int(g.mng_user_id)



def json_get(key, default=None, type=None, is_raise=0, must=0,obj=None):
    """
    由于request.json.get方法不像request.args.get方法，可以支持type参数，所以用这个方法来实现json.get的type参数
    :param key: 参数名称
    :param type: 类型，如 int float unicode
    如果转换成功，返回转换后的值，否则抛出ParamError异常
    """
    json = obj or request.json or dict()
    try:
        rv = json[key]
        if type is not None:
            rv = type(rv)
    except KeyError:
        rv = default

    except (ValueError, TypeError) as e:
        if default is not None:
            rv = default
        else:
            if is_raise:
                raise ext.ParamError(u'参数%s必须是%s类型' % (key, str(type)))
            else:
                rv = default
    if must and rv is None:
        raise ext.ParamError(U'invalid %s' % key)
    return rv


def args_get(key, default=None, type=None, is_raise=0, must=0):
    return json_get(key, default, type, is_raise, must, request.args)


def form_get(key, default=None, type=None, is_raise=0, must=0):
    return json_get(key, default, type, is_raise, must, request.form)


def rand_str(num):
    return ''.join(random.sample(string.ascii_letters + string.digits, num))


def commit_db(db, error_logger, log_msg_if_fail,is_raise=1):
    """写入数据库，返回成功或失败"""
    try:
        db.session.commit()
        return True
    except:
        import traceback
        error_logger.error(traceback.format_exc())
        error_logger.error(log_msg_if_fail)
        db.session.rollback()
        if is_raise:
            raise ext.OtherError(u'服务器开小差（002）')
        return False


def check_modify(db, modify, error_logger, log_msg_if_fail):
    """检查数据库是否更新成功"""
    if not modify:
        error_logger.error(log_msg_if_fail)
        db.session.rollback()
        return False
    return True


def deamonize(stdout='/dev/null', stderr=None, stdin='/dev/null',
              pidfile=None, startmsg='started with pid %s'):
    '''
        This forks the current process into a daemon.
        The stdin, stdout, and stderr arguments are file names that
        will be opened and be used to replace the standard file descriptors
        in sys.stdin, sys.stdout, and sys.stderr.
        These arguments are optional and default to /dev/null.
        Note that stderr is opened unbuffered, so
        if it shares a file with stdout then interleaved output
        may not appear in the order that you expect.
    '''
    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0: sys.exit(0)  # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0: sys.exit(0)  # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)

    # Open file descriptors and print start message
    if not stderr: stderr = stdout
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    pid = str(os.getpid())
    sys.stderr.write("\n%s\n" % startmsg % pid)
    sys.stderr.flush()
    if pidfile: file(pidfile, 'w+').write("%s\n" % pid)

    # Redirect standard file descriptors.
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def startstop(stdout='/dev/null', stderr=None, stdin='/dev/null',
              pidfile='pid.txt', startmsg='started with pid %s'):
    if len(sys.argv) > 1:
        action = sys.argv[1]
        try:
            pf = file(pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        if 'stop' == action or 'restart' == action:
            if not pid:
                mess = "Could not stop, pid file '%s' missing.\n"
                sys.stderr.write(mess % pidfile)
                sys.exit(1)
            try:
                while 1:
                    os.kill(pid, SIGTERM)
                    time.sleep(1)
            except OSError, err:
                err = str(err)
                if err.find("No such process") > 0:
                    os.remove(pidfile)
                    if 'stop' == action:
                        sys.exit(0)
                    action = 'start'
                    pid = None
                else:
                    print str(err)
                    sys.exit(1)
        if 'start' == action:
            if pid:
                mess = "Start aborded since pid file '%s' exists.\n"
                sys.stderr.write(mess % pidfile)
                sys.exit(1)
            deamonize(stdout, stderr, stdin, pidfile, startmsg)
            return
    print "usage: %s start|stop|restart" % sys.argv[0]
    sys.exit(2)


def dt2str(dt):
    return dt.strftime("%Y-%m-%d")


def str2dt(dt):
    return datetime.strptime(string, '%Y-%m-%d')


def dt2strm(dt):
    return dt.strftime("%Y-%m-%d %X")


def strm2dt(string):
    try:
        return datetime.strptime(string, '%Y-%m-%d %X')
    except:
        return None


def get_ip():
    ip = request.environ.get('HTTP_X_FORWARDED_FOR')
    if ',' in ip:
        ip = ip.split(',')[0]
    return ip


def decimal_round(d):
    """四舍五入decimal类型为两位小数"""
    return d.quantize(Decimal(".00"))


def safe_str2datetime(dt_str, format='%Y-%m-%d'):
    """转换字符串到datetime格式，安全版"""
    if dt_str:
        try:
            dt = datetime.strptime(dt_str, format)
        except:
            raise ext.ParamError(u'日起不符合格式%s' % format)
    else:
        dt = None
    return dt


class Addr():
    """收货地址数据类"""

    def __init__(self, name, contact, prov, city, street, detail):
        self.name = name,
        self.contact = contact,
        self.prov = prov,
        self.city = city,
        self.street = street,
        self.detail = detail,


def get_addr(f=None):
    """获取地址类"""
    f = form_get if f is None else f
    addr_name = f("addr_name", type=str)
    if addr_name is None:
        return None
    addr_contact = f("addr_contact", type=str, must=1)
    addr_prov = f("addr_prov", type=str, must=1)
    addr_city = f("addr_city", type=str, must=1)
    addr_street = f("addr_street", type=str, must=1)
    addr_detail = f("addr_detail", type=str, must=1)
    return Addr(addr_name, addr_contact, addr_prov, addr_city, addr_street, addr_detail)


def time_print(msg):
    print datetime.now().strftime("%Y-%m-%d %X"), msg


def get_records(data):
    """批量发货，获取xls文件的发货记录"""
    def _get_value(value):
        if isinstance(value, float):
            return str(int(value))
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, basestring):
            # return value
            return value.encode('utf8')

    f = xlrd.open_workbook(file_contents=data)
    table = f.sheets()[0]

    records = []
    for row in range(1, 101):
        if not table.cell(row, 1).value:
            return records
        record = []
        for col in range(1, 4):
            record.append(_get_value(table.cell(row, col).value))
        records.append(record)
    return records



if __name__ == '__main__':
    pass

# encoding=utf8
import logging

LOGGER_LEVEL = logging.DEBUG
LOGGERS = [
    ("common", '/data/logs/ktask_common.log', LOGGER_LEVEL, None),
    ("access", '/data/logs/ktask_access.log', LOGGER_LEVEL, None),
    ("error", '/data/logs/ktask_error.log', LOGGER_LEVEL, None),
    ("pay", '/data/logs/ktask_pay.log', LOGGER_LEVEL, None),
    ("listed_log", '/data/logs/ktask_listed.log', LOGGER_LEVEL, None),
    ("sche", '/data/logs/ktask_sche.log', LOGGER_LEVEL, None),
]
#本地服务的域名 ,不要斜杠结尾,
LOCAL_HOST="http://www.ktask_test.com"
LOCAL_IP='10.1.91.203'
#程序文件的跟路径，config的地址是LOCAL_ROOT/ktask/config.py
LOCAL_ROOT='/data/ktask/'
# REDIS配置
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PASSWORD = 'ktask.ktask'
REDIS_DB = 3


#每页的数量
PAGE_SIZE=20

HTML_DEBUG = True   # html debug
# HTML_DEBUG = False  # html debug
# DEBUG = True
DEBUG = False
SQLALCHEMY_ECHO = False

#MYSQL
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ktask_test:ktaskpwd@127.0.0.1:3306/ktask_test?charset=utf8'
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_POOL_SIZE = 5



#####che服务器配置

# SCHEDULER_URL = 'http://127.0.0.1:9095'
EXPLAIN_TEMPLATE_LOADING=False

##############微信API相关###############################
APPID="XXXXXXXX"
SECRET="XXXXXXXX"
##############微信支付###############################
# APPID='000001'
WEIXIN_MEDIA_URL = 'http://file.api.weixin.qq.com/cgi-bin/media/get'
WEIXIN_PREPAY = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
WEIXIN_MCH_ID = 'XXXXXXXX'
#接收微信支付成功通知
WEIXIN_NOTIFY_URL = 'http://weixin.ttsharing.com/ktask/v1/order/wechat/notify'
WEIXIN_PAY_KEY = 'XXXXXXXX'
WEIXIN_BODY = 'XXXXXXXX'
WEIXIN_DEBUG=True
WEIXIN_OP_USER_ID="XXXXXXXX"
WEIXIN_REFUND_URL="https://api.mch.weixin.qq.com/secapi/pay/refund" #退款URL
WEIXIN_CERT_FILE="%scert/apiclient_cert.pem"%LOCAL_ROOT
WEIXIN_CERT_KEY_FILE="%scert/apiclient_key.pem"%LOCAL_ROOT
WEIXIN_TRANSFERS_URL="https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers"
##############################微信支付###############################
##############################微信其他###############################\
WEIXIN_ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'
JS_API_TICKET_URL = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket'

##############################微信其他###############################


##############################微信小程序###############################
WEIXIN_WXA_APPID='XXXXXXXX'
WEIXIN_WXA_SECRET='XXXXXXXX'
##############################微信小程序###############################

##############################七牛图片上传###############################
QINIU_DOMAIN = 'XXXXXXXX.clouddn.com'
QINIU_ACCESS_KEY='XXXXXXXX'
QINIU_SECRET_KEY='XXXXXXXX'
QINIU_BUCKET_NAME = 'ktask'
QINIU_BASE_URL = 'http://ogiqbjmw0.bkt.clouddn.com/'  #七牛的url
##############################七牛图片上传###############################


#最大显示的消费券的二维码数量
MAX_SHOW_COUPOU=4

#普通账号的初始密码
FIRST_PWD='XXXXXXXX'
COMMON_ACCOUNT_AUTH=["project","bill","listed","coupon"]


####wxa_order
#快递信息接口
EXPRESS_KEY='XXXXXXXX'
EXPRESS_BUSINESS_ID=10000
EXPRESS_EXPRESS_TYPE=10000


#阿里
ALI_APPID = 'XXXXXXXX'
ALI_SCRE = 'XXXXXXXX'
ALI_FILE_URL = 'https://ktask.oss-cn-beijing.aliyuncs.com/'

if __name__ == '__main__':
    pass

# encoding=utf8
# -*- coding: utf-8 -*-
import hashlib
from ktask import e_log, config
import os
from qiniu import Auth
from qiniu import put_file,put_data
import oss2
from ktask import exception as ext
class ImgMgr(object):
    # 图片管理类
    def __init__(self, name, **kwargs):
        self.name = name
        self.e_log = e_log

    def get_url(self, db_img_uri):
        """用户资产变更"""
        if db_img_uri:
            return u"%s%s" % (config.ALI_FILE_URL, db_img_uri)
        else:
            return u""
            return u"https://www.baidu.com/img/bd_logo1.png"

    def get_file_name(self, file_path):
        """获取文件的md5"""
        with open(file_path, 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()[8:-8]
            suffix = os.path.splitext(file_path)[1]
            key = '%s%s' % (md5, suffix)
            return key
    def get_file_name_online(self, data,suffix):
        """获取文件的md5"""
        md5 = hashlib.md5(data).hexdigest()
        key = '%s.%s' % (md5, suffix)
        return key

    def upload_file(self, file_path):
        '''
        上传文件到七牛
        :param file_path:本地服务器的文件路径
        :return: 上传后的uri
        '''
        if not os.path.exists(file_path):
            self.e_log.error(u'【上传文件】文件不存在，file_path:%s', file_path)
            return None
        access_key = config.QINIU_ACCESS_KEY
        secret_key = config.QINIU_SECRET_KEY
        q = Auth(access_key, secret_key)
        bucket_name = config.QINIU_BUCKET_NAME  # 空间名
        key = self.get_file_name(file_path)
        mime_type = "image/jpeg"
        token = q.upload_token(bucket_name, key)
        put_file(token, key, file_path, mime_type=mime_type, check_crc=True)
        return key

    def upload_file_online(self, mime_type,data,suffix):
        '''
        上传文件到七牛
        :param file_path:本地服务器的文件路径
        :return: 上传后的uri
        '''
        access_key = config.QINIU_ACCESS_KEY
        secret_key = config.QINIU_SECRET_KEY
        q = Auth(access_key, secret_key)
        bucket_name = config.QINIU_BUCKET_NAME  # 空间名
        key = self.get_file_name_online(data,suffix)
        mime_type = mime_type
        token = q.upload_token(bucket_name, key)
        put_data(token, key, data, mime_type=mime_type, check_crc=True)
        return key

    def upload_file_online1(self, mime_type, data, suffix):

        # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
        auth = oss2.Auth(config.ALI_APPID, config.ALI_SCRE)
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        bucket = oss2.Bucket(auth, 'http://oss-cn-beijing.aliyuncs.com', 'ktask')
        key = self.get_file_name_online(data, suffix)
        result = bucket.put_object(key, data)
        if result.status == 200:
            return key
        else:
            raise ext.OtherError(u'上传错误')

img_mgr = ImgMgr('ImgMgr')

if __name__ == '__main__':
    pass

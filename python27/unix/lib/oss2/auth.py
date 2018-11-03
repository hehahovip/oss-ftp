# -*- coding: utf-8 -*-

import hmac
import hashlib
import time
import logging

from . import utils
from .compat import urlquote, to_bytes, to_unicode
from urllib import quote

class Auth(object):
    """用于保存用户AccessKeyId、AccessKeySecret，以及计算签名的对象。"""

    _subresource_key_set = frozenset(
        ['response-content-type', 'response-content-language',
         'response-cache-control', 'logging', 'response-content-encoding',
         'acl', 'uploadId', 'uploads', 'partNumber', 'group', 'link',
         'delete', 'website', 'location', 'objectInfo',
         'response-expires', 'response-content-disposition', 'cors', 'lifecycle',
          'restore', 'qos', 'referer', 'append', 'position']
    )

    def __init__(self, access_key_id, access_key_secret):
        self.id = access_key_id.strip()
        self.secret = access_key_secret.strip()

    def _sign_request(self, req, bucket_name, key):
        req.headers['date'] = utils.http_date()

        signature = self.__make_signature(req, bucket_name, key)
        req.headers['authorization'] = "AWS {0}:{1}".format(self.id, signature)
        logging.info("req authorization: %s" % (req.headers['authorization']))

    def _sign_url(self, req, bucket_name, key, expires):
        expiration_time = int(time.time()) + expires

        req.headers['date'] = str(expiration_time)
        signature = self.__make_signature(req, bucket_name, key)

        req.params['OSSAccessKeyId'] = self.id
        req.params['Expires'] = str(expiration_time)
        req.params['Signature'] = signature


        logging.info("req params: %s" %(vars(req.params)))

        return req.url + '?' + '&'.join(_param_to_quoted_query(k, v) for k, v in req.params.items())

    def __make_signature(self, req, bucket_name, key):
        logging.info("req key: %s" %(key))

        string_to_sign = self.__get_string_to_sign(req, bucket_name, key)

        logging.debug('string_to_sign={0}'.format(string_to_sign))

        h = hmac.new(to_bytes(self.secret), to_bytes(string_to_sign), hashlib.sha1)
        return utils.b64encode_as_string(h.digest())

    def __get_string_to_sign(self, req, bucket_name, key):
        logging.info("req_string_sign key: %s" %(key))
        # logging.info("bucket_name: %s" %(unicode(bucket_name, 'utf-8')))
        # logging.info("key: %s" %(unicode(key, 'utf-8')))
        resource_string = self.__get_resource_string(req, bucket_name, key)
        headers_string = self.__get_headers_string(req)
        # resource_string = self.__get_resource_string(req, bucket_name, key)
        # headers_string = self.__get_headers_string(req)

        content_md5 = req.headers.get('content-md5', '')
        content_type = req.headers.get('content-type', '')
        date = req.headers.get('date', '')

        logging.info("req headers: %s" %(vars(req.headers)))

        return '\n'.join([req.method,
                          content_md5,
                          content_type,
                          date,
                          headers_string + resource_string])

    def __get_headers_string(self, req):
        headers = req.headers
        canon_headers = []
        for k, v in headers.items():
            lower_key = k.lower()
            if lower_key.startswith('x-oss-'):
                canon_headers.append((lower_key, v))

        canon_headers.sort(key=lambda x: x[0])

        if canon_headers:
            return '\n'.join(k + ':' + v for k, v in canon_headers) + '\n'
        else:
            return ''

    def __get_resource_string(self, req, bucket_name, key):
        if not bucket_name:
            return '/'
        else:
            bucket_name = urlquote(bucket_name)
            key = urlquote(key)
            return '/{0}/{1}{2}'.format(bucket_name, key, self.__get_subresource_string(req.params))

    def __get_subresource_string(self, params):
        if not params:
            return ''

        subresource_params = []
        for key, value in params.items():
            if key in self._subresource_key_set:
                subresource_params.append((key, value))

        subresource_params.sort(key=lambda e: e[0])

        if subresource_params:
            return '?' + '&'.join(self.__param_to_query(k, v) for k, v in subresource_params)
        else:
            return ''

    def __param_to_query(self, k, v):
        if v:
            return k + '=' + v
        else:
            return k


class AnonymousAuth(object):
    """用于匿名访问。

    .. note::
        匿名用户只能读取public-read的Bucket，或只能读取、写入public-read-write的Bucket。
        不能进行Service、Bucket相关的操作，也不能罗列文件等。
    """
    def _sign_request(self, req, bucket_name, key):
        pass

    def _sign_url(self, req, bucket_name, key, expires):
        return req.url + '?' + '&'.join(_param_to_quoted_query(k, v) for k, v in req.params.items())


def _param_to_quoted_query(k, v):
    if v:
        return urlquote(k, '') + '=' + urlquote(v, '')
    else:
        return urlquote(k, '')


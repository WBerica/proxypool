import time

import cfg
from common.utils import to_str
import base64
import json


class ProxyQueueHandle(object):

    def push(self, val):
        pass


class Proxy(object):

    _name = 'unknow'
    _ratio = 100
    _request_max_num = 0

    _queue_handle = None
    _server_request_timeout = 0

    def __init__(self, queue_handle, ratio=100, request_timeout=0):
        self._queue_handle = queue_handle
        self._ratio = ratio
        self._server_request_timeout = request_timeout
        self._last_request_time = None

    @property
    def name(self):
        return self._name

    @property
    def ratio(self):
        return self._ratio

    @property
    def request_max_num(self):
        """
        每次请求可以获取最大数量
        :return:  数量
        """
        return self._request_max_num

    @classmethod
    def create(cls, queue_handle, ratio, request_timeout=2):
        """
        创建本类
        :param queue_handle:  ProxyQueueHandle的对象
        :return: 本类对象
        """
        if not isinstance(queue_handle, ProxyQueueHandle):
            raise ValueError("queue_handle is Not ProxyQueueHandle!")
        return cls(queue_handle, ratio, request_timeout)

    def get(self, num):
        """
        获取IP
        :param num: 需要获取IP数量
        :return:    添加到队列数量
        """
        pass

    def _push(self, host, port, protocol='http',time_out = None, user=None, pwsd=None):
        if protocol not in ['http', 'https']:
            protocol = 'http'
        if not time_out:
            time_out = cfg.PROXY_MAX_TIMEOUT
        proxy = "%(protocol)s://%(host)s:%(port)s" % {
                "protocol": protocol,
                "host": host,
                "port": port,
            }
        data = {
            'proxy': proxy,
            'proxy_name': self.name,
            'time_out':time_out
        }
        if user and pwsd:
            proxy_user_pass = user + ":" + pwsd
            data['Proxy-Authorization'] = 'Basic ' + to_str(base64.b64encode(proxy_user_pass.encode('utf8')))
        self._queue_handle.push(json.dumps(data, ensure_ascii=False))






from .proxy import Proxy
from common import log
from requests.adapters import HTTPAdapter
import time
import requests
import traceback


PROXY_REQUEST_MAX_NUM = 200
PROXY_TIMEOUT = 5
PROXY_TID = ''    # 订单号
PROXY_SERVER_INTERVAL_TIME = 1


class Daxiangdaili(Proxy):

    _request_url = ''

    _last_request_server_time = None
    _request_server_interval_time = PROXY_SERVER_INTERVAL_TIME

    def __init__(self, queue_handle, ratio, request_timeout):
        super(Daxiangdaili, self).__init__(queue_handle, ratio, request_timeout)
        self._name = 'daxiangdaili.com'
        self._request_max_num = PROXY_REQUEST_MAX_NUM
        self._request_url = 'http://tpv.daxiangdaili.com/ip/'
        self._last_request_server_time = None
        self._request_server_interval_time = PROXY_SERVER_INTERVAL_TIME

    def _get_proxy_server(self, num):
        url = "%(url)s?tid=%(tid)s&num=%(num)s&delay=%(delay)s&filter=on&category=2" % {
            'url': self._request_url,
            'tid': PROXY_TID,
            'num': num,
            'delay': PROXY_TIMEOUT
        }
        return url

    def _get_proxys_from_server(self, num):
        proxy_pool_server1 = self._get_proxy_server(num)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        }
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        try:
            r = s.get(proxy_pool_server1, headers=headers, timeout=self._server_request_timeout)
            if r.status_code == 200:
                proxys = r.text
                if 'ERROR' in proxys:
                    log.error("_get_proxys_from_server (%s): fail to get proxy list(%s)" % (self.name, r.text))
                    return None
                return proxys.split('\n')
            else:
                log.error("_get_proxys_from_server (%s): fail to get proxy list(%d)" % (self.name, r.status_code))
                return None
        except Exception as e:
            log.error("_get_proxys_from_server error: " + str(e))
            log.error("_get_proxys_from_server traceback:" + traceback.format_exc())
            return None

    def get(self, num):
        if num <= 0:
            return 0
        proxys = None
        cur_time = time.time()
        if self._last_request_server_time is None:
            proxys = self._get_proxys_from_server(num)
            self._last_request_server_time = cur_time
        elif (self._last_request_server_time + self._request_server_interval_time) < cur_time:
            proxys = self._get_proxys_from_server(num)
            self._last_request_server_time = cur_time
        if proxys:
            result = len(proxys)
            for proxy in proxys:
                proxy = proxy.strip(' \r\n\t')
                ip, port = proxy.split(':')
                ip = ip.strip(' \r\n\t')
                port = port.strip(' \r\n\t')

                self._push(ip, port)
        else:
            result = 0
        return result


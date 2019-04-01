import importlib
import json
import random
import sys
import time
import os

import datetime
import traceback

import six
from bintrees import BinaryTree

import cfg
from common import log, redis_pool
from common.utils import to_str
from proxy.proxy import Proxy, ProxyQueueHandle


class RedisProxyQueue(ProxyQueueHandle):

    def __init__(self, key):
        self.key = key

    def push(self, val):
        r = redis_pool.get_redis()
        r.lpush(self.key, val)

    def len(self):
        r = redis_pool.get_redis()
        return r.llen(self.key)

    def clear(self):
        r = redis_pool.get_redis()
        r.delete(self.key)

    # def pop(self, timeout=0):
    #     r = redis_pool.get_redis()
    #     if timeout > 0:
    #         data = r.brpop(self.key, timeout)
    #         if isinstance(data, tuple):
    #             data = data[1]
    #     else:
    #         data = r.rpop(self.key)
    #     if data:
    #         data = to_str(data, redis_pool.get_redis_encoding())
    #         return json.loads(data)
    #     else:
    #         return None
    def pop(self, timeout=0):
        r = redis_pool.get_redis()
        if timeout > 0:
            data = r.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = r.rpop(self.key)
        if data:
            data = to_str(data, redis_pool.get_redis_encoding())
            data = json.loads(data)
            time_out = data.get('time_out','')
            if time_out:
                if time_out >int(time.time()-10):
                    return data
                else:
                    self.pop()
            else:
                return data


        else:
            return None


class AppProxy(object):
    def __init__(self, queue_key=None):
        self.proxys = BinaryTree()
        self.proxy_queue_handle = None

        #  self.proxy_queue_key =  "scrapy:ip_proxy_queue"
        self.proxy_queue_key = queue_key
        # 代理IP 池的长度
        self.proxy_queue_min_lenght = cfg.PROXY_MIN_QUEUE_LENGHT
        # 代理最多每次增加数量
        self.proxy_increment_num = 20
        self.sleep_time = 0.2

    def _create_proxy(self, proxycls, ratio):
        if not isinstance(ratio, int):
            ratio = int(ratio)
        if isinstance(proxycls, Proxy):
            obj = proxycls.create(self.proxy_queue_handle, ratio, cfg.PROXY_SERVER_REQUEST_TIMEOUT)
        elif isinstance(proxycls, six.string_types):
            obj = AppProxy.load_object(proxycls).create(self.proxy_queue_handle, ratio, cfg.PROXY_SERVER_REQUEST_TIMEOUT)
        else:
            raise ValueError("Not a valid value(%s)" % str(proxycls))

        last_val = ratio

        if self.proxys.count > 0:
            last_val = self.proxys.max_item()[0] + last_val
        self.proxys.insert(last_val, obj)

    def _get_proxy(self, need_num):
        # 根据需求数，调用不同的类的get方法，往代理池中增加相应数量的ip数量

        max_weight = self.proxys.max_item()[0]
        random_weight = random.randint(1, max_weight)
        proxy = self.proxys.ceiling_item(random_weight)[1]
        num = int(min(proxy.request_max_num, need_num))
        result = 0
        if num > 0:
            result = proxy.get(num)
        log.debug("_on_proxy: (%s)ratio=%d|request_max_num=%d|result=%d" % (proxy.name, proxy.ratio,
                                                                            proxy.request_max_num, result))
        return result

    def _on_procrssed(self):
        # 判断代理ip池中的长度
        llen = self.proxy_queue_handle.len()
        # 和最小ip池数量做对比，求出差值，
        need_num = cfg.PROXY_MIN_QUEUE_LENGHT - llen
        result = 0
        if need_num > 0:
            need_num = min(need_num, self.proxy_increment_num)
            result = self._get_proxy(need_num)
        log.debug("_on_procrssed -->: llen=%d|need_num=%d|result=%d" % (llen, need_num, result))

    @staticmethod
    def load_object(path):
        """
        Load an object given its absolute object path, and return it.
        :param path: ie, 'proxy.proxy.Proxy'
        :return:
        """
        try:
            dot = path.rindex('.')
        except ValueError:
            raise ValueError("Error loading object '%s': not a full path" % path)

        module, name = path[:dot], path[dot + 1:]
        mod = importlib.import_module(module)

        try:
            obj = getattr(mod, name)
        except AttributeError:
            raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

        return obj

    def start_proxys(self, redis_cfg, proxy_class):

        redis_pool.init_redis(redis_cfg)

        self.proxy_queue_handle = RedisProxyQueue(self.proxy_queue_key)
        self.proxy_queue_handle.clear()
        for proxycls in proxy_class:
            # 返回一个不同代理IP供应商类的实例
            self._create_proxy(proxycls, proxy_class[proxycls])
            log.info("start_proxy: %s --> %d" % (str(proxycls), proxy_class[proxycls]))

    def run(self):
        log.info('###############################################')
        log.info('Now begin.......')
        while 1:
            try:
                self._on_procrssed()
                time.sleep(self.sleep_time)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                log.error('run error:', str(e))
                log.error("run traceback:" + traceback.format_exc())


def start_app(environ='dev', area='all'):
    # 日志配置内容
    # log_path = os.path.join(cfg.LOG_DIR,
    #                         ("%s.%s.%s.log" % (cfg.APP_NAME, area, datetime.datetime.now().strftime("%Y%m%d"))))
    # print("BASE_DIR:", cfg.BASE_DIR)
    # print("log's path:", log_path)
    # log.init_logger(log_path, cfg.LOG_FILE_MAX_BYTES, cfg.LOG_FILE_BACKUP_COUNT)

    # 根据启动的时候传递过来的area调用不同站点适用的ip池
    # queue_key = "scrapy:ip_proxy_queue"

    queue_key = cfg.PROXY_QUEUE_KEY[area]
    #  调用配置的不同的IP供应商的类
    #  proxy_class=  {
    #     'proxy.duoip.Duoip': 20,
    #     'proxy.wandouip.Wandouip': 15,
    #     'proxy.daxiangdaili.Daxiangdaili': 25,
    #     'proxy.baibian2.BaiBian': 30,
    #     'proxy.a2u_proxy.A2uProxy': 5,
    #     'proxy.spyme_proxy.SpyMeProxy': 5,
    # }
    proxy_class = cfg.PROXY_OPERATION_CLASS[area]
    # 调用不同的redis数据库
    #  redis_cfg =  {'host': '127.0.0.1','port': 16379,}
    redis_cfg = cfg.PROXY_REDIS_CFG[environ]
    print("queue_key: ", queue_key)
    print("proxy_class: ", proxy_class)
    print("redis_cfg: ", redis_cfg)

    # 初始化代理ip类
    app = AppProxy(queue_key)

    app.start_proxys(redis_cfg, proxy_class)
    app.run()


if __name__ == '__main__':
    print("Begin.....")
    if len(sys.argv) == 1:
        start_app()
    elif len(sys.argv) >= 3:
        environ = sys.argv[1]
        area = sys.argv[2]
        start_app(environ, area)

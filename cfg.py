import os

import sys

import datetime
import time

def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path

    elif os.path.isfile(path):
        return os.path.dirname(path)


BASE_DIR = cur_file_dir()

LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

APP_NAME = os.path.basename(sys.argv[0])

# ############################

# LOG 相关配置

LOG_FILE = APP_NAME + datetime.datetime.now().strftime(".%Y%m%d") + ".log"
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)
LOG_FILE_MAX_BYTES = 1024 * 1024 * 100
LOG_FILE_BACKUP_COUNT = 5

# 配置读取代理ip的key
PROXY_QUEUE_KEY = {
    'all': 'scrapy:ip_proxy_queue',
}
# 配置不同商家的IP所用的类以及权重
# operation class
PROXY_OPERATION_CLASS = {
    'all': {
        'proxy.daxiangdaili.Daxiangdaili': 100,
    },
}
# redis的配置
PROXY_REDIS_CFG = {
    'dev': {
        'host': '127.0.0.1',
        'port': 6379,
    },
    'test': {
        'host': '127.0.0.1',
        'port': 6379,
    },
    'rel': {
        'host': '127.0.0.1',
        'port': 6379,
    }
}

# 代理IP池的长度
PROXY_MIN_QUEUE_LENGHT = 200

# 超时时间  s
PROXY_SERVER_REQUEST_TIMEOUT = 2

PROXY_MAX_TIMEOUT = int(time.time())+180

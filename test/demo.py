import json
import time
import requests
from app_proxy import RedisProxyQueue
from cfg import PROXY_QUEUE_KEY, PROXY_REDIS_CFG
from common import redis_pool

key = PROXY_QUEUE_KEY['all']
proxy_redis_cfg = PROXY_REDIS_CFG['dev']
redis_pool.init_redis(proxy_redis_cfg)

# 目标网站
url = 'https://www.amazon.co.uk'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
}

while 1:
    time.sleep(2)
    json_dict = RedisProxyQueue(key=key).pop(timeout=5)
    if json_dict:
        proxy_authorization = json_dict.get("Proxy-Authorization")
        proxy = json_dict.get("proxy")
        proxy_name = json_dict.get("proxy_name", "unknown")
        time_out = json_dict.get("time_out", "unknown")
        proxies = {"http": proxy}
        print('proxy:', proxy)
        print('proxy_name:', proxy_name)
        print('time_out:', time_out)
        response =requests.get(url, headers=headers, proxies=proxy)
        if response.status_code == 200:
            print("响应成功")
            data = {
                'proxy': proxy,
                'proxy_name': proxy_name,
                'time_out': time_out
            }
            data = json.dumps(data)
            RedisProxyQueue(key=key).push(data)


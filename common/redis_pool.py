import redis
import copy
from .global_value import gol


REDIS_DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
    'encoding': 'utf-8',
    'socket_timeout': 30,
    'socket_connect_timeout': 10,
    'max_connections': 100,
    'socket_keepalive': False,
    'socket_keepalive_options': False,
    'retry_on_timeout': False
}


def init_redis(cfg):
    redis_cfg = copy.copy(REDIS_DEFAULT_CONFIG)
    for key in redis_cfg:
        if key in cfg:
            redis_cfg[key] = cfg[key]

    # redis_pool = redis.ConnectionPool(host=redis_cfg['host'],
    #                                 port=redis_cfg['port'],
    #                                 db=redis_cfg['db'],
    #                                 password=redis_cfg['password'],
    #                                 encoding=redis_cfg['encoding'],
    #                                 socket_timeout=redis_cfg['socket_timeout'],
    #                                 socket_connect_timeout=redis_cfg['socket_connect_timeout'],
    #                                 socket_keepalive=redis_cfg['socket_keepalive'],
    #                                 socket_keepalive_options=redis_cfg['socket_keepalive_options'],
    #                                 retry_on_timeout=redis_cfg['retry_on_timeout'],
    #                                 max_connections=redis_cfg['max_connections'])
    redis_pool = redis.ConnectionPool(**redis_cfg)
    gol.set_value('redis', redis_pool)


def get_redis(name='redis'):
    redis_pool = gol.get_value(name)
    if redis_pool is None:
        raise ValueError("_global_dict not have redis's handle!")
    return redis.Redis(connection_pool=redis_pool)


def get_redis_encoding(name='redis'):
    redis_pool = gol.get_value(name)
    if redis_pool is None:
        raise ValueError("_global_dict not have redis's handle!")
    return redis_pool.connection_kwargs.get('encoding')



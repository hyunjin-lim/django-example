import redis
from setting.settings import (REDIS_HOST, REDIS_PORT, REDIS_DB)
from setting.exceptions import RedisError

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def is_redis_available(r):
    try:
        r.ping()
    except (redis.exceptions.ConnectionError):
        raise RedisError()
    return True


if is_redis_available(r):
    print("radis connected!")

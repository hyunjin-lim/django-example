import redis
from rest_framework import exceptions
from setting.settings import (REDIS_HOST, REDIS_PORT, REDIS_DB)
from setting.exceptions import RedisError

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
except redis.RedisError:
    raise RedisError()
from rest_framework.exceptions import APIException


class RedisError(APIException):
    status_code = 500
    default_detail = "redis server error"
    default_code = "redis server error"

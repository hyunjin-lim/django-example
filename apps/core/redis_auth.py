import jwt
from django.conf import settings
from apps.users.models import User

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
import time
from setting.redis_connect import r
from setting.settings import (
    AUTH_TOKEN,
)


class RedisAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = '{}:{}'.format(AUTH_TOKEN, key)
            if not r.exists(token):
                return None

            id = r.hget(token, 'id')
            if not id:
                return None

            user = User.objects.get(id=id)
            print('----redis confirm----')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (user, token)
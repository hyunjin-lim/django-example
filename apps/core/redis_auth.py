import jwt
from django.conf import settings
from apps.users.models import User

from rest_framework import exceptions, authentication
import time
from setting.redis_connect import r
from setting.settings import (
    AUTH_TOKEN,
)
from rest_framework.authentication import TokenAuthentication


class RedisAuthentication(TokenAuthentication):
    keyword = 'Bearer'

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

# class RedisAuthentication(authentication.BaseAuthentication):
#     authentication_header_prefix = 'Bearer'
#
#     def authenticate(self, key):
#         auth_header = authentication.get_authorization_header(key).split()
#         auth_header_prefix = self.authentication_header_prefix.lower()
#
#         prefix = auth_header[0].decode('utf-8')
#         key = auth_header[1].decode('utf-8')
#
#         if prefix.lower() != auth_header_prefix:
#             return None
#
#         try:
#             token = '{}:{}'.format(AUTH_TOKEN, key)
#             if not r.exists(token):
#                 return None
#
#             id = r.hget(token, 'id')
#             if not id:
#                 return None
#
#             user = User.objects.get(id=id)
#             print('----redis confirm----')
#         except User.DoesNotExist:
#             raise exceptions.AuthenticationFailed('Invalid token')
#
#         return (user, token)
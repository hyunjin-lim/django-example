import jwt

from django.conf import settings
from apps.users.models import User

from rest_framework import authentication, exceptions
from rest_framework.authentication import TokenAuthentication
import time


class JSONWebTokenAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Bearer'

    def authenticate(self, key):
        auth_header = authentication.get_authorization_header(key).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            expire = payload.get('exp')

            if int(time.time()) > expire:
                raise exceptions.AuthenticationFailed('Token has expired')

            id = payload.get('id')
            if not id:
                raise exceptions.AuthenticationFailed('Invalid token')

            user = User.objects.get(id=payload['id'])
            print('----jwt confirm----')

        except (jwt.DecodeError, User.DoesNotExist):
            raise exceptions.AuthenticationFailed('Invalid token')

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted')

        return (user, payload)
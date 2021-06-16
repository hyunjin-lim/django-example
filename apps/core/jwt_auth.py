import jwt

from django.conf import settings
from apps.users.models import User

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
import time


class JSONWebTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            payload = jwt.decode(key, settings.SECRET_KEY, algorithms="HS256")
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
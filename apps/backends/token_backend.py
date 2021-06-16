from apps.users.models import User
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from setting.settings import (
    O_AUTH_TOKEN,
)

#
# class TokenBackend(BaseBackend):
#     """
#     1. 토큰 확인
#     2. 토큰에 해당하는 유저 확인
#     3. 유저 리턴
#     """
#     def authenticate(self, request, token=None):
#         if token is None:
#             return None
#         // 토큰 모델 생성 및 확인하는 로직으로 변경
#         try:
#             user = User.objects.get(**kwargs)
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             # user = User(username=username)
#             # user.is_staff = True
#             # user.is_superuser = True
#             # user.save()
#             return None
#
#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None
from apps.users.models import User
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
import requests
"""
외부 서버 계정이 있는 경우
"""


def check_if_user(user_id, user_pw):
    payload = {
        'user_id': str(user_id),
        'user_pw': str(user_pw)
    }
    with requests.Session() as s:
        s.post('https://community-dummy.com/login', data=payload)
        auth = s.get('https://community-dummy.com/login_requited_page')
        if auth.status_code == 200: # 성공적으로 가져올 때
            return True
        else: # 로그인이 실패시
            return False


class OAuthBackend(BaseBackend):
    def authenticate(self, username=None, password=None):
        if check_if_user(username, password):  # OO커뮤니티 사이트 인증에 성공한 경우
            try:  # 유저가 있는 경우
                user = User.objects.get(username=username)
            except User.DoesNotExist:  # 유저 정보가 없지만 인증 통과시 user 생성
                user = User(username=username)
                user.is_staff = False
                user.is_superuser = False
                user.save()
                # 여기서는 user.password를 저장하는 의미가 없음.(장고가 관리 못함)
            return user
        else:  # OO 커뮤니티 사이트 인증에 실패한 경우, Django기본 User로 감안해 password검증
            try:
                user = User.objects.get(username=username)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except:
                return None

    def user_can_authenticate(self, user):
        is_active = getattr(user, 'is_active', None)  # 유저가 활성화 되었는지
        return is_active or is_active is None  # 유저가 없는 경우 is_active는 None이므로 True

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)  # 유저를 pk로 가져온다
        except User.DoesNotExist:
            return None
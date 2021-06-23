from apps.users.models import User
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
import requests
import msal
from setting.settings import (
    AZURE_ENDPOINT,
    AZURE_CLIENT_ID,
    AZURE_AUTHORITY
)
import json


def check_if_user(user_id, user_pw):
    scope = ["User.Read"]
    app = msal.PublicClientApplication(
        AZURE_CLIENT_ID, authority=AZURE_AUTHORITY,
        # token_cache=...  # Default cache is in memory only.
        # You can learn how to use SerializableTokenCache from
        # https://msal-python.rtfd.io/en/latest/#msal.SerializableTokenCache
    )
    # The pattern to acquire a token looks like this.
    result = None
    # Firstly, check the cache to see if this end user has signed in before
    accounts = app.get_accounts()
    if accounts:
        # logging.info("Account(s) exists in cache, probably with token too. Let's try.")
        result = app.acquire_token_silent(scope, account=accounts[0])
    if not result:
        # logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
        # See this page for constraints of Username Password Flow.
        # https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication
        result = app.acquire_token_by_username_password(
            user_id, user_pw, scopes=scope)
    if "access_token" in result:
        # Calling graph using the access token
        graph_data = requests.get(  # Use token to call downstream service
            AZURE_ENDPOINT,
            headers={'Authorization': 'Bearer ' + result['access_token']}, ).json()
        print("Graph API call result: %s" % json.dumps(graph_data, indent=2))
        return True
    else:
        return False


class UserBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        if check_if_user(username, password):  # OO커뮤니티 사이트 인증에 성공한 경우
            try:  # 유저가 있는 경우
                user = User.objects.get(username=username)
            except User.DoesNotExist:  # 유저 정보가 없지만 인증 통과시 user 생성
                user = User(email=username, username=username)
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
#pytest

from django.test import TestCase
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


@pytest.fixture
def default_group_fixture(db):
   default_group, _ = Group.objects.get_or_create(name='default')
   return default_group

@pytest.fixture
def user_with_default_group_fixture(db, default_group_fixture):
    User = get_user_model()
    return User.objects.create_user(
        'john', 'lennon@thebeatles.com', 'johnpassword',
        groups=[default_group_fixture]
    )

@pytest.fixture
def create_user():
    User = get_user_model()
    return User.objects.create_user('lennon@thebeatles.com', 'johnpassword')

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

# @pytest.fixture
# def get_or_create_token(db, create_user):
#     user = create_user
#     return user.token


@pytest.fixture
def api_client_with_credentials(
   db, create_user, api_client
):
    user = create_user
    api_client.force_authenticate(user=user)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.mark.django_db
def test_authorized_request(api_client_with_credentials):
    url = reverse('users-url')
    response = api_client_with_credentials.get(url)
    assert response.status_code == 200



@pytest.mark.django_db
@pytest.mark.parametrize(
   'email, password, status_code', [
       (None, None, 400),
       (None, 'strong_pass', 400),
       ('user@example.com', None, 400),
       ('user@example.com', 'invalid_pass', 400),
       ('user@example.com', 'strong_pass', 200),
   ]
)
def test_login_data_validation(
   email, password, status_code, api_client
):
   url = reverse('login-url')
   data = {
       'email': email,
       'password': password
   }
   response = api_client.post(url, data=data)
   assert response.status_code == status_code

# @pytest.mark.django_db
# def test_unauthorized_request(api_client, get_or_create_token):
#     url = reverse('users-url')
#     token = get_or_create_token
#     print(token)
#     api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
#     response = api_client.get(url)
#     assert response.status_code == 200


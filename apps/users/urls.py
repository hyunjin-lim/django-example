from django.urls import path
from .views import (
    RegisterCreateAPIView,
    UserListApiView,
    LoginAPIView,
)

urlpatterns = [
    path(r'login', LoginAPIView.as_view(), name="login-url"),
    path(r'users', UserListApiView.as_view(), name="users-url"),
    path(r'register', RegisterCreateAPIView.as_view())
]
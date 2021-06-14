from django.urls import path
from .views import (
    RegisterCreateAPIView,
    UserListApiView,
    LoginAPIView,
)

urlpatterns = [
    path(r'login', LoginAPIView.as_view()),
    path(r'users', UserListApiView.as_view()),
    path(r'register', RegisterCreateAPIView.as_view())
]
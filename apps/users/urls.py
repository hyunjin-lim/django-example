from django.urls import path
from .views import (RegisterCreateAPIView, UserListApiView)

urlpatterns = [
    path(r'users', UserListApiView.as_view()),
    path(r'register', RegisterCreateAPIView.as_view())
]
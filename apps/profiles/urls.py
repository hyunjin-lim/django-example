from django.urls import path

from .views import (
    ProfileListAPIView
)

urlpatterns = [
    path(r'profiles', ProfileListAPIView.as_view()),
]
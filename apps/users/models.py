from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimestampedModel
from .managers import UserManager
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from setting.redis_connect import r


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(db_index=True, max_length=255, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['-id']

    def __str__(self):
        return self.email


    @property
    def token(self):
        token = self._generate_jwt_token()
        self._set_redis(token)
        return token

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        return jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

    def _set_redis(self, token):
        dt = timedelta(days=7)
        key = '{0}:{1}'.format('user:token', token)
        r.hset(key, "id", self.pk)
        r.expire(key, int(dt.total_seconds()))

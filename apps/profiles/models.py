from django.db import models
from apps.core.models import TimestampedModel
# Create your models here.


class ProfileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user')


class Profile(TimestampedModel):
    user = models.OneToOneField(
        'users.User',
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )
    bio = models.TextField(blank=True)
    image = models.URLField(blank=True)

    objects = ProfileManager()

    def __str__(self):
        return self.user.username
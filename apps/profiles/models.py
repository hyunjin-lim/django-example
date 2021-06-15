from django.db import models
from apps.core.models import TimestampedModel
# Create your models here.


class Profile(TimestampedModel):
    user = models.OneToOneField(
        'users.User',
        on_delete=models.DO_NOTHING,
        db_constraint=False,
    )
    bio = models.TextField(blank=True)
    image = models.URLField(blank=True)

    def __str__(self):
        return self.user.username
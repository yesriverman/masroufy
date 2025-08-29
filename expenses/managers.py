# managers.py
from django.db import models

class UserScopedManager(models.Manager):
    def for_user(self, user):
        return self.get_queryset().filter(user=user)

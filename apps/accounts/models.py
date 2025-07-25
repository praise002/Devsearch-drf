import uuid
from datetime import timedelta

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.common.models import IsDeletedModel

from .managers import CustomUserManager


def slugify_two_fields(self):
    return f"{self.first_name}-{self.last_name}"


class User(AbstractBaseUser, IsDeletedModel, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = AutoSlugField(
        populate_from=slugify_two_fields, unique=True, always_update=True
    )
    email = models.EmailField(unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    user_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["username"]),
        ]
        permissions = [
            ("can_toggle_user_status", "Can toggle user active status")
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.otp)

    @property
    def is_valid(self):
        expiration_time = self.created_at + timedelta(
            minutes=settings.EMAIL_OTP_EXPIRE_MINUTES
        )
        return timezone.now() < expiration_time

from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class Skill(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey("Profile", related_name="skills", on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created"]
        unique_together = ("user", "name")

    def __str__(self):
        return self.name


class Profile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False
    )
    short_intro = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(
        upload_to="photos/%Y/%m/%d/",
        blank=True,
        null=True,
    )
    updated = models.DateTimeField(auto_now=True)

    # Social Links
    social_github = models.URLField(max_length=200, blank=True)
    social_stackoverflow = models.URLField(max_length=200, blank=True)
    social_twitter = models.URLField(max_length=200, blank=True)
    social_linkedin = models.URLField(max_length=200, blank=True)
    social_website = models.URLField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"{self.user.full_name}"

    @property
    def image_url(self):
        try:
            url = self.photo.url
        except:
            url = "https://res.cloudinary.com/dq0ow9lxw/image/upload/v1732236186/default-image_foxagq.jpg"
        return url

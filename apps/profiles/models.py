from django.conf import settings
from django.db import models

from apps.common.models import BaseModel

AVATAR_FOLDER = "avatar/"


class Skill(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def clean(self):
        if self.name:
            self.name = self.name.lower()

    def __str__(self):
        return self.name


class ProfileSkill(BaseModel):
    profile = models.ForeignKey(
        "Profile", on_delete=models.CASCADE
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("profile", "skill")

    def __str__(self):
        return f"{self.profile.user.email}'s {self.skill.name} skill"


class Profile(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False
    )
    short_intro = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to=AVATAR_FOLDER, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    # Social Links
    social_github = models.URLField(max_length=200, blank=True)
    social_stackoverflow = models.URLField(max_length=200, blank=True)
    social_twitter = models.URLField(max_length=200, blank=True)
    social_linkedin = models.URLField(max_length=200, blank=True)
    social_website = models.URLField(max_length=200, blank=True)

    skills = models.ManyToManyField(
        Skill,
        through="ProfileSkill",
        through_fields=("profile", "skill"),
        related_name="profiles",
    )

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"{self.user.full_name}"

    @property
    def avatar_url(self):
        try:
            url = self.avatar.url
        except:
            url = "https://res.cloudinary.com/dq0ow9lxw/image/upload/v1732236186/default-image_foxagq.jpg"
        return url

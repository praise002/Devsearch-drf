from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel
from apps.profiles.models import Profile
from autoslug import AutoSlugField


class Tag(BaseModel):
    name = models.CharField(_("Name"), max_length=50, blank=True)

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class Project(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    slug = AutoSlugField(populate_from="title", always_update=True, unique=True)
    owner = models.ForeignKey(
        Profile, related_name="projects", on_delete=models.CASCADE
    )
    featured_image = models.ImageField(
        _("Featured Image"), upload_to="featured_image/", blank=True
    )
    description = models.TextField(_("Description"))
    source_link = models.CharField(_("Source Code Link"), max_length=200, blank=True)
    demo_link = models.CharField(_("Demo Link"), max_length=200, blank=True)
    tags = models.ManyToManyField(Tag)
    vote_total = models.IntegerField(_("Vote Total"), default=0)
    vote_ratio = models.IntegerField(_("Vote Ratio"), default=0)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["-created"]),
            models.Index(fields=["title", "description"]),
        ]

    @property
    def featured_image_url(self) -> str:
        try:
            url = self.featured_image.url
        except:
            url = ""  # TODO: USE UPLOADED IMAGE IN CLOUDINARY LATER
        return url

    def __str__(self):
        return self.title

    @property
    def reviewers(self):
        queryset = self.reviews.all().values_list("reviewer__id", flat=True)
        return queryset

    @property
    def review_percentage(self) -> float:
        """
        Calculate the positive feedback percentage based on votes.
        """
        reviews = self.reviews.all()
        total_votes = reviews.count()

        if total_votes > 0:
            up_votes = reviews.filter(value="up").count()
            ratio = (up_votes / total_votes) * 100
            self.vote_total = total_votes
            self.vote_ratio = ratio

            self.save()


class Review(BaseModel):
    VOTE_TYPE = (
        ("up", _("Up Vote")),
        ("down", _("Down Vote")),
    )

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        Profile, related_name="votes", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=4, choices=VOTE_TYPE)
    content = models.TextField(
        _("Content"),
    )

    class Meta:
        ordering = ["-created"]
        unique_together = (
            "project",
            "reviewer",
        )  # Ensures a user can only vote once per project

    def __str__(self):
        return self.value

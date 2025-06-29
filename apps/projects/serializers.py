from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.common.serializers import SuccessResponseSerializer

from .models import Project, Review, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "source_link",
            "demo_link",
        ]

    def create(self, validated_data):
        # Get the authenticated user's profile
        user = self.context["request"].user.profile

        # Create the project and associate it with the user
        project = Project.objects.create(owner=user, **validated_data)
        return project


class FeaturedImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            "featured_image",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)  # Display owner name
    tags = TagSerializer(many=True, read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    review_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "slug",
            "owner",
            "featured_image",
            "featured_image_url",
            "description",
            "source_link",
            "demo_link",
            "tags",
            "vote_total",
            "vote_ratio",
            "review_percentage",
        ]

    @extend_schema_field(serializers.URLField)
    def get_featured_image_url(self, obj):
        return obj.featured_image_url

    @extend_schema_field(serializers.IntegerField)
    def get_review_percentage(self, obj):
        return obj.review_percentage


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "value", "content"]

class ProjectResponseSerializer(SuccessResponseSerializer):
    data = ProjectSerializer()
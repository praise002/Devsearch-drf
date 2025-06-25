from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Profile, Skill

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "description"]
        # extra_kwargs = {"description": {"required": False}}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    user = UserUpdateSerializer()

    class Meta:
        model = Profile
        fields = [
            "user",
            "short_intro",
            "bio",
            "location",
            "social_github",
            "social_stackoverflow",
            "social_twitter",
            "social_linkedin",
        ]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user",
            "short_intro",
            "bio",
            "location",
            "social_github",
            "social_stackoverflow",
            "social_twitter",
            "social_linkedin",
            "skills",
            "image_url",
        ]

    @extend_schema_field(serializers.URLField)
    def get_image_url(self, obj):
        return obj.image_url

class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            "image",
        ]
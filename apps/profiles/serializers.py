from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Profile, Skill

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "short_intro",
            "bio",
            "location",
            "social_github",
            "social_stackoverflow",
            "social_twitter",
            "social_linkedin",
        ]
        
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        # update user fields
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()
            
        return super().update(instance, validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)

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
            "avatar_url",
        ]

    @extend_schema_field(serializers.URLField)
    def get_avatar_url(self, obj):
        return obj.avatar_url


class AvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            "avatar",
        ]

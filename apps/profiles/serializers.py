from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Profile, ProfileSkill, Skill

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class ProfileSkillSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="skill.id", read_only=True)
    name = serializers.CharField(source="skill.name", read_only=True)

    class Meta:
        model = ProfileSkill
        fields = ["id", "name", "description"]


class ProfileSkillCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="skill.name")

    class Meta:
        model = ProfileSkill
        fields = ["name"]

    def create(self, validated_data):
        request = self.context.get("request")
        skill_name = validated_data.pop("skill")["name"].lower()

        skill, _ = Skill.objects.get_or_create(name=skill_name)

        profile_skill, created = ProfileSkill.objects.get_or_create(
            profile=request.user.profile, skill=skill
        )

        if not created:
            raise serializers.ValidationError(
                {"name": f"You already have '{skill.name}' skill in your profile."}
            )

        return profile_skill


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
        user_data = validated_data.pop("user", {})
        # update user fields
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        return super().update(instance, validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = serializers.SerializerMethodField()
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

    @extend_schema_field(ProfileSkillSerializer(many=True))
    def get_skills(self, obj):
        profile_skills = obj.profileskill_set.all().select_related("skill")
        return ProfileSkillSerializer(profile_skills, many=True).data

    @extend_schema_field(serializers.URLField)
    def get_avatar_url(self, obj):
        return obj.avatar_url


class AvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            "avatar",
        ]

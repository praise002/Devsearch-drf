from .models import Profile, Skill
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'description']
        extra_kwargs = {
            'description': {'required': False}
        }
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            "user",
            "short_intro", "bio", "location", "photo",
            "social_github", "social_stackoverflow",
            "social_twitter", "social_linkedin",
            "skills",
        ] 
        extra_kwargs = {
            'short_intro': {'required': False},
            'bio': {'required': False},
            'location': {'required': False},
            'photo': {'required': False},
            'social_github': {'required': False},
            'social_stackoverflow': {'required': False},
            'social_twitter': {'required': False},
            'social_linkedin': {'required': False},
        }
        

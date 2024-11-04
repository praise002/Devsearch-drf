from rest_framework import serializers
from .models import Tag, Project, Review
from apps.profiles.models import Profile  # Assuming Profile exists in the profiles app

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)  # Display owner name
    tags = TagSerializer(many=True, read_only=True)
    featured_image_url = serializers.ReadOnlyField()
    review_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'owner', "featured_image", 'featured_image_url',
            'description', 'source_link', 'demo_link', 'tags',
            'vote_total', 'vote_ratio', 'review_percentage'
        ]
        read_only_fields = ['vote_total', 'vote_ratio']

class ReviewSerializer(serializers.ModelSerializer):
    # project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    # reviewer = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'value', 'content']
        # extra_kwargs = {
        #     'value': {'required': True},
        #     'content': {'required': True},
        # } TODO: MIGHT NOT BE NEEDED, TEST AND REMOVE

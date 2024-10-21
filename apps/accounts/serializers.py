from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Use the custom user manager to create a user with the validated data
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user
    
    def validate(self, attrs):
        first_name = attrs['first_name']
        last_name = attrs['last_name']
        
        if len(first_name.split()) > 1:
            raise serializers.ValidationError({'first_name': 'No spacing allowed'})
        
        if len(last_name.split()) > 1:
            raise serializers.ValidationError({'last_name': 'No spacing allowed'})

        return attrs

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Authenticate the user
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(_('Invalid email or password.'))
        
        # If authentication is successful, add the user to validated_data
        attrs['user'] = user
        return attrs
        
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

# from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.common.serializers import SuccessResponseSerializer
from .models import  User


# REQUEST SERIALIZERS
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Use the custom user manager to create a user with the validated data
        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
        return user

    def validate(self, attrs):
        first_name = attrs["first_name"]
        last_name = attrs["last_name"]

        if len(first_name.split()) > 1:
            raise serializers.ValidationError({"first_name": "No spacing allowed"})

        if len(last_name.split()) > 1:
            raise serializers.ValidationError({"last_name": "No spacing allowed"})

        return attrs

    def validate_password(self, value):
        try:
            validate_password(value)  # This invokes all default password validators
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)  # Raise any validation errors
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Get the standard token with default claims
        token = super().get_token(user)
        # Add custom claim for username
        token["username"] = user.username
        return token


class SendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError({"error": "Old password is incorrect."})

        return value

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                {"error": "Password must be at least 8 characters long."}
            )
        return value
    
    def save(self, **kwargs):
        user = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save() #TODO: MIGHT MOVE LATER


class RequestPasswordResetOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField(
        validators=[MinValueValidator(100000), MaxValueValidator(999999)]
    )
    

class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)
    
    def validate_new_password(self, value):
        try:
            validate_password(value)  # This invokes all default password validators
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)  # Raise any validation errors
        return value


# RESPONSES


class RegisterResponseSerializer(SuccessResponseSerializer):
    email = serializers.EmailField(default="bob123@example.com")


class LoginResponseSerializer(SuccessResponseSerializer):
    data = serializers.DictField(
        default={
            "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMxMDY5NzEyLCJpYXQiOjE3MzA5ODMzMTIsImp0aSI6ImIzYTM2NmEwMDZkZTQxZTg4YzRlNDhmNzZmYmYyNWQ0IiwidXNlcl9pZCI6IjNhYzFlMzJiLTUzOWYtNDZkYi05ODZlLWRiZDFkZDQyYmUzMCIsInVzZXJuYW1lIjoiZGF2aWQtYmFkbXVzIn0.YuhFA2m47oDiwkOUd359hcumhN6lX5QfvXd92ES8vSQ",
            "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczODc1OTMxMiwiaWF0IjoxNzMwOTgzMzEyLCJqdGkiOiI5NjBkZmE2NTFhYjk0YWYzYTU4MjgzMTcwYjIxODEwYiIsInVzZXJfaWQiOiIzYWMxZTMyYi01MzlmLTQ2ZGItOTg2ZS1kYmQxZGQ0MmJlMzAiLCJ1c2VybmFtZSI6ImRhdmlkLWJhZG11cyJ9.A5shgQ-SI891PRS6nDs4-LA6ZNBoVXmLF2L9VMXoPC4",
        }
    )

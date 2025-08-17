from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import BlacklistedToken, OutstandingToken

from apps.accounts.models import Otp
from apps.common.errors import ErrorCode
from apps.common.responses import CustomResponse


def validate_password_strength(value):
    try:
        validate_password(value)  # This invokes all default password validators
    except DjangoValidationError as e:
        raise serializers.ValidationError(e.messages)  # Raise any validation errors
    return value


def invalidate_previous_otps(user):
    Otp.objects.filter(user=user).delete()


def get_otp_record(user, otp):
    """ "Checks for the validity and existence of otp associated with a user"""
    try:
        otp_record = Otp.objects.get(user=user, otp=otp)

        if not otp_record.is_valid:
            return CustomResponse.error(
                message="Invalid or expired OTP. Please enter a valid OTP or request a new one.",
                err_code=ErrorCode.VALIDATION_ERROR,
            )

        return otp_record

    except Otp.DoesNotExist:
        return CustomResponse.error(
            message="Invalid or expired OTP. Please enter a valid OTP or request a new one.",
            err_code=ErrorCode.VALIDATION_ERROR,
        )


def blacklist_token(user):
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


def get_client_ip(self, request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

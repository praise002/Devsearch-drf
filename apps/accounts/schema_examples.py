from django.conf import settings
from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
    RefreshTokenResponseSerializer,
    RegisterSerializer,
    RequestPasswordResetOtpSerializer,
    SendOtpSerializer,
    SetNewPasswordSerializer,
    VerifyOtpSerializer,
)
from apps.common.errors import ErrorCode
from apps.common.schema_examples import (
    ACCESS_TOKEN,
    ERR_RESPONSE_STATUS,
    REFRESH_TOKEN,
    SUCCESS_RESPONSE_STATUS,
)
from apps.common.serializers import ErrorDataResponseSerializer, ErrorResponseSerializer

REGISTER_EXAMPLE = {"email": "bob123@example.com"}

if settings.DEBUG:
    LOGIN_EXAMPLE = {
        "access": ACCESS_TOKEN,
    }
    PASSWORD_CHANGE_EXAMPLE = {
        "access": ACCESS_TOKEN,
    }
else:
    LOGIN_EXAMPLE = {
        "refresh": REFRESH_TOKEN,
        "access": ACCESS_TOKEN,
    }
    PASSWORD_CHANGE_EXAMPLE = {
        "refresh": REFRESH_TOKEN,
        "access": ACCESS_TOKEN,
    }

if settings.DEBUG:
    REFRESH_TOKEN_EXAMPLE = {
        "access": ACCESS_TOKEN,
    }
else:
    REFRESH_TOKEN_EXAMPLE = {
        "access": ACCESS_TOKEN,
        "refresh": REFRESH_TOKEN,
    }

UNAUTHORIZED_USER_RESPONSE = OpenApiResponse(
    response=ErrorResponseSerializer,
    description="Unauthorized User or Invalid Access Token",
    examples=[
        OpenApiExample(
            name="Unauthorized User",
            value={
                "status": ERR_RESPONSE_STATUS,
                "message": "Authentication credentials were not provided.",
                "err_code": ErrorCode.UNAUTHORIZED,
            },
        ),
        OpenApiExample(
            name="Invalid Access Token",
            value={
                "status": ERR_RESPONSE_STATUS,
                "message": "Token is Invalid or Expired.",
                "err_code": ErrorCode.INVALID_TOKEN,
            },
        ),
    ],
)

REGISTER_RESPONSE_EXAMPLE = {
    # 201: RegisterResponseSerializer,
    201: OpenApiResponse(
        response=RegisterSerializer,
        description="OTP Sent Successful",
        examples=[
            OpenApiExample(
                name="OTP Sent Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "OTP sent for email verification.",
                    "data": REGISTER_EXAMPLE,
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}

LOGIN_RESPONSE_EXAMPLE = {
    # 200: LoginResponseSerializer,
    200: OpenApiResponse(
        response=CustomTokenObtainPairSerializer,
        description="Login Successful",
        examples=[
            OpenApiExample(
                name="Login Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Login successful.",
                    "data": LOGIN_EXAMPLE,
                },
            ),
        ],
    ),
    401: OpenApiResponse(
        response=CustomTokenObtainPairSerializer,
        description="Unauthorized",
        examples=[
            OpenApiExample(
                name="Unauthorized",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "No active account found with the given credentials.",
                    "code": ErrorCode.UNAUTHORIZED,
                },
            ),
        ],
    ),
    403: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Permission Denied",
        examples=[
            OpenApiExample(
                name="Email not verified",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Email not verified. Please verify your email before logging in.",
                    "code": ErrorCode.FORBIDDEN,
                },
            ),
            OpenApiExample(
                name="Account disabled",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Your account has been disabled. Please contact support for assistance.",
                    "code": ErrorCode.FORBIDDEN,
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}

RESEND_VERIFICATION_EMAIL_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=SendOtpSerializer,
        description="OTP Resent Successful",
        examples=[
            OpenApiExample(
                name="OTP Resent Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "OTP sent successfully.",
                },
            ),
            OpenApiExample(
                name="Email already verified",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Your email is already verified. No OTP sent.",
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Validation Error",
        examples=[
            OpenApiExample(
                name="No account found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "No account is associated with this email.",
                    "code": ErrorCode.VALIDATION_ERROR,
                },
            ),
            OpenApiExample(
                name="Field Validation Error",
                value={
                    "status": "error",
                    "message": "Some fields are invalid.",
                    "code": "validation_error",
                    "data": {"email": ["This field is required."]},
                },
            ),
        ],
    ),
}

VERIFY_EMAIL_RESPONSE_EXAMPLE = {
    # 200: SuccessResponseSerializer,
    200: OpenApiResponse(
        response=VerifyOtpSerializer,
        description="Email Verification Successful",
        examples=[
            OpenApiExample(
                name="Email Verification Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Email verified successfully.",
                },
            ),
            OpenApiExample(
                name="Email already verified",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Email address already verified. No OTP sent.",
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
        examples=[
            OpenApiExample(
                name="No account found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "No account is associated with this email.",
                    "code": ErrorCode.VALIDATION_ERROR,
                },
            ),
            OpenApiExample(
                name="Invalid OTP",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Invalid or expired OTP. Please enter a valid OTP or request a new one.",
                    "code": ErrorCode.VALIDATION_ERROR,
                },
            ),
            OpenApiExample(
                name="Field Validation Error",
                value={
                    "status": "error",
                    "message": "Some fields are invalid.",
                    "code": "validation_error",
                    "data": {"otp": ["This field is required."]},
                },
            ),
        ],
    ),
}

LOGOUT_RESPONSE_EXAMPLE = {
    # 200: SuccessResponseSerializer,
    200: OpenApiResponse(
        response=PasswordChangeSerializer,
        description="Logout Successful",
        examples=[
            OpenApiExample(
                name="Logout Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Logged out successfully.",
                },
            ),
        ],
    ),
    401: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Unauthorized User or Invalid Refresh Token",
        examples=[
            OpenApiExample(
                name="Invalid Refresh Token",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Token is Invalid or Expired.",
                    "err_code": ErrorCode.INVALID_TOKEN,
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}

LOGOUT_ALL_RESPONSE_EXAMPLE = {
    # 200: SuccessResponseSerializer,
    200: OpenApiResponse(
        response=PasswordChangeSerializer,
        description="Logout Successful",
        examples=[
            OpenApiExample(
                name="Logout Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Successfully logged out from all devices.",
                },
            ),
        ],
    ),
    401: ErrorResponseSerializer,
    500: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Internal Server Error",
        examples=[
            OpenApiExample(
                name="Logout Error",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Error during logout",
                    "code": ErrorCode.SERVER_ERROR,
                },
            ),
        ],
    ),
}

PASSWORD_CHANGE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=PasswordChangeSerializer,
        description="Password Change Successful",
        examples=[
            OpenApiExample(
                name="Password Change Successful (Production)",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Password changed successfully. Please use the new tokens.",
                    "data": PASSWORD_CHANGE_EXAMPLE,
                },
            ),
            OpenApiExample(
                name="Password Change Successful (Debug)",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Password changed successfully. Please use the new access token.",
                    "data": {"access": ACCESS_TOKEN},
                },
            ),
        ],
    ),
    401: UNAUTHORIZED_USER_RESPONSE,
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
        examples=[
            OpenApiExample(
                name="Password mismatch",
                value={
                    "status": "error",
                    "message": "Some fields are invalid.",
                    "code": "validation_error",
                    "data": {
                        "error": ["New password and confirm password do not match."]
                    },
                },
            ),
            OpenApiExample(
                name="Incorrect old password",
                value={
                    "status": "error",
                    "message": "Some fields are invalid.",
                    "code": "validation_error",
                    "data": {
                        "error": [
                            "The current password you entered is incorrect. Please try again."
                        ]
                    },
                },
            ),
        ],
    ),
}

PASSWORD_RESET_REQUEST_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=RequestPasswordResetOtpSerializer,
        description="Password Reset Request Successful",
        examples=[
            OpenApiExample(
                name="Password Reset Request Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "If that email address is in our database, we will send you an email to reset your password.",
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
        examples=[
            OpenApiExample(
                name="Field Validation Error",
                value={
                    "status": "error",
                    "message": "Some fields are invalid.",
                    "code": "validation_error",
                    "data": {"email": ["This field is required."]},
                },
            ),
        ],
    ),
}

VERIFY_OTP_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=VerifyOtpSerializer,
        description="OTP Verification Successful",
        examples=[
            OpenApiExample(
                name="OTP Verification Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "OTP verified, proceed to set a new password.",
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
        examples=[
            OpenApiExample(
                name="No account found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "No account is associated with this email.",
                    "code": ErrorCode.VALIDATION_ERROR,
                },
            ),
            OpenApiExample(
                name="Invalid OTP",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Invalid or expired OTP. Please enter a valid OTP or request a new one.",
                    "code": ErrorCode.VALIDATION_ERROR,
                },
            ),
            OpenApiExample(
                name="Field Validation Error",
                value={
                    "status": "error",
                    "message": "Some fields are invalid.",
                    "code": "validation_error",
                    "data": {"otp": ["This field is required."]},
                },
            ),
        ],
    ),
}

PASSWORD_RESET_DONE_RESPONSE_EXAMPLE = {
    200: OpenApiResponse(
        response=SetNewPasswordSerializer,
        description="Password Reset Successful",
        examples=[
            OpenApiExample(
                name="Password Reset Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Your password has been reset, proceed to login.",
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
        examples=[
            OpenApiExample(
                name="No account found",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "No account is associated with this email.",
                    "code": ErrorCode.VALIDATION_ERROR,
                },
            ),
            OpenApiExample(
                name="Password mismatch",
                value={
                    "status": "error",
                    "message": "Some fields are invalid.",
                    "code": "validation_error",
                    "data": {
                        "error": ["New password and confirm password do not match."]
                    },
                },
            ),
            OpenApiExample(
                name="Field Validation Error",
                value={
                    "status": "error",
                    "message": "Some fields are invalid.",
                    "code": "validation_error",
                    "data": {"email": ["This field is required."]},
                },
            ),
        ],
    ),
}

REFRESH_TOKEN_RESPONSE_EXAMPLE = {
    # 200: RefreshTokenResponseSerializer,
    # 401: ErrorResponseSerializer,
    # 422: ErrorDataResponseSerializer,
    200: OpenApiResponse(
        response=RefreshTokenResponseSerializer,
        description="Refresh Token Successful",
        examples=[
            OpenApiExample(
                name="Refresh Token Successful",
                value={
                    "status": SUCCESS_RESPONSE_STATUS,
                    "message": "Token refreshed successfully.",
                    "data": REFRESH_TOKEN_EXAMPLE,
                },
            ),
        ],
    ),
    401: OpenApiResponse(
        response=ErrorResponseSerializer,
        description="Unauthorized User or Invalid Refresh Token",
        examples=[
            OpenApiExample(
                name="Invalid Refresh Token",
                value={
                    "status": ERR_RESPONSE_STATUS,
                    "message": "Token is Invalid or Expired.",
                    "err_code": ErrorCode.INVALID_TOKEN,
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        response=ErrorDataResponseSerializer,
        description="Validation Error",
    ),
}

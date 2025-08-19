import logging

from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.accounts.emails import SendEmail
from apps.accounts.schema_examples import (
    LOGIN_RESPONSE_EXAMPLE,
    LOGOUT_ALL_RESPONSE_EXAMPLE,
    LOGOUT_RESPONSE_EXAMPLE,
    PASSWORD_CHANGE_RESPONSE_EXAMPLE,
    PASSWORD_RESET_DONE_RESPONSE_EXAMPLE,
    PASSWORD_RESET_REQUEST_RESPONSE_EXAMPLE,
    REFRESH_TOKEN_RESPONSE_EXAMPLE,
    REGISTER_RESPONSE_EXAMPLE,
    RESEND_VERIFICATION_EMAIL_RESPONSE_EXAMPLE,
    VERIFY_EMAIL_RESPONSE_EXAMPLE,
    VERIFY_OTP_RESPONSE_EXAMPLE,
)
from apps.accounts.utils import (
    blacklist_token,
    get_client_ip,
    get_otp_record,
    invalidate_previous_otps,
)
from apps.common.errors import ErrorCode
from apps.common.responses import CustomResponse

from .models import User
from .permissions import IsUnauthenticated
from .serializers import (
    CustomTokenObtainPairSerializer,
    PasswordChangeSerializer,
    RegisterSerializer,
    RequestPasswordResetOtpSerializer,
    SendOtpSerializer,
    SetNewPasswordSerializer,
    VerifyOtpSerializer,
)

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("security")
auth_logger = logging.getLogger("auth")

tags = ["Auth"]


class RegisterView(APIView):
    """
    Handles user registration with email verification.
    Creates new user account and sends OTP for email verification.
    Security: Requires email verification before account activation.
    """

    serializer_class = RegisterSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account and sends OTP for email verification. User must verify email before login.",
        tags=tags,
        responses=REGISTER_RESPONSE_EXAMPLE,
        auth=[],
    )
    def post(self, request):
        client_ip = get_client_ip(request)

        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            data = serializer.validated_data

            auth_logger.info(
                f"User registration successful",
                extra={
                    "event_type": "user_registration",
                    "status": "success",
                    "email": data["email"],
                    "user_id": user.id,
                    "client_ip": client_ip,
                    "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                },
            )

            # Send OTP for email verification
            SendEmail.send_email(request, user)

            return CustomResponse.success(
                message="OTP sent for email verification.",
                data={"email": data["email"]},
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            auth_logger.warning(
                f"User registration failed",
                extra={
                    "event_type": "user_registration",
                    "status": "failed",
                    "email": request.data.get("email"),  # data["email"] will fail
                    "client_ip": client_ip,
                    "error": str(e),
                    "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                },
            )
            raise  # Let DRF handle the exception and return appropriate error response


class LoginView(TokenObtainPairView):
    """
    Authenticates users and issues JWT tokens.
    Security: Validates email verification and account status before login.
    """

    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="Login a user",
        description="Authenticates user credentials and returns JWT tokens. Validates email verification and account status.",
        responses=LOGIN_RESPONSE_EXAMPLE,
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        client_ip = get_client_ip(request)

        try:
            serializer.is_valid(raise_exception=True)
            email = request.data.get("email")

            user = User.objects.get(email=email)

            # Check if the user's email is verified
            if not user.is_email_verified:
                security_logger.warning(
                    f"Login attempt with unverified email",
                    extra={
                        "event_type": "login_attempt",
                        "status": "blocked_unverified",
                        "email": email,
                        "user_id": user.id,
                        "client_ip": client_ip,
                        "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                    },
                )
                # If email is not verified, prompt them to request an OTP
                return CustomResponse.error(
                    message="Email not verified. Please verify your email before logging in.",
                    status_code=status.HTTP_403_FORBIDDEN,
                    err_code=ErrorCode.FORBIDDEN,
                )

            if not user.user_active:
                security_logger.warning(
                    f"Login attempt on disabled account",
                    extra={
                        "event_type": "login_attempt",
                        "status": "blocked_disabled",
                        "email": email,
                        "user_id": user.id,
                        "client_ip": client_ip,
                        "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                    },
                )
                # Frontend can redirect helpful page to show how to contact support
                return CustomResponse.error(
                    message="Your account has been disabled. Please contact support for assistance.",
                    status_code=status.HTTP_403_FORBIDDEN,
                    err_code=ErrorCode.FORBIDDEN,
                )

        except TokenError as e:
            security_logger.error(
                f"Login error occurred",
                extra={
                    "event_type": "login_error",
                    "email": email,
                    "client_ip": client_ip,
                    "error": str(e),
                    "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                },
            )
            raise InvalidToken(e.args[0])

        if settings.DEBUG:
            # Extract the refresh token from the response
            refresh = serializer.validated_data["refresh"]
            access = serializer.validated_data["access"]

            # Set the refresh token as an HTTP-only cookie
            response = CustomResponse.success(
                message="Login successful.",
                data={
                    "access": access,
                },
                status_code=status.HTTP_200_OK,
            )
            response.set_cookie(
                key="refresh",
                value=refresh,
                httponly=True,  # Prevent JavaScript access
                secure=True,  # Only send over HTTPS
                samesite="None",  # Allow cross-origin requests if frontend and backend are on different domains
            )
        else:
            response = CustomResponse.success(
                message="Login successful.",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK,
            )

        auth_logger.info(
            f"User login successful",
            extra={
                "event_type": "login",
                "status": "success",
                "email": email,
                "user_id": user.id,
                "client_ip": client_ip,
                "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
            },
        )
        return response


class ResendVerificationEmailView(APIView):
    """
    Resends email verification OTP to users.
    Security: Rate limiting through OTP invalidation prevents spam.
    """

    serializer_class = SendOtpSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Resend email verification OTP",
        description="Sends OTP to user's email for verification. Invalidates previous OTPs for security.",
        responses=RESEND_VERIFICATION_EMAIL_RESPONSE_EXAMPLE,
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
            if user.is_email_verified:
                return CustomResponse.success(
                    message="Your email is already verified. No OTP sent.",
                    status_code=status.HTTP_200_OK,
                )

            # Invalidate/clear any previous OTPs
            invalidate_previous_otps(user)

            # Send OTP to user's email
            SendEmail.send_email(request, user)

            return CustomResponse.success(
                message="OTP sent successfully.",
                status_code=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            # left it cos email is gotten from localStorage in the frontend
            return CustomResponse.error(
                message="No account is associated with this email.",
                err_code=ErrorCode.VALIDATION_ERROR,
            )


class VerifyEmailView(APIView):
    """
    Verifies user email address using OTP.
    Security: Clears OTP after successful verification to prevent reuse.
    Triggers welcome email after verification completion.
    """

    serializer_class = VerifyOtpSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Verify a user's email",
        description="Verifies user email using OTP. Clears OTP after verification and sends welcome email.",
        responses=VERIFY_EMAIL_RESPONSE_EXAMPLE,
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
            otp_result = get_otp_record(user, otp)

            # Why? for it not to fail when it returns a Response
            if hasattr(otp_result, "status_code"):
                return otp_result

            # Check if user is already verified
            if user.is_email_verified:
                # Clear the OTP
                invalidate_previous_otps(user)
                return CustomResponse.success(
                    message="Email address already verified. No OTP sent.",
                    status_code=status.HTTP_200_OK,
                )

            user.is_email_verified = True
            user.save()

            # Clear OTP after verification
            invalidate_previous_otps(user)

            SendEmail.welcome(request, user)
            return CustomResponse.success(
                message="Email verified successfully.",
                status_code=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            # left it cos email is gotten from localStorage in the frontend
            return CustomResponse.error(
                message="No account is associated with this email.",
                err_code=ErrorCode.VALIDATION_ERROR,
            )


class LogoutView(TokenBlacklistView):
    """
    Logs out user from current session.
    Security: Blacklists the current refresh token to prevent reuse.
    """

    @extend_schema(
        summary="Logout a user",
        description="Logs out user from current session by blacklisting their refresh token.",
        responses=LOGOUT_RESPONSE_EXAMPLE,
        tags=tags,
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        if settings.DEBUG:
            # Clear the HTTP-only cookie containing the refresh token
            response.delete_cookie("refresh")
        else:

            response = CustomResponse.success(
                message="Logged out successfully.", status_code=status.HTTP_200_OK
            )
        return response


class LogoutAllView(APIView):
    """
    Logs out user from all devices/sessions.
    Security: Blacklists all active refresh tokens for the user.
    Use case: When user suspects account compromise or wants to force re-authentication.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(
        summary="Logout from all devices",
        description="Blacklists all refresh tokens for the user, logging them out from all devices.",
        tags=tags,
        responses=LOGOUT_ALL_RESPONSE_EXAMPLE,
    )
    def post(self, request):
        client_ip = get_client_ip(request)
        try:
            user = request.user

            # Get all valid tokens for the user
            tokens = OutstandingToken.objects.filter(
                user=user, expires_at__gt=timezone.now(), blacklistedtoken=None
            )

            # Blacklist all tokens
            for token in tokens:
                RefreshToken(token.token).blacklist()

            security_logger.info(
                f"User logged out from all devices",
                extra={
                    "event_type": "logout_all_devices",
                    "user_id": user.id,
                    "email": user.email,
                    "client_ip": client_ip,
                    "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                },
            )

            return CustomResponse.success(
                message="Successfully logged out from all devices.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(
                f"Logout all devices error",
                extra={
                    "event_type": "logout_all_error",
                    "user_id": user.id,
                    "error": str(e),
                    "client_ip": client_ip,
                },
            )
            return CustomResponse.error(
                message="Error during logout",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                err_code=ErrorCode.SERVER_ERROR,
            )


class PasswordChangeView(APIView):
    """
    Changes user password while maintaining current session.
    Security: Blacklists all other sessions but preserves current session with new tokens.
    Token rotation: Issues new access/refresh tokens to prevent session hijacking.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    @extend_schema(
        summary="Change user password",
        description="Allows authenticated users to change their password. Blacklists all other sessions and issues new tokens for current session.",
        responses=PASSWORD_CHANGE_RESPONSE_EXAMPLE,
        tags=tags,
    )
    def post(self, request):
        client_ip = get_client_ip(request)
        user = request.user

        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            # Get the new tokens from the serializer's save method
            new_tokens = serializer.save()

            if settings.DEBUG:
                security_logger.info(
                    f"Password changed successfully",
                    extra={
                        "event_type": "password_change",
                        "status": "success",
                        "user_id": user.id,
                        "email": user.email,
                        "client_ip": client_ip,
                        "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                    },
                )
                response = CustomResponse.success(
                    message="Password changed successfully.",
                    data={"access": new_tokens["access"]},
                    status_code=status.HTTP_200_OK,
                )
                response.set_cookie(
                    key="refresh",
                    value=new_tokens["refresh"],
                    httponly=True,
                    secure=True,
                    samesite="None",
                )
                return response

            else:
                security_logger.info(
                    f"Password changed successfully",
                    extra={
                        "event_type": "password_change",
                        "status": "success",
                        "user_id": user.id,
                        "email": user.email,
                        "client_ip": client_ip,
                        "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                    },
                )
                return CustomResponse.success(
                    message="Password changed successfully.",
                    data=new_tokens,  # Contains 'refresh' and 'access' tokens
                    status_code=status.HTTP_200_OK,
                )

        except Exception as e:
            security_logger.warning(
                f"Password change failed",
                extra={
                    "event_type": "password_change",
                    "status": "failed",
                    "user_id": user.id,
                    "email": user.email,
                    "client_ip": client_ip,
                    "error": str(e),
                    "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                },
            )
            raise  # Let DRF handle the exception and return appropriate error response


class PasswordResetRequestView(APIView):
    """
    Initiates password reset process by sending OTP.
    Security: Always returns same message to prevent email enumeration.
    Privacy: Invalidates previous OTPs to prevent timing attacks.
    """

    permission_classes = (IsUnauthenticated,)
    serializer_class = RequestPasswordResetOtpSerializer

    @extend_schema(
        summary="Request password reset OTP",
        description="Sends password reset OTP to user's email. Returns generic message for security.",
        responses=PASSWORD_RESET_REQUEST_RESPONSE_EXAMPLE,
        tags=tags,
        auth=[],
    )
    def post(self, request):
        client_ip = get_client_ip(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
            invalidate_previous_otps(user)
            SendEmail.send_password_reset_email(request, user)
            auth_logger.info(
                f"Password reset email sent",
                extra={
                    "event_type": "password_reset_email_sent",
                    "user_id": user.id,
                    "email": email,
                    "client_ip": client_ip,
                },
            )
        except User.DoesNotExist:
            # silently pass due to security reasons
            security_logger.warning(
                f"Password reset attempted on non-existent account",
                extra={
                    "event_type": "password_reset_invalid_email",
                    "email": email,
                    "client_ip": client_ip,
                    "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
                },
            )

        # ALWAYS return the same message
        return CustomResponse.success(
            message="If that email address is in our database, we will send you an email to reset your password.",
            status_code=status.HTTP_200_OK,
        )


class VerifyOtpView(APIView):
    """
    Verifies OTP for password reset process.
    Security: Clears OTP after verification to prevent reuse.
    Intermediate step: Validates OTP before allowing password reset.
    """

    permission_classes = (IsUnauthenticated,)
    serializer_class = VerifyOtpSerializer

    @extend_schema(
        summary="Verify password reset OTP",
        description="Verifies the password reset OTP before allowing new password setup.",
        responses=VERIFY_OTP_RESPONSE_EXAMPLE,
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)

            otp_result = get_otp_record(user, otp)
            # Why? for it not to fail when it returns a Response
            if hasattr(otp_result, "status_code"):
                return otp_result

            # Clear OTP after verification
            invalidate_previous_otps(user)
            return CustomResponse.success(
                message="OTP verified, proceed to set a new password.",
                status_code=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            # left it cos email is gotten from localStorage in the frontend
            return CustomResponse.error(
                message="No account is associated with this email.",
                err_code=ErrorCode.VALIDATION_ERROR,
            )


class PasswordResetDoneView(APIView):
    """
    Completes password reset process with new password.
    Security: Blacklists all existing sessions for the user.
    Forces re-authentication: User must login again with new password.
    """

    permission_classes = (IsUnauthenticated,)
    serializer_class = SetNewPasswordSerializer

    @extend_schema(
        summary="Set new password",
        description="Sets a new password and blacklists all existing sessions for security.",
        responses=PASSWORD_RESET_DONE_RESPONSE_EXAMPLE,
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
            # Update the user's password
            user.set_password(new_password)
            user.save()

            blacklist_token(user)

            SendEmail.password_reset_success(request, user)

            return CustomResponse.success(
                message="Your password has been reset, proceed to login.",
                status_code=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            # input is gotten from user, it is good to give them quick feedback on its existence
            return CustomResponse.error(
                message="No account is associated with this email.",
                err_code=ErrorCode.VALIDATION_ERROR,
            )


class RefreshTokensView(TokenRefreshView):
    """
    Refreshes JWT access tokens using valid refresh token.
    Security: Validates refresh token before issuing new access token.
    """

    @extend_schema(
        summary="Refresh user access token",
        description="Refreshes access token using valid refresh token. Returns new tokens for continued authentication.",
        tags=tags,
        responses=REFRESH_TOKEN_RESPONSE_EXAMPLE,
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to refresh the JWT token
        """
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        if settings.DEBUG:
            response = CustomResponse.success(
                message="Token refreshed successfully.",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK,
            )
        else:
            # Extract the new refresh token from the response
            refresh = serializer.validated_data["refresh"]
            access = serializer.validated_data("access")

            # Set the new refresh token as an HTTP-only cookie
            response = CustomResponse.success(
                message="Token refreshed successfully.",
                data={"access": access},
                status_code=status.HTTP_200_OK,
            )

            response.set_cookie(
                key="refresh",
                value=refresh,
                httponly=True,  # Prevent JavaScript access
                secure=True,  # Only send over HTTPS
                samesite="None",  # Allow cross-origin requests if frontend and backend are on different domains
            )

        return response


# TODO:
# Staticfiles for admin still not working in heroku

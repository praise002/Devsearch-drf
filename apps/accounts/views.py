from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from apps.accounts.emails import SendEmail
from .serializers import (
    PasswordChangeSerializer,
    RegisterSerializer,
    RequestPasswordResetOtpSerializer,
    ResetPasswordWithOtpSerializer,
    SendOtpSerializer,
    VerifyOtpSerializer,
    CustomTokenObtainPairSerializer,
    RegisterResponseSerializer,
    LoginResponseSerializer,
)

from apps.common.serializers import (
    ErrorDataResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from .models import User, Otp
from .permissions import IsUnauthenticated
from rest_framework.permissions import AllowAny


tags = ["Auth"]


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Register a new user",
        description="This endpoint registers new users into our application",
        tags=tags,
        responses={
            201: RegisterResponseSerializer,
            400: ErrorDataResponseSerializer,
        },
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = serializer.validated_data

        # Send OTP for email verification
        SendEmail.send_otp(request, user)

        return Response(
            {
                "message": "OTP sent for email verification.",
                "email": data["email"],
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        summary="Login a user",
        description="This endpoint generates new access and refresh tokens for authentication",
        responses={
            200: LoginResponseSerializer,
            404: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data.get("email"))

            # Check if the user's email is verified
            if not user.is_email_verified:
                # If email is not verified, prompt them to request an OTP
                return Response(
                    {
                        "message": "Email not verified. Please verify your email before logging in.",
                        "next_action": "send_otp",  # Inform the client to call SendOtpView
                        "email": user.email,  # Send back the email to pass it to SendOtpView
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND
            )

        # If email is verified, proceed with the normal token generation process
        return super().post(request, *args, **kwargs)


class SendOtpView(APIView):
    serializer_class = SendOtpSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Send OTP to a user's email",
        description="This endpoint sends OTP to a user's email for verification",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account is associated with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Invalidate/clear any previous OTPs TODO: MIGHT MOVE TO ANOTHER FN LATER
        Otp.objects.filter(user=user).delete()

        # Send OTP to user's email
        SendEmail.send_otp(request, user)

        return Response(
            {"message": "OTP sent successfully."}, status=status.HTTP_200_OK
        )


class VerifyOtpView(APIView):
    serializer_class = VerifyOtpSerializer
    permission_classes = (IsUnauthenticated,)

    @extend_schema(
        summary="Verify a user's email",
        description="This endpoint verifies a user's email",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
            410: ErrorResponseSerializer,
        },
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
        except User.DoesNotExist:
            return Response(
                {"error": "No account is associated with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the OTP is valid for this user
        try:
            otp_record = Otp.objects.get(user=user, otp=otp)
        except Otp.DoesNotExist:
            return Response(
                {"error": "Invalid OTP provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if OTP is expired
        if not otp_record.is_valid:
            return Response(
                {
                    "error": "OTP has expired.",
                    "next_action": "request_new_otp",
                    "request_url": "/api/v1/auth/send-otp/",
                },
                status=status.HTTP_410_GONE,
            )

        # Check if user is already verified
        if user.is_email_verified:
            # Clear the OTP
            Otp.objects.filter(user=user).delete()
            return Response(
                {"error": "Email address already verified!"},
            )

        user.is_email_verified = True
        user.save()

        # Clear OTP after verification
        Otp.objects.filter(user=user).delete()

        SendEmail.welcome(request, user)

        return Response(
            {"message": "Email verified successfully."}, status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = None

    @extend_schema(
        summary="Logout a user",
        description="This endpoint logs a user out from our application",
        responses={
            205: SuccessResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=tags,
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    @extend_schema(
        summary="Change user password",
        description="This endpoint allows authenticated users to update their account password. The user must provide their current password for verification along with the new password they wish to set. If successful, the password will be updated, and a response will confirm the change.",
        responses={
            200: SuccessResponseSerializer,
            422: ErrorDataResponseSerializer,
        },
        tags=tags,
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class PasswordResetRequestView(APIView):
    permission_classes = (IsUnauthenticated,)
    serializer_class = RequestPasswordResetOtpSerializer

    @extend_schema(
        summary="Send Password Reset Otp",
        description="This endpoint sends new password reset otp to the user's email",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Clear otps if another otp is requested
        Otp.objects.filter(user=user).delete()

        # Send OTP to user's email
        SendEmail.send_password_reset_otp(request, user)

        return Response(
            {"message": "OTP sent successfully."}, status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    permission_classes = (IsUnauthenticated,)
    serializer_class = ResetPasswordWithOtpSerializer

    @extend_schema(
        summary="Set New Password",
        description="This endpoint verifies the password reset OTP and sets a new password if the OTP is valid.",
        responses={
            200: SuccessResponseSerializer,
            400: ErrorDataResponseSerializer,
            404: ErrorResponseSerializer,
            410: ErrorResponseSerializer,
        },
        tags=tags,
        auth=[],
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # This call will set the new password and save the user instance
        serializer.save()

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "No account is associated with this email."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the OTP is valid for this user
        try:
            otp_record = Otp.objects.get(user=user, otp=otp)
        except Otp.DoesNotExist:
            return Response(
                {"error": "Invalid OTP provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if OTP is expired
        if not otp_record.is_valid:
            return Response(
                {
                    "error": "OTP has expired. Please request a new one.",
                    "next_action": "request_new_otp",
                },
                status=status.HTTP_410_GONE,
            )

        # Update the user's password
        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)
        user.save()

        # Clear OTP after verification
        Otp.objects.filter(user=user).delete()

        SendEmail.password_reset_success(request, user)

        return Response(
            {"message": "Your password has been reset, proceed to login."},
            status=status.HTTP_200_OK,
        )


class RefreshTokensView(TokenRefreshView):
    @extend_schema(
        summary="Refresh user access token",
        description="This endpoint allows users to refresh their access token using a valid refresh token. It returns a new access token, which can be used for further authenticated requests.",
        tags=tags,
        responses={
            200: SuccessResponseSerializer,  # response schema for successful token refresh
            401: ErrorDataResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to refresh the JWT token
        """
        response = super().post(request, *args, **kwargs)

        return response


# WRITE TEST TO TEST ALL CASES OF RESPONSE ERROR

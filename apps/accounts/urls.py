from django.urls import path

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view()),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("token/", views.LoginView.as_view()),
    path("token/refresh/", views.RefreshTokensView.as_view(), name="token_refresh"),
    path("token/revoke/", views.LogoutView.as_view()),
    path("otp/", views.SendVerificationEmailView.as_view(), name="send_email"),
    path("otp/verify/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("password-change/", views.PasswordChangeView.as_view()),
    path("password-reset/otp/", views.PasswordResetRequestView.as_view()),
    path("password-reset/otp/verify/", views.VerifyOtpView.as_view()),
    path("password-reset/done/", views.PasswordResetDoneView.as_view()),
]

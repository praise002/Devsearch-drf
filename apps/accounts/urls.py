from django.urls import path

from . import views

# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
#     TokenBlacklistView,
# )


urlpatterns = [
    # Authentication
    path("register/", views.RegisterView.as_view()),
    path("token/", views.LoginView.as_view()),
    path("token/refresh/", views.RefreshTokensView.as_view()),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # Sessions (for logout)
    path("sessions/", views.LogoutView.as_view()),
    path("sessions/all/", views.LogoutAllView.as_view()),
    
    # Verification
    path("verification/", views.ResendVerificationEmailView.as_view()),
    path("verification/verify/", views.VerifyEmailView.as_view()),
    
    # Password management
    path("passwords/change/", views.PasswordChangeView.as_view()),
    path("passwords/reset/", views.PasswordResetRequestView.as_view()),
    path("passwords/reset/verify/", views.VerifyOtpView.as_view()),
    path("passwords/reset/complete/", views.PasswordResetDoneView.as_view()),
]


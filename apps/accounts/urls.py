from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .import views

urlpatterns = [
    path('register/', views.RegisterView.as_view()),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/', views.LoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view()),
    
    path('send-otp/', views.SendOtpView.as_view(), name='send_otp'),
    path('verify-otp/', views.VerifyOtpView.as_view(), name='verify_otp'),
    
    path('password/change/', views.PasswordChangeView.as_view()),
]

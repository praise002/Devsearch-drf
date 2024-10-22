from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.emails import SendEmail
from .serializers import RegisterSerializer, SendOtpSerializer, VerifyOtpSerializer
from .models import User
import random

class RegisterView(APIView):
    permission_classes = [AllowAny] 
    serializer_class = RegisterSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Send OTP for email verification
        SendEmail.send_otp(request, user)
           
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'OTP sent for email verification.'
        }, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(email=request.data.get('email'))
            
            # Check if the user's email is verified
            if not user.is_email_verified:
                # If email is not verified, prompt them to request an OTP
                return Response({
                    'message': 'Email not verified. Please verify your email before logging in.',
                    'next_action': 'send_otp', # Inform the client to call SendOtpView
                    'email': user.email  # Send back the email to pass it to SendOtpView
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({'error': 'User does not exist.'},
                            status=status.HTTP_404_NOT_FOUND)
            
        # If email is verified, proceed with the normal token generation process
        return super().post(request, *args, **kwargs)

class SendOtpView(APIView):
    def post(self, request):
        serializer = SendOtpSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Send OTP to user's email
        SendEmail.send_otp(request, user)
        
        return Response({'message': 'OTP sent successfully.'}, 
                        status=status.HTTP_200_OK)
        
class VerifyOtpView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
       
        user = User.objects.get(email=email)
        user.is_email_verified = True
        user.otp = None  # Clear OTP after verification
        user.save()   
        
        SendEmail.welcome(request, user)         
        
        return Response({'message': 'Email verified successfully.'}, 
                        status=status.HTTP_200_OK)
        
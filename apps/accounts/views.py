from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from apps.accounts.emails import SendEmail
from .serializers import (PasswordChangeSerializer, RegisterSerializer, 
                          RequestPasswordResetOtpSerializer, 
                          ResetPasswordWithOtpSerializer, 
                          SendOtpSerializer, VerifyOtpSerializer,
                          CustomTokenObtainPairSerializer,
                          RegisterResponseSerializer,
                          ErrorDataResponseSerializer)
from .models import User, Otp
from .permissions import IsUnauthenticated

tags = ["Auth"]

class RegisterView(APIView):
    serializer_class = RegisterSerializer
    
    @extend_schema(
        summary="Register a new user",
        description="This endpoint registers new users into our application",
        tags=tags,
        responses={201: RegisterResponseSerializer, 400: ErrorDataResponseSerializer},
    )
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = serializer.validated_data
        
        # Create JWT tokens
        # refresh = RefreshToken.for_user(user)
        
        # Send OTP for email verification
        SendEmail.send_otp(request, user)
           
        return Response({
            # 'refresh': str(refresh),
            # 'access': str(refresh.access_token),
            'message': 'OTP sent for email verification.',
            'email': data['email']
        }, status=status.HTTP_201_CREATED)

class LoginView(TokenObtainPairView):
    # permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer
    
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
        
        # Invalidate/clear any previous OTPs TODO: MIGHT MOVE TO ANOTHER FN LATER
        Otp.objects.filter(user=user).delete()
        
        # Send OTP to user's email
        SendEmail.send_otp(request, user)
        
        return Response({'message': 'OTP sent successfully.'}, 
                        status=status.HTTP_200_OK)
        
class VerifyOtpView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        #TODO: CHECK IF EMAIL IS VERIFIED THEN RETURN A RESPONSE
       
        user = User.objects.get(email=email)
        user.is_email_verified = True
        user.save() 
        
        # Clear OTP after verification
        Otp.objects.filter(user=user).delete()
          
        SendEmail.welcome(request, user)         
        
        return Response({'message': 'Email verified successfully.'}, 
                        status=status.HTTP_200_OK)
        
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful.'},
                            status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, 
                            status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data,
                                              context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password changed successfully.'}, 
                        status=status.HTTP_200_OK)
        
class PasswordResetRequestView(APIView):
    permission_classes = (IsUnauthenticated,)
    
    def post(self, request):
        serializer = RequestPasswordResetOtpSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Clear otps if another otp is requested 
        Otp.objects.filter(user=user).delete()
        
        # Send OTP to user's email
        SendEmail.send_password_reset_otp(request, user)
        
        return Response({'message': 'OTP sent successfully.'}, 
                        status=status.HTTP_200_OK)
    
class PasswordResetConfirmView(APIView):
    permission_classes = (IsUnauthenticated,)
    
    def post(self, request):
        serializer = ResetPasswordWithOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)   
        # This call will set the new password and save the user instance
        serializer.save()
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Clear OTP after verification
        Otp.objects.filter(user=user).delete()
        
        SendEmail.password_reset_success(request, user)      
        
        return Response({'message': 'Your password has been reset, proceed to login.'}, 
                        status=status.HTTP_200_OK)
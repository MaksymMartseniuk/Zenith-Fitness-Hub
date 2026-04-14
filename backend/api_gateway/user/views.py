from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from .utils import send_verification_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str

User = get_user_model()

# Create your views here.
class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        print(f"Received registration request with email: {email}")
        print(f"Password provided: {'Yes' if password else 'No'}")
        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email is already registered.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(email=email, password=password,is_email_verified=False)

        from .models import Profile
        Profile.objects.create(user=user)

        send_verification_email(user)

        return Response({'message': 'User registered successfully.', 'email': user.email}, status=status.HTTP_201_CREATED)
    
class VerifyEmailView(APIView):
    permission_classes=[AllowAny]
    def post(self, request, uidb64, token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user=None
        if user is not None and default_token_generator.check_token(user, token):
            if user.is_email_verified:
                return Response({'message': 'Email is already verified.'}, status=status.HTTP_200_OK)
            user.is_email_verified=True
            user.save()
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)
        


        



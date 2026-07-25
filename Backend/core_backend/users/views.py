from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView
from .models import CustomUser, Profile
from .serializers import (
    CustomUserSerializer,
    ProfileSerializer,
    VerifyEmailSerializer,
    ResendVerificationEmailSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    GoogleAuthSerializer,
    CustomTokenObtainPairSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from .services import send_verification_email, send_password_reset_email
import secrets
from rest_framework_simplejwt.tokens import RefreshToken

from .throttles import (
    RegisterRateThrottle,
    VerifyEmailRateThrottle,
    ResendVerifyRateThrottle,
    PasswordResetConfirmRateThrottle,
    PasswordResetRequestRateThrottle,
    ChangePasswordRateThrottle,
    UserMeRateThrottle,
    LoginRateThrottle,
)

from google.oauth2 import id_token
from google.auth.transport import requests as GoogleRequests
from rest_framework_simplejwt.views import TokenObtainPairView
from core.settings import GOOGLE_CLIENT_ID

# Create your views here.


class UserRegistrationView(CreateAPIView):
    """Endpoint for user registration.
    Allows access to create a new user with email and password.
    """

    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    throttle_classes = (RegisterRateThrottle,)

    def create(self, request, *args, **kwargs):
        """Override the create method to handle user registration."""
        serializer_data = self.get_serializer(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        serializer_data.save()
        return Response(
            {
                "message": "User registered successfully. Please check your email for verification.",
            },
            status=status.HTTP_201_CREATED,
        )


class CustomeTokenObtainPairView(TokenObtainPairView):
    throttle_classes = (LoginRateThrottle,)


class UserVerificationEmailView(GenericAPIView):
    """Endpoint for verifying a user's email using a verification code sent to their email."""

    permission_classes = [AllowAny]
    serializer_class = VerifyEmailSerializer
    throttle_classes = (VerifyEmailRateThrottle,)

    def post(self, request, *args, **kwargs):
        serializer_data = self.get_serializer(data=request.data)
        serializer_data.is_valid()
        email = serializer_data.validated_data["email"]
        verification_code = serializer_data.validated_data["verification_code"]
        cache_key: str = f"email_verification_code_{email}"
        saved_code = cache.get(cache_key)

        if saved_code is None or str(saved_code) != str(verification_code):
            return Response(
                {"error": "Invalid or expired verification code."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user: CustomUser = CustomUser.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {"message": "Email is already verified."}, status=status.HTTP_200_OK
                )
            user.is_verified = True
            user.save(update_fields=["is_verified"])
            cache.delete(cache_key)

            return Response(
                {"message": "Email verified successfully! You can now log in."},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ResendVerificationEmailView(GenericAPIView):
    """Endpoint for resending verification code for email"""

    permission_classes = [AllowAny]
    serializer_class = ResendVerificationEmailSerializer
    throttle_classes = (ResendVerifyRateThrottle,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user: CustomUser = CustomUser.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {"message": "Email is already verified. You can log in."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            send_verification_email.delay(user_id=user.id)
            return Response(
                {
                    "message": "Verification code resent successfully. Please check your email."
                },
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User with this email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class PasswordResetRequestView(GenericAPIView):
    """Endpoint to request a password reset link."""

    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    throttle_classes = (PasswordResetRequestRateThrottle,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            reset_token = secrets.token_urlsafe(32)
            cache_key = f"reset_token:{reset_token}"
            cache.set(cache_key, email, timeout=900)
            send_password_reset_email(email, reset_token)
        except CustomUser.DoesNotExist:
            pass

        return Response(
            {
                "message": "If an account with this email exists, a password reset link has been sent."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(GenericAPIView):
    """Endpoint to set a new password using a token."""

    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    throttle_classes = (PasswordResetConfirmRateThrottle,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["password"]
        cache_key = f"reset_token:{token}"
        email = cache.get(cache_key)
        if not email:
            return Response(
                {"error": "Invalid or expired reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user: CustomUser = CustomUser.objects.get(email=email)
            user.set_password(new_password)
            user.save(update_fields=["password"])
            cache.delete(cache_key)
            return Response(
                {
                    "message": "Password has been reset successfully. You can now log in."
                },
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User associated with this token no longer exists."},
                status=status.HTTP_404_NOT_FOUND,
            )


class LogoutView(GenericAPIView):
    """
    Endpoint for user logout.
    Blacklists the provided refresh token.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = serializer.validated_data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(
                {"error": "Token is invalid or already blacklisted."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangePasswordView(GenericAPIView):
    """
    Endpoint for changing password. Requires JWT authentication.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    throttle_classes = (ChangePasswordRateThrottle,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        old_password = serializer.validated_data["old_password"]
        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Wrong old password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response(
            {"message": "Password updated successfully."}, status=status.HTTP_200_OK
        )


class UserMeView(RetrieveAPIView):
    """
    Endpoint to retrieve the currently authenticated user's details.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    throttle_classes = (UserMeRateThrottle,)

    def get_object(self):
        return self.request.user


class GoogleLoginView(GenericAPIView):
    """
    Endpoint for Google Social Authentication.
    Accepts an id_token, verifies it with Google, and returns JWT tokens.
    """

    permission_classes = [AllowAny]
    serializer_class = GoogleAuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token_id"]
        try:
            idinfo = id_token.verify_oauth2_token(
                token, GoogleRequests.Request(), GOOGLE_CLIENT_ID
            )
            email = idinfo["email"]
            first_name = idinfo.get("given_name", "")
            last_name = idinfo.get("family_name", "")

            user, created = CustomUser.objects.get_or_create(email=email)
            if created:
                user.is_verified = True
                user.set_unusable_password()
                user.save()
                user.profile.first_name = first_name
                user.profile.last_name = last_name
                user.profile.save(update_fields=["first_name", "last_name"])
            refresh = CustomTokenObtainPairSerializer.get_token(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "is_new_user": created,
                },
                status=status.HTTP_200_OK,
            )

        except ValueError:
            return Response(
                {"error": "Invalid or expired Google token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

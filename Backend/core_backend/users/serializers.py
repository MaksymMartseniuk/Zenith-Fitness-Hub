from rest_framework import serializers
from .models import CustomUser, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .services import send_verification_email
from rest_framework.exceptions import AuthenticationFailed


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for the CustomUser model, handling user registration and validation."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "password",
            "confirm_password",
            "telegram_id",
            "is_staff",
            "is_superuser",
            "is_active",
            "is_verified",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "is_staff",
            "is_superuser",
            "is_active",
            "is_verified",
            "date_joined",
        ]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError(
                {"password": "Password and Confirm Password do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop(
            "confirm_password", None
        )  # Remove confirm_password as it's not needed for user creation
        password = validated_data.pop("password")
        validated_data["is_verified"] = False  # Set is_verified to False for new users
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        send_verification_email.delay(user.id)  # Send verification email asynchronously
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "goal",
            "birth_date",
            "height_cm",
            "weight_kg",
            "current_fat_percentage",
            "activity_level",
            "preferred_environment",
            "target_workouts_per_week",
            "measurement_system",
            "timezone",
            "experience_level",
            "is_premium",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at", "is_premium"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise AuthenticationFailed(
                "Please verify your email address before logging in."
            )
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        if hasattr(user, "profile"):
            token["first_name"] = user.profile.first_name
        return token


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for verifying a user's email using a verification code."""

    email = serializers.EmailField(required=True)
    verification_code = serializers.CharField(required=True, max_length=6)


class ResendVerificationEmailSerializer(serializers.Serializer):
    """Serializer for resending the verification code"""

    email = serializers.EmailField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for sending a password reset link."""

    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for setting a new password via token."""

    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password": "The two password fields didn't match."}
            )
        return attrs


class LogoutSerializer(serializers.Serializer):
    """Serializer for handling user logout by blacklisting the refresh token."""

    refresh = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password when user is already authenticated."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"new_password": "The two password fields didn't match."}
            )
        return attrs

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from django.utils import timezone
# Create your models here.


class GenderEnums(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"


class GoalEnums(models.TextChoices):
    MAINTENANCE = "maintenance", "Maintenance"
    WEIGHT_LOSS = "weight_loss", "Weight Loss"
    MUSCLE_GAIN = "muscle_gain", "Muscle Gain"


class ActivityLevelEnums(models.TextChoices):
    SEDENTARY = "sedentary", "Sedentary"
    LIGHTLY_ACTIVE = "lightly_active", "Lightly Active"
    MODERATELY_ACTIVE = "moderately_active", "Moderately Active"
    VERY_ACTIVE = "very_active", "Very Active"
    EXTRA_ACTIVE = "extra_active", "Extra Active"


class WorkoutEnvironmentEnums(models.TextChoices):
    GYM = "gym", "Gym"
    HOME = "home", "Home"
    OUTDOOR = "outdoor", "Outdoor"


class MeasurementSystemEnums(models.TextChoices):
    METRIC = "metric", "Metric"
    IMPERIAL = "imperial", "Imperial"


class ExperienceLevelEnums(models.TextChoices):
    BEGINNER = "beginner", "Beginner"
    INTERMEDIATE = "intermediate", "Intermediate"
    ADVANCED = "advanced", "Advanced"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        error_messages={"unique": "A user with that email already exists."},
    )
    telegram_id = models.CharField(max_length=255, blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(
        max_length=10, blank=True, null=True, choices=GenderEnums.choices
    )
    goal = models.CharField(
        max_length=20, blank=True, null=True, choices=GoalEnums.choices
    )
    birth_date = models.DateField(blank=True, null=True)
    height_cm = models.FloatField(blank=True, null=True)
    weight_kg = models.FloatField(blank=True, null=True)
    current_fat_percentage = models.FloatField(blank=True, null=True)
    activity_level = models.CharField(
        max_length=20, blank=True, null=True, choices=ActivityLevelEnums.choices
    )
    preferred_environment = models.CharField(
        max_length=10, blank=True, null=True, choices=WorkoutEnvironmentEnums.choices
    )
    target_workouts_per_week = models.IntegerField(blank=True, null=True)
    measurement_system = models.CharField(
        max_length=10, blank=True, null=True, choices=MeasurementSystemEnums.choices
    )
    timezone = models.CharField(max_length=50, blank=True, null=True, default="UTC")
    experience_level = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=ExperienceLevelEnums.choices,
        default=ExperienceLevelEnums.BEGINNER,
    )
    is_premium = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

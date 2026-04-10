from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email=models.EmailField(unique=True, max_length=255,null=False,blank=False,db_index=True)
    telegram_id=models.CharField(max_length=255,null=True,blank=True,unique=True,db_index=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    class Meta:
        db_table='users'


class Profile(models.Model):
    class Genders(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
    class Goals(models.TextChoices):
        WEIGHT_LOSS = 'WL', 'Weight Loss'
        MUSCLE_GAIN = 'MG', 'Muscle Gain'
        MAINTENANCE = 'MT', 'Maintenance'
    class ExperienceLevels(models.TextChoices):
        BEGINNER= 'BG', 'Beginner'
        INTERMEDIATE = 'IM', 'Intermediate'
        ADVANCED = 'AD', 'Advanced'
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    first_name=models.CharField(max_length=255,null=True)
    last_name=models.CharField(max_length=255,null=True)
    gender=models.CharField(max_length=1, choices=Genders.choices,null=True)
    goal=models.CharField(max_length=2, choices=Goals.choices,null=True)
    birth_date=models.DateField(null=True)
    height=models.FloatField(null=True)
    weight=models.FloatField(null=True)
    current_fat_percentage=models.FloatField(null=True)
    experience_level=models.CharField(max_length=2, choices=ExperienceLevels.choices,null=True)
    is_premium=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
from rest_framework import serializers
from .models import User, Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','email','telegram_id','is_staff','is_active','created_at']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields=['id','user','first_name','last_name','gender',
                'goal','birth_date','height','weight','current_fat_percentage',
                'experience_level','is_premium','created_at']

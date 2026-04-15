from rest_framework import serializers
from .models import User, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if getattr(self.user, 'is_email_verified', False) is False:
            raise serializers.ValidationError('Email is not verified.', code='email_not_verified')
        return data

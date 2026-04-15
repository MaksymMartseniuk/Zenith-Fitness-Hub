from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def send_verification_email(user):
    token=default_token_generator.make_token(user)
    uid=urlsafe_base64_encode(force_bytes(user.pk))
    verification_link=f"http://localhost:3000/verify-email/{uid}/{token}/"
    subject="Verify your email for Zenith Fitness Hub"
    message=f'''Hi {user.email},\n\nPlease click the link below to verify your email address:\n\n{verification_link}\n\n
    If you did not create an account, please ignore this email.\n\nBest regards,\nZenith Fitness Hub Team'''
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def send_password_reset_email(user):
    token=default_token_generator.make_token(user)
    uid=urlsafe_base64_encode(force_bytes(user.pk))
    reset_link=f"http://localhost:3000/reset-password/{uid}/{token}/"
    subject="Reset your password for Zenith Fitness Hub"
    message=f'''Hi {user.email},\n\nPlease click the link below to reset your password:\n\n{reset_link}\n\n
    If you did not request a password reset, please ignore this email.\n\nBest regards,\nZenith Fitness Hub Team'''
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
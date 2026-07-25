from celery import shared_task
import secrets
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser
from core.settings import FRONTEND_URL


@shared_task
def send_verification_email(user_id: int) -> None:
    """Send a verification email to the newly registered user."""
    from .models import CustomUser  # Importing here to avoid circular imports

    try:
        user: CustomUser = CustomUser.objects.get(id=user_id)
        secure_code: str = str(100000 + secrets.randbelow(900000))
        cache_key: str = f"email_verification_code_{user.email}"
        cache.set(cache_key, secure_code, timeout=600)  # Store code for 10 minutes

        context: dict[str, str] = {"verification_code": secure_code}
        html_content: str = render_to_string("emails/verify_email.html", context)
        text_content: str = strip_tags(html_content)

        email: EmailMultiAlternatives = EmailMultiAlternatives(
            subject="Welcome to Zenith Fitness Hub - Verify Your Email",
            body=text_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
    except CustomUser.DoesNotExist:
        return "User does not exist."


@shared_task
def cleanup_unverified_users() -> str:
    """Periodary task for deleting unverifying users"""
    expiration_date = timezone.now() - timedelta(hours=24)
    deleted_count, _ = CustomUser.objects.filter(
        is_verified=False, date_joined__lt=expiration_date
    ).delete()
    return f"Deleted {deleted_count} unverified users."


@shared_task
def send_password_reset_email(email: str, reset_token: str) -> str:
    """Send Email for reseting password of users accounts"""
    frontend_url = FRONTEND_URL
    reset_link = f"{frontend_url}/reset-password?{reset_token}"
    subject = "Password Reset Request - Zenith Fitness Hub"
    html_message = render_to_string(
        "emails/password-reset.html", {"reset_link": reset_link}
    )
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    email_message = EmailMultiAlternatives(
        subject=subject, body=plain_message, from_email=from_email, to=[email]
    )
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()
    return f"Password reset link sent to {email}"

from django.urls import path

from .views import (
    UserRegistrationView,
    UserVerificationEmailView,
    ResendVerificationEmailView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    ChangePasswordView,
    UserMeView,
    LogoutView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .throttles import LoginRateThrottle


userurlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path(
        "token/",
        TokenObtainPairView.as_view(throttle_classes=(LoginRateThrottle,)),
        name="token-obtain",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("verify-email/", UserVerificationEmailView.as_view(), name="verify-email"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "resend-verification-code/",
        ResendVerificationEmailView.as_view(),
        name="resend-verification-code",
    ),
    path(
        "password-reset-request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("me/", UserMeView.as_view(), name="me"),
]

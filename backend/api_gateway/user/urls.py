from django.urls import path
from .views import RegisterUserView, VerifyEmailView, CustomerTokenObtainPairView, ForgetPasswordView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', CustomerTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('forget-password/', ForgetPasswordView.as_view(), name='forget-password'),
    path('reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
]
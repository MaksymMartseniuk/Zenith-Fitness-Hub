from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from unittest.mock import patch, ANY
from faker import Faker

CustomUser = get_user_model()


class PasswordManagementTest(APITestCase):
    """Test suite for password reset and password change endpoints."""

    def setUp(self):
        cache.clear()
        self.faker = Faker()
        self.reset_request_url = reverse("password-reset-request")
        self.reset_confirm_url = reverse("password-reset-confirm")
        self.change_password_url = reverse("change-password")

        self.password = self.faker.password(
            length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
        )

        self.user = CustomUser.objects.create_user(
            email=self.faker.unique.email(), password=self.password
        )
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()

    @patch("users.views.send_password_reset_email.delay")
    def test__password_reset_request_success(self, mock_send_email):
        """TEST SUCCESS: Valid email requests a password reset link/code."""
        data = {"email": self.user.email}
        response = self.client.post(self.reset_request_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "If an account with this email exists, a password reset link has been sent.",
        )
        mock_send_email.assert_called_once_with(self.user.email, ANY)

    @patch("users.views.send_password_reset_email.delay")
    def test_password_reset_request_nonexistent_email(self, mock_send_email):
        """TEST SUCCESS (Security): Non-existent email still returns 200 OK to prevent enumeration."""
        data = {"email": "ghost@example.com"}
        response = self.client.post(self.reset_request_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "If an account with this email exists, a password reset link has been sent.",
        )
        mock_send_email.assert_not_called()

    def test_password_reset_request_throttling(self):
        """TEST FAILURE: Ensure throttling limits the number of reset requests."""
        data = {"email": self.user.email}

        for _ in range(3):
            self.client.post(self.reset_request_url, data)

        response = self.client.post(self.reset_request_url, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_password_reset_confirm_success(self):
        """TEST SUCCESS: User successfully resets password with valid token from Redis."""
        reset_token = "random_test_token_123"
        cache_key = f"reset_token:{reset_token}"
        cache.set(cache_key, self.user.email, timeout=300)
        new_password = "NewStrongPassword123!"
        data = {
            "token": reset_token,
            "password": new_password,
            "confirm_password": new_password,
        }
        response = self.client.post(self.reset_confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertIsNone(cache.get(f"reset_token:{reset_token}"))

    def test_password_reset_confirm_invalid_token(self):
        """TEST FAILURE: Password reset fails with invalid or expired token."""
        data = {
            "token": "fake-or-expired-token",
            "password": "NewStrongPassword123!",
            "confirm_password": "NewStrongPassword123!",
        }
        response = self.client.post(self.reset_confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_different_password(self):
        """TEST FAILURE: Password reset fails with different passwords"""
        reset_token = "random_test_token_123"
        cache_key = f"reset_token:{reset_token}"
        cache.set(cache_key, self.user.email, timeout=300)
        new_password = "NewStrongPassword123!"
        new_password_confirm = "NEWSTRONGPASSWOR0D123@"
        data = {
            "token": reset_token,
            "password": new_password,
            "confirm_password": new_password_confirm,
        }
        response = self.client.post(self.reset_confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_success(self):
        """TEST SUCCESS: Authenticated user can change their password."""
        self.client.force_authenticate(user=self.user)
        new_password = "AnotherNewPassword123!"
        data = {
            "old_password": self.password,
            "new_password": new_password,
            "confirm_password": new_password,
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_change_password_wrong_old_password(self):
        """TEST FAILURE: Change password fails if old password is incorrect."""
        self.client.force_authenticate(user=self.user)
        new_password = "AnotherNewPassword123!"
        data = {
            "old_password": "WrongOldPassword123!",
            "new_password": new_password,
            "confirm_password": new_password,
        }
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_change_password_mismatch(self):
        """TEST FAILURE: Change password fails if new_password and confirm_password do not match."""
        self.client.force_authenticate(user=self.user)
        data = {
            "old_password": self.password,
            "new_password": "NewPassword123!",
            "confirm_password": "DifferentPassword123!",
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_unauthenticated(self):
        """TEST FAILURE: Unauthenticated user cannot change password."""
        new_password = "AnotherNewPassword123!"
        data = {
            "old_password": self.password,
            "new_password": new_password,
            "confirm_password": new_password,
        }
        response = self.client.post(self.change_password_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

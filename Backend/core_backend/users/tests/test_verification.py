from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from unittest.mock import patch
from faker import Faker

CustomUser = get_user_model()


class UserVerificationTest(APITestCase):
    """Test suite for email verification and resending verification codes."""

    def setUp(self):
        cache.clear()
        self.faker = Faker()
        self.verify_email = reverse("verify-email")
        self.resend_verification_code = reverse("resend-verification-code")

        self.user = CustomUser.objects.create_user(
            email=self.faker.unique.email(),
            password=self.faker.password(
                length=12,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ),
        )
        self.user.is_verified = False
        self.user.save()

        self.verification_code = "123456"
        self.cache_key = f"email_verification_code_{self.user.email}"

    def test_verify_email_success(self):
        """TEST SUCCESS: User successfully verifies email with a valid code."""
        cache.set(self.cache_key, self.verification_code, timeout=300)
        data = {"email": self.user.email, "verification_code": self.verification_code}
        response = self.client.post(self.verify_email, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        self.assertIsNone(cache.get(self.cache_key))

    def test_verify_email_invalid_code(self):
        """TEST FAILURE: Verification fails if the code is wrong or expired."""
        cache.set(self.cache_key, "654321", timeout=300)
        data = {"email": self.user.email, "verification_code": self.verification_code}
        response = self.client.post(self.verify_email, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)

    @patch("users.views.send_verification_email.delay")
    def test_resend_verification_success(self, mock_send_email):
        """TEST SUCCESS: Unverified user can request a new verification code."""
        data = {"email": self.user.email}
        response = self.client.post(self.resend_verification_code, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_email.assert_called_once_with(user_id=self.user.id)

    def test_resend_verification_already_verified(self):
        """TEST FAILURE: Verified user cannot request a new verification code."""
        self.user.is_verified = True
        self.user.save()
        data = {"email": self.user.email}
        response = self.client.post(self.resend_verification_code, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_email_expired_code(self):
        """TEST FAILURE: Verification fails if the code has expired (not in Redis cache)."""
        data = {"email": self.user.email, "verification_code": self.verification_code}
        response = self.client.post(self.verify_email, data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)

    def test_verify_email_user_not_found(self):
        """TEST FAILURE: Verification fails if the email does not exist in the database."""
        data = {"email": "test@gmail.com", "verification_code": self.verification_code}
        response = self.client.post(self.verify_email, data)
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )

    def test_verify_email_throttling(self):
        """TEST FAILURE: Ensure throttling prevents brute-forcing the verification code."""
        cache.set(self.cache_key, self.verification_code, timeout=300)
        data = {"email": self.user.email, "verification_code": "654321"}
        for _ in range(11):
            self.client.post(self.verify_email, data)
        response = self.client.post(self.verify_email, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @patch("users.views.send_verification_email.delay")
    def test_resend_verification_throttling(self, mock_send_email):
        """TEST FAILURE: Ensure throttling prevents spamming the resend email endpoint."""
        data = {"email": self.user.email}
        for _ in range(3):
            self.client.post(self.resend_verification_code, data)
        response = self.client.post(self.resend_verification_code, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

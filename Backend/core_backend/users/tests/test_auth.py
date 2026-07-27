from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from faker import Faker
from django.core.cache import cache

CustomUser = get_user_model()


class AuthenticationTest(APITestCase):
    """Test suite for JWT authentication (login), token refresh, and logout."""

    def setUp(self):
        cache.clear()
        self.faker = Faker()
        self.login_url = reverse("token-obtain")
        self.refresh_url = reverse("token-refresh")
        self.logout_url = reverse("logout")

        self.password = self.faker.password(
            length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
        )

        self.verified_user = CustomUser.objects.create_user(
            email=self.faker.unique.email(), password=self.password
        )
        self.verified_user.is_verified = True
        self.verified_user.is_active = True
        self.verified_user.save()

        self.unverified_user = CustomUser.objects.create_user(
            email=self.faker.unique.email(), password=self.password
        )
        self.unverified_user.is_verified = False
        self.unverified_user.is_active = True
        self.unverified_user.save()

    def test_login_success(self):
        """TEST SUCCESS: Verified user can log in and receive JWT tokens."""
        data = {
            "email": self.verified_user.email,
            "password": self.password,
        }
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_password(self):
        """TEST FAILURE: Login fails with incorrect password."""
        data = {"email": self.verified_user.email, "password": "WRONGPASSWORD123"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unverified_user(self):
        """TEST FAILURE: Unverified user cannot log in even with correct credentials."""
        data = {"email": self.unverified_user.email, "password": self.password}
        response = self.client.post(self.login_url, data)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_login_nonexistent_user(self):
        """TEST FAILURE: Login fails if the user does not exist."""
        data = {"email": "nobody@example.com", "password": "Password123!"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user(self):
        """TEST FAILURE: Inactive users (e.g., banned) cannot log in."""
        self.verified_user.is_active = False
        self.verified_user.save()

        data = {"email": self.verified_user.email, "password": self.password}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        """TEST SUCCESS: Valid refresh token issues a new access token."""
        login_data = {"email": self.verified_user.email, "password": self.password}
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data["refresh"]
        response = self.client.post(self.refresh_url, {"refresh": refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid(self):
        """TEST FAILURE: Fake or invalid refresh token is rejected."""
        response = self.client.post(self.refresh_url, {"refresh": "fake-invalid-token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        """TEST SUCCESS: User can log out and their refresh token is blacklisted."""
        # 1. Логінимось
        login_data = {"email": self.verified_user.email, "password": self.password}
        login_response = self.client.post(self.login_url, login_data)
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.post(self.logout_url, {"refresh": refresh_token})
        self.assertIn(
            response.status_code, [status.HTTP_200_OK, status.HTTP_205_RESET_CONTENT]
        )

        refresh_response = self.client.post(
            self.refresh_url, {"refresh": refresh_token}
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_unauthenticated(self):
        """TEST FAILURE: Unauthenticated user cannot access the logout endpoint."""
        response = self.client.post(self.logout_url, {"refresh": "some-token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

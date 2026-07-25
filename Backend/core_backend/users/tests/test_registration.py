from faker import Faker
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.core.cache import cache

CustomUser = get_user_model()


class UserRegistrationTest(APITestCase):
    """Test suite for user registration API endpoints."""

    def setUp(self):
        """Set up initial data and configurations for the tests."""
        cache.clear()
        self.register_url = reverse("user-register")
        self.faker = Faker()
        password = self.faker.password(
            length=12,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        )
        self.user_data = {
            "email": self.faker.unique.email(),
            "password": password,
            "confirm_password": password,
        }

    @patch("users.views.send_verification_email.delay")
    def test_user_registration_success(self, mock_send_email):
        """TEST SUCCESS: Ensure a new user can register successfully with valid credentials."""
        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)

        user = CustomUser.objects.get(email=self.user_data["email"])

        self.assertFalse(user.is_verified)
        mock_send_email.assert_called_once_with(user.id)

    def test_user_registration_duplicate_email(self):
        """TEST FAILURE: Ensure registration is rejected if the email is already registered."""
        CustomUser.objects.create_user(
            email=self.user_data["email"], password=self.user_data["password"]
        )

        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_registration_invalid_email(self):
        """TEST FAILURE: Ensure registration is rejected if the email format is invalid."""
        invalid_data = {
            "email": "not-an-email-format",
            "password": self.user_data["password"],
            "confirm_password": self.user_data["password"],
        }

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_registration_invalid_password(self):
        """TEST FAILURE: Ensure registration is rejected if the password is too weak."""
        invalid_data = {
            "email": self.user_data["email"],
            "password": "12345",
            "confirm_password": 12345,
        }

        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    @patch("users.views.send_verification_email.delay")
    def test_user_registration_creates_profile(self, mock_send_email):
        """TEST SUCCESS: Ensure a user profile is automatically created via post_save signals upon registration."""
        self.client.post(self.register_url, self.user_data)
        user = CustomUser.objects.get(email=self.user_data["email"])

        self.assertTrue(hasattr(user, "profile"))

    def test_user_registration_missing_fields(self):
        """TEST FAILURE: Ensure registration is rejected when required fields are missing from the payload."""
        response = self.client.post(self.register_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)

    def test_user_registration_throttling(self):
        """TEST FAILURE: Ensure the rate limiter (throttling) blocks excessive registration attempts."""
        for _ in range(3):
            data = {
                "email": self.faker.unique.email(),
                "password": self.user_data["password"],
                "confirm_password": self.user_data["password"],
            }
            self.client.post(self.register_url, data)
        data = {
            "email": self.faker.unique.email(),
            "password": self.user_data["password"],
            "confirm_password": self.user_data["password"],
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

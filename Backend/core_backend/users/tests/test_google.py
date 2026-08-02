from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from faker import Faker

CustomUser = get_user_model()


class GoogleLoginTest(APITestCase):
    """Test suite for Google OAuth2 Login."""

    def setUp(self):
        self.faker = Faker()
        self.google_login_url = reverse("google-login")
        self.existing_email = self.faker.unique.email()
        self.user = CustomUser.objects.create_user(
            email=self.existing_email,
            password=self.faker.password(
                length=12,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ),
        )
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()

    @patch("users.views.id_token.verify_oauth2_token")
    def test_google_login_success(self, mock_verify_token):
        """TEST SUCCESS: Google login returns JWT tokens for an existing user."""
        mock_verify_token.return_value = {
            "email": self.existing_email,
            "email_verified": True,
            "given_name": "Test",
            "family_name": "User",
        }
        data = {"token_id": "valid_google_id_token"}
        response = self.client.post(self.google_login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        self.assertFalse(response.data["is_new_user"])
        mock_verify_token.assert_called_once()

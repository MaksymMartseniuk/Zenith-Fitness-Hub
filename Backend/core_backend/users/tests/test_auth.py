from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from faker import Faker

CustomUser = get_user_model()


class AuthenticationTest(APITestCase):
    """Test suite for JWT authentication (login), token refresh, and logout."""

    def setUp(self):
        self.faker = Faker()
        self.

"""
Test for the language API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Language

from snippet.serializers import LanguageSerializer


LANGUAGE_URL = reverse('snippet:language-list')


def create_user(email='user@example.com', password='testpass123'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicSourceApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving sources."""
        res = self.client.get(LANGUAGE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLanguageApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_languages(self):
        """Test retrieving a list of languages."""

        Language.objects.create(
                user=self.user,
                name='java',
                style='default',
                linenos=True,
        )

        res = self.client.get(LANGUAGE_URL)

        languages = Language.objects.all().order_by('-name')
        serializer = LanguageSerializer(languages, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

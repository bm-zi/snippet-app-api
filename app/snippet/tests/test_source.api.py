"""
Test for the Source API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Source, Language

from snippet.serializers import SourceSerializer


SOURCE_URL = reverse('snippet:source-list')


def create_user(email='user@example.com', password='testpass123'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_language(name='python', style='default', linenos=True):
    """Create and return language object."""
    return Language.objects.create(
            user=create_user(),
            name=name,
            style=style,
            linenos=linenos,
        )


class PublicSourceApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving sources."""
        res = self.client.get(SOURCE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSourceApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_sources(self):
        """Test retrieving a list of sources."""
        language1 = create_language()
        language2 = create_language()
        Source.objects.create(
            user=self.user,
            code='code no 1',
            description='description for code 1',
            link='www.example.com/code_1',
            language=language1
        )
        Source.objects.create(
            user=self.user,
            code='code no 2',
            description='description for code 2',
            link='www.example.com/code_2',
            language=language2
        )

        res = self.client.get(SOURCE_URL)

        sources = Source.objects.all().order_by('-created')
        serializer = SourceSerializer(sources, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_sources_limited_to_user(self):
        """Test list of sources is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        language3 = create_language()
        language4 = create_language()
        Source.objects.create(
            user=user2,
            code='code for user2',
            description='description for code',
            link='www.example.com/somecode',
            language=language3,
        )
        source = Source.objects.create(
            user=self.user,
            code='code for user',
            description='description for code',
            link='www.example.com/code_sample',
            language=language4,
        )

        res = self.client.get(SOURCE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['code'], source.code)
        self.assertEqual(res.data[0]['id'], source.id)

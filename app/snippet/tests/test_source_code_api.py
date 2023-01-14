"""
Test for the Source API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import SourceCode
# from snippet.serializers import SourceCodeSerializer
from snippet.serializers import SourceCodeBriefSerializer


SOURCE_CODE_URL = reverse('snippet:sourcecode-list')


def detail_url(source_code_id):
    """Create and return a source code detail URL."""
    return reverse("snippet:sourcecode-detail", args=[source_code_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_source_code(user=None, title='title for sample snippet',
                       author='bm-zi',
                       code='''
                       var = 'Some variable'
                       print(var)
                       ''',
                       notes='This is a sample python test code.',
                       url='http://example.com/code_sample',
                       status='U',
                       rating=4,
                       is_favorite=False):
    """Create and return source code object."""
    return SourceCode.objects.create(user=user, title=title, author=author,
                                     code=code, notes=notes, url=url,
                                     status=status, rating=rating,
                                     is_favorite=is_favorite)


class PublicSourceApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving sources."""
        res = self.client.get(SOURCE_CODE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSourceApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_source_codes(self):
        """Test retrieving a list of source codes."""

        create_source_code(user=self.user, title="title 1", code="code 1")
        create_source_code(user=self.user, title="title 2", code="code 2")

        res = self.client.get(SOURCE_CODE_URL)

        source_codes = SourceCode.objects.all().order_by('-id')
        serializer = SourceCodeBriefSerializer(source_codes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_sources_limited_to_user(self):
        """Test list of sources is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        source_code_1 = create_source_code(user=self.user)
        create_source_code(user=user2, code='code for user2')

        res = self.client.get(SOURCE_CODE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], source_code_1.title)
        self.assertEqual(res.data[0]['id'], source_code_1.id)

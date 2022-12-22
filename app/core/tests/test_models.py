"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models."""
    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_snippet(self):
        """Test creating a snippet is successful"""
        user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        snippet = models.Snippet.objects.create(
            user=user,
            title='Sample snippet name',
            is_favorite=True,
        )
        self.assertEqual(str(snippet), snippet.title)

    def test_create_tag(self):
        """Test creating a tag successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")
        self.assertEqual(str(tag), tag.name)

    def test_create_language_object(self):
        user = create_user()
        language = models.Language.objects.create(
            user=user,
            name='java',
            style='default',
            linenos=False,
        )
        self.assertEqual(str(language), language.name)

    def test_create_snippet_with_source(self):
        """Test creating a snippet with source and language."""
        user = create_user()
        language = models.Language.objects.create(
            user=user,
            name='java',
            style='friendly',
            linenos=True,
        )
        self.assertEqual(str(language), language.name)
        source = models.Source.objects.create(
            user=user,
            code='code body content',
            description='description about using this source code',
            link='http://www.examplecom/source_code_sample',
            language=language,
        )
        self.assertEqual(str(source), source.description)
        snippet = models.Snippet.objects.create(
            user=user,
            title='Sample snippet with source code',
            is_favorite=True,
            source=source,
        )
        self.assertEqual(str(snippet), snippet.title)

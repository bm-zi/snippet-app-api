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
            language_name="python",
            style="default",
            linenos=False,
        )
        snippet_obj = "Snippet {}".format(snippet.id)
        self.assertEqual(str(snippet), snippet_obj)

    def test_create_tag(self):
        """Test creating a tag successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")
        self.assertEqual(str(tag), tag.name)

    def test_create_source_code(self):
        user = create_user()
        source_code = models.SourceCode.objects.create(
            user=user,
            title='title for sample snippet',
            author='bm-zi',
            code='''
            var = 'Some variable'
            print(var)
            ''',
            notes='This is a sample python test code.',
            url='http://example.com/code_sample',
            status='U',
            rating=4,
            is_favorite=False,
        )
        self.assertEqual(str(source_code), source_code.title)

    def test_create_snippet_with_source_code_and_tag(self):
        """Test creating a snippet with source and language."""
        user = create_user()
        source_code = models.SourceCode.objects.create(
            user=user,
            title='title for sample snippet',
            author='bm-zi',
            code='''
            var = 'Some variable'
            print(var)
            ''',
            notes='This is a sample python test code.',
            url='http://example.com/code_sample',
            status='U',
            rating=4,
            is_favorite=False,
        )
        self.assertEqual(str(source_code), source_code.title)

        tag1 = models.Tag.objects.create(user=user, name="Tag1")
        tag2 = models.Tag.objects.create(user=user, name="Tag2")
        self.assertEqual(str(tag1), tag1.name)
        self.assertEqual(str(tag2), tag2.name)

        snippet = models.Snippet.objects.create(
            user=user,
            language_name='python',
            style='friendly',
            linenos=True,
            source_code=source_code,
        )
        snippet.tags.set(models.Tag.objects.all())
        snippet_obj = "Snippet {}".format(snippet.id)
        self.assertEqual(str(snippet), snippet_obj)

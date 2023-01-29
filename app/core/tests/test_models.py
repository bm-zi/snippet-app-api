"""
Tests for models.
"""
from unittest.mock import patch
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
        """
        Test creating a snippet with given values to all fields in model
        Snippet and model SourceCode is successful.
        """
        user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        source_code = models.SourceCode.objects.create(
                user=user,
                title="my first code snippet",
                author="bm-zi",
                code="print('Hello world')",
                notes="Some notes for this code",
                url="http://example.com/first_code",
                status="C",
                rating=1,
                is_favorite=True
        )
        snippet = models.Snippet.objects.create(
            user=user,
            language_name="python",
            style="default",
            linenos=True,
            source_code=source_code
        )
        snippet_obj = "snippet {}".format(snippet.id)
        self.assertEqual(str(snippet), snippet_obj)

    def test_create_snippet_without_source_code(self):
        """
        Test creating snippet without source_code field
        is successful.
        """
        user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )

        self.assertTrue(
            models.Snippet.objects.create(
                user=user,
                language_name="python",
                style="default",
                linenos=True,
            )
        )

    def test_create_snippet_without_title_field(self):
        """
        Test creating snippet requires the field code from model
        SourceCode to have a value. The code field cannot be empty.
        """
        user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        source_code = models.SourceCode.objects.create(
                user=user,
                code="print('Hello world')",
        )
        snippet = models.Snippet.objects.create(
            user=user,
            language_name="python",
            style="default",
            linenos=True,
            source_code=source_code
        )
        snippet_obj = "snippet {}".format(snippet.id)
        self.assertEqual(str(snippet), snippet_obj)

    def test_create_snippet_with_blank_title(self):
        """
        Test creating snippet with no value for title field in model
        SourceCode, generates a value automatically.

        Also testing for a second snippet with no value for title,
        the genrated title will be different from the title in first
        snippet.
        """
        user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        source_code = models.SourceCode.objects.create(
                user=user,
                title="",
                code="code block with no title",
        )
        snippet = models.Snippet.objects.create(
            user=user,
            language_name="python",
            style="default",
            linenos=True,
            source_code=source_code
        )

        self.assertTrue(snippet)

        snippet_obj = "snippet {}".format(snippet.id)
        self.assertEqual(str(snippet), snippet_obj)
        self.assertEqual(snippet.source_code.title, source_code.title)

        source_code2 = models.SourceCode.objects.create(
                user=user,
                title="",
                code="second code block with no title",
        )
        snippet2 = models.Snippet.objects.create(
            user=user,
            language_name="java",
            style="colorful",
            linenos=True,
            source_code=source_code2
        )
        self.assertEqual(snippet2.source_code.title, source_code2.title)

    def test_create_snippets_with_same_code(self):
        """
        Testing when two snippets have the same code fails.
        """
        user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        source_code = models.SourceCode.objects.create(
                user=user,
                code="code block",
        )
        snippet = models.Snippet.objects.create(
            user=user,
            source_code=source_code
        )
        snippet_obj = "snippet {}".format(snippet.id)
        self.assertEqual(str(snippet), snippet_obj)
        count = models.Snippet.objects.filter(source_code=source_code).count()
        self.assertEqual(count, 1)

    def test_create_source_code(self):
        """
        Test create a source code with given values to all fields,
        Fields modified, created and count_updated are not required.
        """
        user = create_user()
        source_code = models.SourceCode.objects.create(
            user=user,
            title='title for sample snippet',
            author='bm-zi',
            code="""
            var = 'Some variable'
            print(var)
            """,
            notes='This is a sample python test code.',
            url='http://example.com/code_sample',
            status='U',
            rating=4,
            is_favorite=False,
        )
        self.assertEqual(str(source_code), source_code.title)

    def test_create_source_code_without_any_fields_value(self):
        """
        Testing create a source code with no given values to
        the all fields (except user and code content fields) fails.
        """
        user = create_user()
        source_code = models.SourceCode.objects.create(
                user=user,
                code="Some code"
            )
        self.assertTrue(str(source_code), source_code.__str__)

    def test_create_tag(self):
        """Test creating a tag successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")
        self.assertEqual(str(tag), tag.name)

    def test_create_snippet_with_source_code_and_tag(self):
        """Test creating a snippet with source code and tags."""
        user = create_user()
        source_code = models.SourceCode.objects.create(
            user=user,
            title='title for sample snippet',
            author='bm-zi',
            code="""
            var = 'Some variable'
            print(var)
            """,
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
        snippet_obj = "snippet {}".format(snippet.id)
        self.assertEqual(str(snippet), snippet_obj)

    @patch('core.models.uuid.uuid4')
    def test_snippet_file_name_uuid(self, mock_uuid):
        """Test genrating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.snippet_image_file_path(None, 'example.jpg')
        self.assertEqual(file_path, f'uploads/snippet/{uuid}.jpg')

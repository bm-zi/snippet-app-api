"""
Tests for snippet APIs
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Snippet, Tag

from snippet.serializers import (
    SnippetSerializer,
    SnippetDetailSerializer,
)


SNIPPETS_URL = reverse('snippet:snippet-list')


def detail_url(snippet_id):
    """Create and retrieve a snippet detail url"""
    return reverse('snippet:snippet-detail', args=[snippet_id])


def create_snippet(user, **params):
    """Create and return a sample snippet"""
    defaults = {
        'language_name': 'python',
        'style': 'colorful',
        'linenos': True,
    }
    defaults.update(params)

    snippet = Snippet.objects.create(user=user, **defaults)
    return snippet


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicSnippetApiTests(TestCase):
    """Test unauthenticated API requests"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to call API."""
        res = self.client.get(SNIPPETS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSnippetApiTests(TestCase):
    """Test authenticated API requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_snippets(self):
        """Test retrieve a list of snippets."""
        create_snippet(user=self.user)
        create_snippet(user=self.user)

        res = self.client.get(SNIPPETS_URL)

        snippets = Snippet.objects.all().order_by('-id')
        serializer = SnippetSerializer(snippets, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_snippet_list_limited_to_user(self):
        """Test list of snippets is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='test123')
        create_snippet(user=other_user)
        create_snippet(user=self.user)

        res = self.client.get(SNIPPETS_URL)

        snippets = Snippet.objects.filter(user=self.user)
        serializer = SnippetSerializer(snippets, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_snippet_detail(self):
        """Test get snippet detail."""
        snippet = create_snippet(user=self.user)
        url = detail_url(snippet.id)
        res = self.client.get(url)

        serializer = SnippetDetailSerializer(snippet)
        self.assertEqual(res.data, serializer.data)

    '''def test_create_snippet(self):
        """Test creating a snippet."""
        payload = {
            'user': self.user,
            "language_name": "java",
            "style": "default",
            "linenos": True,
        }
        res = self.client.post(SNIPPETS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        snippet = Snippet.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(snippet, k), v)

        self.assertEqual(snippet.user, self.user)

    def test_partial_update(self):
        """Test partial update of a snippet"""

        snippet = create_snippet(
            user=self.user,
            title='Sample snippet title',
        )

        payload = {'title': 'New Snippet title'}
        url = detail_url(snippet.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        snippet.refresh_from_db()
        self.assertEqual(snippet.title, payload['title'])

        self.assertEqual(snippet.user, self.user)

    def test_full_update(self):
        """Test full update of snippet."""
        snippet = create_snippet(
            user=self.user,
            title="original snippet title",
        )
        payload = {
            'title': "modified snippet title",
            'is_favorite': False
        }

        url = detail_url(snippet.id)
        res = self.client.put(url, payload)

        snippet.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for k, v in payload.items():
            self.assertEqual(getattr(snippet, k), v)
        self.assertEqual(snippet.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the snippet user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        snippet = create_snippet(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(snippet.id)
        self.client.patch(url, payload)

        snippet.refresh_from_db()
        self.assertEqual(snippet.user, self.user)

    def test_delete_snippet(self):
        """Test deleting a snippet is successful."""
        snippet = create_snippet(user=self.user)

        url = detail_url(snippet.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Snippet.objects.filter(id=snippet.id).exists())

    def test_delete_other_users_snippet_error(self):
        """Test trying deleting another users snippet gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        snippet = create_snippet(user=new_user)

        url = detail_url(snippet.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Snippet.objects.filter(id=snippet.id).exists())

    def test_create_snippet_with_new_tags(self):
        """Test creating snippet with a new tags."""
        payload = {
            'title': "sample snippet with new tag",
            'is_favorite': True,
            'tags': [{'name': 'web scraping'}, {'name': 'web crawling'}],
        }
        res = self.client.post(SNIPPETS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        snippets = Snippet.objects.filter(user=self.user)
        self.assertEqual(snippets.count(), 1)
        snippet = snippets[0]
        self.assertEqual(snippet.tags.count(), 2)
        for tag in payload['tags']:
            exists = snippet.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_snippet_with_existing_tags(self):
        """Test creating a snippet with existing tag."""
        tag_orm = Tag.objects.create(user=self.user, name='orm')
        payload = {
            'title': "sample snippet with existing tags",
            'is_favorite': False,
            'tags': [{'name': 'databse'}, {'name': 'orm'}],
        }
        res = self.client.post(SNIPPETS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        snippets = Snippet.objects.filter(user=self.user)
        self.assertEqual(snippets.count(), 1)
        snippet = snippets[0]
        self.assertEqual(snippet.tags.count(), 2)
        self.assertIn(tag_orm, snippet.tags.all())
        for tag in payload['tags']:
            exists = snippet.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test create tag when updating a snippet."""
        snippet = create_snippet(user=self.user)

        payload = {'tags': [{'name': 'web surfing'}]}
        url = detail_url(snippet.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='web surfing')
        self.assertIn(new_tag, snippet.tags.all())

    def test_update_snippet_assign_tag(self):
        """Test assigning an existing tag when updating a snippet."""
        tag_OOP = Tag.objects.create(user=self.user, name='OOP')
        snippet = create_snippet(user=self.user)
        snippet.tags.add(tag_OOP)

        tag_RDBS = Tag.objects.create(user=self.user, name='RDBS')
        payload = {'tags': [{'name': 'RDBS'}]}
        url = detail_url(snippet.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_RDBS, snippet.tags.all())
        self.assertNotIn(tag_OOP, snippet.tags.all())

    def test_clear_snippet_tags(self):
        """Test clearing a snippet's tag"""
        tag = Tag.objects.create(user=self.user, name='RESTful')
        snippet = create_snippet(user=self.user)
        snippet.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(snippet.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(snippet.tags.count(), 0)

    def test_create_snippet_with_no_title(self):
        """Testing creating snippet when title is empty"""
        snippet = Snippet.objects.create(
            user=self.user,
            is_favorite=True,
        )
        url = detail_url(snippet.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], snippet.title)

    def test_updating_snippet_with_empty_title(self):
        """Test updating an snippet with empty title"""
        snippet = create_snippet(user=self.user)
        payload = {
            'user': self.user,
            'title': '',
        }

        url = detail_url(snippet.id)
        res = self.client.put(url, payload)
        snippet.refresh_from_db()
        snippet = Snippet.objects.get(id=snippet.id)
        self.assertEqual(res.data['title'], snippet.title)

        snippet2 = create_snippet(user=self.user, title='snippet2')
        payload = {'title': '', 'is_favorite': True}
        url = detail_url(snippet2.id)
        res = self.client.patch(url, payload, format='json')
        snippet2.refresh_from_db()
        self.assertEqual(res.data['title'], snippet2.title)

    def test_creating_multiple_snippets_with_no_title(self):
        """Test creating multiple snippets with no title"""
        snippet3 = create_snippet(user=self.user, title='')
        test_string = snippet3.title
        no = [int(i) for i in test_string.split() if i.isdigit()][0]

        snippet4 = create_snippet(user=self.user, title='')
        self.assertEqual(snippet4.title, f'Snippet no {no+1}')

        snippet5 = create_snippet(user=self.user, title='')
        self.assertEqual(snippet5.title, f'Snippet no {no+2}')'''

"""
Views for the snippet APIs
"""
from django.db import connection
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Snippet, Tag
from snippet import serializers


class SnippetViewSet(viewsets.ModelViewSet):
    """View for manage snippet APIs."""
    serializer_class = serializers.SnippetDetailSerializer
    queryset = Snippet.objects.all()
    # serializer_class and queryset are from class GenericAPIView
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve snippets for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.SnippetSerializer

        return self.serializer_class

    def get_latest_id(self):
        try:
            query = 'SELECT * FROM core_snippet'
            cursor = connection.cursor()
            cursor.execute(query)
            row_no = len(cursor.fetchall()) + 1
            return str(row_no)
        except Exception:
            return str('1')

    def perform_create(self, serializer):
        """Create a new snippet"""
        if not serializer.validated_data['title']:
            serializer.validated_data['title'] = \
                f"Snippet No. {self.get_latest_id()}"
        serializer.save(user=self.request.user)


class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter querysett to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')

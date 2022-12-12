"""
Serializer for snippet API
"""

from rest_framework import serializers
from core.models import Snippet


class SnippetSerializer(serializers.ModelSerializer):
    """Serializer for snippets"""

    class Meta:
        model = Snippet
        fields = ['id', 'title', 'language']
        read_only_fields = ['id']


class SnippetDetailSerializer(SnippetSerializer):
    """Serializer for a snippet detail."""

    class Meta(SnippetSerializer.Meta):
        fields = SnippetSerializer.Meta.fields + [
            'linenos', 'style', 'created',
            'modified', 'is_favorite',
        ]

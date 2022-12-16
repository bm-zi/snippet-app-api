"""
Serializer for snippet API
"""

from rest_framework import serializers
from core.models import Snippet, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class SnippetSerializer(serializers.ModelSerializer):
    """Serializer for snippets"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Snippet
        fields = ['id', 'title', 'language', 'tags']
        read_only_fields = ['id']


class SnippetDetailSerializer(SnippetSerializer):
    """Serializer for a snippet detail view."""

    class Meta(SnippetSerializer.Meta):
        fields = SnippetSerializer.Meta.fields + [
            'linenos', 'style', 'created',
            'modified', 'is_favorite',
        ]

    def create(self, validated_data):
        """Create a snippet"""
        tags = validated_data.pop('tags', [])   # ['tag1', 'tag2']
        snippet = Snippet.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            snippet.tags.add(tag_obj)

        return snippet

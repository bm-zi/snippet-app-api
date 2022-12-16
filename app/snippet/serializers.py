"""
Serializer for snippet API
"""

from rest_framework import serializers
from core.models import (
    Snippet,
    Tag,
)


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

    def _get_or_create_tags(self, tags, snippet):
        """
        Handle adding tags to a given snippet while
        creating or updating that snippet.
        """
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            snippet.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a snippet"""
        tags = validated_data.pop('tags', [])   # ['tag1', 'tag2']
        snippet = Snippet.objects.create(**validated_data)
        self._get_or_create_tags(tags, snippet)

        return snippet

    def update(self, instance, validated_data):
        """Update a snippet."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

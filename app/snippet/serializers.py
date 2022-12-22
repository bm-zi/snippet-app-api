"""
Serializer for snippet API
"""

from rest_framework import serializers
from core.models import (
    Snippet,
    Tag,
    Language,
    Source,
)


class LanguageSerializer(serializers.ModelSerializer):
    """Serializer for Languages."""

    class Meta:
        model = Language
        fields = ['id', 'user', 'name', 'style', 'linenos']
        read_only_fields = ['id']


class SourceSerializer(serializers.ModelSerializer):
    """Serializer for Sources."""
    language = LanguageSerializer(many=True, required=True)

    class Meta:
        model = Source
        fields = [
            'id', 'user', 'code', 'description', 'language',
            'link', 'created', 'modified',
        ]
        read_only_fields = ['id']


class SourceDetailSerializer(SourceSerializer):
    """Serializer for source detail view."""

    def _get_or_create_language(self, language, source):
        """
        Handle adding language to a given source while
        creating or updating that snippet.
        """
        auth_user = self.context['request'].user
        language_obj, created = Language.objects.get_or_create(
                user=auth_user,
                language=language,
            )
        source.language = language_obj

    def create(self, validated_data):
        """Create a snippet"""
        language = validated_data.pop('language', None)
        source = Source.objects.create(**validated_data)
        if language is not None:
            self._get_or_create_language(language, source)

        return source

    def update(self, instance, validated_data):
        """Update a snippet."""
        language = validated_data.pop('languege', None)
        if language is not None:
            instance.language.clear()
            self._get_or_create_language(language, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class SnippetSerializer(serializers.ModelSerializer):
    """Serializer for snippets"""
    tags = TagSerializer(many=True, required=False)
    sources = SourceSerializer(many=True, required=False)

    class Meta:
        model = Snippet
        fields = ['id', 'title', 'tags', 'is_favorite']
        read_only_fields = ['id']


class SnippetDetailSerializer(SnippetSerializer):
    """Serializer for a snippet detail view."""

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

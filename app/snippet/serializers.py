"""
Serializer for snippet API
"""

from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

from rest_framework import serializers
from core.models import (
    Snippet,
    Tag,
    SourceCode,
)


class SourceCodeSerializer(serializers.ModelSerializer):
    """Serializer for source code."""

    class Meta:
        model = SourceCode
        fields = [
            'id', 'title', 'author', 'code', 'notes', 'url',
            'status', 'rating', 'is_favorite', 'count_updated',
            'created', 'modified',
        ]
        read_only_fields = ['id']


class SourceCodeTitleSerializer(SourceCodeSerializer):
    """Serializer for source code title"""
    
    summary = serializers.SerializerMethodField()
    def get_summary(self, obj):
        if len(obj.code) > 60:
            return obj.code[:60] + " ..."
        return obj.code

    class Meta(SourceCodeSerializer.Meta):
        fields = ['id', 'title', 'summary']

    
    # code = serializers.SerializerMethodField()
    def validate_code(self):
        return self.code[:4]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class SnippetSerializer(serializers.ModelSerializer):
    """Serializer for snippets"""
    tags = TagSerializer(many=True, required=False)
    source_code = SourceCodeTitleSerializer(required=False)

    class Meta:
        model = Snippet
        fields = [
            'id', 'source_code', 'language_name',
            'style', 'linenos', 'tags'
        ]
        read_only_fields = ['id']


class SnippetDetailSerializer(serializers.ModelSerializer):
    """Serializer for snippet detail view."""
    tags = TagSerializer(many=True, required=False)
    source_code = SourceCodeSerializer(required=False)

    class Meta:
        model = Snippet
        fields = [
            'id', 'language_name', 'style', 'linenos',
            'highlighted', 'source_code', 'tags'
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, snippet_object):
        """Handle adding tags to snippet object."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            snippet_object.tags.add(tag_obj)

    def _get_or_create_source_code(self, source_code_dict, snippet_object):
        """Handle adding source code to snippet."""
        auth_user = self.context['request'].user
        source_code_obj, created = SourceCode.objects.get_or_create(
            user=auth_user,
            title=source_code_dict['title'],
            author=source_code_dict['author'],
            code=source_code_dict['code'],
            notes=source_code_dict['notes'],
            url=source_code_dict['url'],
            status=source_code_dict['status'],
            rating=source_code_dict['rating'],
            is_favorite=source_code_dict['is_favorite']
        )
        snippet_object.source_code = source_code_obj

    def _create_highlighted(self, source_code_dict):
        """Creates a highlighted snippet"""
        self.title = source_code_dict['title']
        self.code = source_code_dict['code']
        self.language_name = self.validated_data['language_name']
        self.style = self.validated_data['style']
        self.linenos = self.validated_data['linenos']

        lexer = get_lexer_by_name(self.language_name)
        linenos = 'table' if self.linenos else False
        options = {'title': self.title} if self.title else {}
        formatter = HtmlFormatter(
            style=self.style,
            linenos=linenos,
            full=True,
            **options
        )
        self.highlighted = highlight(self.code, lexer, formatter)

        return self.highlighted

    def create(self, validated_data):
        """Create a snippet"""
        user = self.context['request'].user
        tags = validated_data.pop('tags', [])
        source_code = validated_data.pop('source_code', None)
        snippet = Snippet.objects.create(**validated_data)
        self._get_or_create_tags(tags, snippet)
        self._get_or_create_source_code(source_code, snippet)
        snippet.highlighted = self._create_highlighted(source_code)
        snippet.user = user

        snippet.save()
        return snippet

    def update(self, instance, validated_data):
        """Update a snippet."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        source_code = validated_data.pop('source_code', None)
        if source_code is not None:
            self._get_or_create_source_code(source_code, instance)

        auth_user = self.context['request'].user
        instance.user = auth_user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def _get_code_field_data(self):
        """Get information for field code"""
        return self.validated_data.get('code')

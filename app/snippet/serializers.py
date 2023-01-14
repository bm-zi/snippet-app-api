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
            'id', 'title', 'code', 'notes', 'url', 'author',
            'status', 'rating', 'is_favorite', 'count_updated',
            'created', 'modified',
        ]
        read_only_fields = ['id', 'created', 'modified']


class SourceCodeBriefSerializer(SourceCodeSerializer):
    """Serializer for source code title"""

    code_content_summary = serializers.SerializerMethodField()
    related_snippet_id = serializers.SerializerMethodField()

    def get_code_content_summary(self, obj):
        if len(obj.code) > 50:
            return obj.code[:50] + " ..."
        return obj.code

    def get_related_snippet_id(self, obj):
        return Snippet.objects.filter(source_code__id=obj.id).first().id

    class Meta(SourceCodeSerializer.Meta):
        fields = ['id', 'title', 'code_content_summary', 'related_snippet_id']
        read_only_fields = ['id', 'related_snippet_id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class SnippetSerializer(serializers.ModelSerializer):
    """Serializer for snippets"""
    tags = TagSerializer(many=True, required=False)
    source_code = SourceCodeBriefSerializer(required=False)

    class Meta:
        model = Snippet
        fields = [
            'id', 'language_name', 'style',
            'tags', 'linenos', 'source_code',
        ]
        read_only_fields = ['id']


class SnippetDetailSerializer(serializers.ModelSerializer):
    """Serializer for snippet detail view."""
    tags = TagSerializer(many=True, required=False)
    source_code = SourceCodeSerializer(required=False)

    class Meta:
        model = Snippet
        fields = [
            'id', 'source_code', 'tags', 'language_name',
            'style', 'linenos', 'highlighted',
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

        if 'title' in source_code_dict.keys():
            title = source_code_dict['title']
        else:
            title = ''

        if 'code' in source_code_dict.keys():
            code = source_code_dict['code']
        else:
            code = ''

        if 'notes' in source_code_dict.keys():
            notes = source_code_dict['notes']
        else:
            notes = ''

        if 'url' in source_code_dict.keys():
            url = source_code_dict['url']
        else:
            url = ''

        if 'author' in source_code_dict.keys():
            author = source_code_dict['author']
        else:
            author = ''

        if 'status' in source_code_dict.keys():
            status = source_code_dict['status']
        else:
            status = 'U'

        if 'rating' in source_code_dict.keys():
            rating = source_code_dict['rating']
        else:
            rating = 3

        if 'is_favorite' in source_code_dict.keys():
            is_favorite = source_code_dict['is_favorite']
        else:
            is_favorite = False

        source_code_obj = SourceCode.objects.create(
            user=auth_user,
            title=title,
            code=code,
            notes=notes,
            url=url,
            author=author,
            status=status,
            rating=rating,
            is_favorite=is_favorite
        )
        snippet_object.source_code = source_code_obj

    def _get_latest_id(self):
        try:
            row_no = Snippet.objects.filter(user=self.request.user).count()
            return f"snippet no {row_no+1}"
        except Exception:
            return str('snippet no 1')

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

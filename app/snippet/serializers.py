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
    SourceCode
)


class SourceCodeSerializer(serializers.ModelSerializer):
    """Serializer for source code details."""
    # title = serializers.CharField(default="Title not set!")
    notes = serializers.CharField(allow_null=True)
    url = serializers.URLField(allow_null=True)

    class Meta:
        model = SourceCode
        fields = [
            'id', 'title', 'code', 'notes', 'url', 'author',
            'status', 'rating', 'is_favorite', 'count_updated',
            'created', 'modified',
        ]
        read_only_fields = [
            'id', 'count_updated', 'created', 'modified'
            ]


class SourceCodeBriefSerializer(serializers.ModelSerializer):
    """Serializer displsys source codes in brief"""

    code_summary = serializers.SerializerMethodField()
    snippet_id = serializers.SerializerMethodField()

    def get_code_summary(self, obj):
        if len(obj.code) > 50:
            return obj.code[:50] + " ..."
        return obj.code

    def get_snippet_id(self, obj):
        snippet = Snippet.objects.filter(source_code__id=obj.id).first()
        if snippet:
            return snippet.id
        return

    class Meta:
        model = SourceCode
        fields = ['id', 'title', 'code_summary', 'snippet_id']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class SnippetSerializer(serializers.ModelSerializer):
    """Serializer for snippets"""

    source_code = SourceCodeBriefSerializer()

    class Meta:
        model = Snippet
        fields = ['language_name', 'source_code']


class SnippetDetailSerializer(serializers.ModelSerializer):
    """Serializer for snippet detail view."""
    # current_user = serializers.SerializerMethodField('_user')

    language_name = serializers.CharField(default='python')
    style = serializers.CharField(default='default')
    linenos = serializers.BooleanField(default=False)

    tags = TagSerializer(many=True, required=False)
    source_code = SourceCodeSerializer(required=False)

    class Meta:
        model = Snippet
        fields = [
            'id', 'language_name', 'style', 'linenos',
            'highlighted', 'tags', 'source_code',
        ]
        read_only_fields = ['id', 'highlighted']

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
            is_favorite=is_favorite,
        )
        source_code_obj.save()
        snippet_object.source_code = source_code_obj

    def _get_latest_id(self):
        try:
            row_no = Snippet.objects.filter(user=self.request.user).count()
            return f"snippet no {row_no+1}"
        except Exception:
            return str('snippet no 1')

    def _create_highlighted(self, source_code_obj):
        """Creates a highlighted snippet"""

        self.title = source_code_obj.title
        self.code = source_code_obj.code
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
        source_code = validated_data.pop('source_code')
        source_code, created = SourceCode.objects.get_or_create(user=user,
                                                                **source_code)
        if not created:
            source_code.save()
        snippet = Snippet.objects.create(user=user, source_code=source_code)
        self._get_or_create_tags(tags, snippet)
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

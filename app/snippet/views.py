"""
Views for the snippet APIs
"""

from rest_framework import authentication
from rest_framework import permissions
from rest_framework import viewsets, mixins
from core.models import Snippet, Tag, SourceCode
from snippet import serializers


class SnippetViewSet(viewsets.ModelViewSet):
    """View for manage snippet APIs."""
    serializer_class = serializers.SnippetDetailSerializer
    queryset = Snippet.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieve snippets for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.SnippetSerializer

        return self.serializer_class

    def get_latest_id(self):
        # try:
        #     query = 'SELECT COUNT(*) FROM core_snippet'
        #     cursor = connection.cursor()
        #     cursor.execute(query)
        #     # row_no = len(cursor.fetchall()) + 1
        #     row_no = int(cursor.fetchall()[0][0]) + 1
        # except Exception:
        #     return str('Snippet no 1')
        try:
            row_no = Snippet.objects.filter(user=self.request.user).count()
            return f"Snippet no {row_no+1}"
        except Exception:
            return str('Snippet no 1')

    def perform_create(self, serializer):
        """Create a new snippet"""
        latest_snippet = self.get_latest_id()
        if not serializer.validated_data['source_code']['title']:
            serializer.validated_data['source_code'].update(
                {'title': latest_snippet}
            )
            source_code = serializer.validated_data['source_code']
            serializer.validated_data.update({'source_code': source_code})

        user = serializer.context['request'].user
        serializer.validated_data.update({'user': user})
        serializer.save()
        return serializer


class BaseSnippetAttrViewSet(viewsets.ModelViewSet):
    """Base viewset for recipe attributes."""



class TagViewSet(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin, 
                mixins.UpdateModelMixin,
                mixins.DestroyModelMixin,
                mixins.ListModelMixin,
                viewsets.GenericViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')


class SourceCodeViewSet(mixins.RetrieveModelMixin, 
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """Manage sources in the database."""
    serializer_class = serializers.SourceCodeSerializer
    queryset = SourceCode.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retrieve source code for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.SourceCodeTitleSerializer

        return self.serializer_class

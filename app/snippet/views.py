"""
Views for the snippet APIs
"""
from rest_framework import (
    authentication,
    permissions,
    viewsets,
    mixins,
    status
)
from rest_framework.response import Response
from rest_framework.decorators import action

from core.models import Snippet, Tag, SourceCode
from snippet import serializers
from django.http import Http404


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
        elif self.action == 'upload_image':
            return serializers.SnippetImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Snippet."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to snippet."""
        snippet = self.get_object()
        serializer = self.get_serializer(snippet, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.source_code:
                SourceCode.objects.get(
                    id=instance.source_code.id).delete()
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(mixins.RetrieveModelMixin,
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
            return serializers.SourceCodeBriefSerializer
        return self.serializer_class

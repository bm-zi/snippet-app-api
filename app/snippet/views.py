"""
Views for the snippet APIs
"""
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import viewsets, mixins
from core.models import Snippet, Tag, SourceCode
from snippet import serializers
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status


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

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # source_code_exists = SourceCode.objects.filter(
            #     id=instance.source_code).exists()
            # if source_code_exists:
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

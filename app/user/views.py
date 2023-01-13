"""
Views for the user API.
"""
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import (
    generics, authentication, permissions,
    mixins, viewsets
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class ListUsersView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()

    def get_queryset(self):
        """Filter querysett to authenticated user."""
        return self.queryset.all().order_by('-id')

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = [user.username for user in get_user_model().objects.all()]
        return Response(usernames)

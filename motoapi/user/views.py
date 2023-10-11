"""
Views for user API.
"""

from rest_framework import generics, authentication, permissions
from user.serializers import AuthTokenSerializer, UserSerializer
from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken


class ManagerUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return authenticated user."""
        return self.request.user


class AuthTokenCreateView(ObtainAuthToken):
    """Creates new token for validated user."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Settings
from .serializers import SettingsSerializer


class SettingsViewSet(viewsets.GenericViewSet):
    serializer_class = SettingsSerializer

    def get_object(self):
        return Settings.get_settings()

    def list(self, request):
        settings = self.get_object()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        settings = self.get_object()
        serializer = self.get_serializer(settings, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def update_statistics(self, request):
        settings = self.get_object()
        settings.update_statistics()
        serializer = self.get_serializer(settings)
        return Response(serializer.data)

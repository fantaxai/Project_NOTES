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

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Статистика по идеям дня"""
        user_id = get_user_id(request)
        total_candidates = Note.objects.filter(is_idea_candidate=True, user_id=user_id).count()
        shown_count = Note.objects.filter(
            is_idea_candidate=True, shown_as_idea=True, user_id=user_id
        ).count()
        unshown_count = total_candidates - shown_count

        return Response({
            "total_candidates": total_candidates,
            "shown_count": shown_count,
            "unshown_count": unshown_count,
            "can_generate": total_candidates >= 20,
            "needs_reset": shown_count >= total_candidates and total_candidates >= 20,
        })

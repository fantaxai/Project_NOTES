from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from note.models import Note

from .models import File
from .serializers import FileCreateSerializer, FileSerializer


class FileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Только файлы заметок текущего пользователя
        return File.objects.filter(
            note__user=self.request.user
        ).order_by("-creation_date")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return FileCreateSerializer
        return FileSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        if not instance.format and instance.name:
            ext = instance.name.split(".")[-1].lower()
            if ext in ["pdf", "png", "jpg", "jpeg", "txt"]:
                instance.format = ext
                instance.save()

    @action(detail=False, methods=["get"])
    def by_note(self, request):
        note_id = request.query_params.get("note_id")
        if not note_id:
            return Response(
                {"error": "Параметр note_id обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Фильтруем по пользователю — чужую заметку не отдаём
            note = Note.objects.get(id=note_id, user=request.user)
            files = self.get_queryset().filter(note=note)
            serializer = self.get_serializer(files, many=True)
            return Response(
                {
                    "note_id": note_id,
                    "note_title": note.title,
                    "count": files.count(),
                    "files": serializer.data,
                }
            )
        except Note.DoesNotExist:
            return Response(
                {"error": f"Заметка с id {note_id} не найдена"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"])
    def by_format(self, request):
        file_format = request.query_params.get("format")
        if not file_format:
            return Response(
                {"error": "Параметр format обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        files = self.get_queryset().filter(format=file_format.lower())
        serializer = self.get_serializer(files, many=True)
        return Response({"format": file_format, "count": files.count(), "files": serializer.data})

    @action(detail=True, methods=["get"])
    def download_info(self, request, pk=None):
        file = self.get_object()
        return Response(
            {
                "id": file.id,
                "name": file.name,
                "size": file.size,
                "size_mb": round(file.size / (1024 * 1024), 2) if file.size else 0,
                "format": file.format,
                "creation_date": file.creation_date,
                "note_title": file.note.title if file.note else None,
            }
        )

    @action(detail=True, methods=["post"])
    def update_thumbnail(self, request, pk=None):
        file = self.get_object()
        thumbnail_url = request.data.get("thumbnail")

        if not thumbnail_url:
            return Response(
                {"error": "Поле thumbnail обязательно"}, status=status.HTTP_400_BAD_REQUEST
            )

        file.thumbnail = thumbnail_url
        file.save()

        serializer = self.get_serializer(file)
        return Response(
            {"status": "success", "message": "Миниатюра обновлена", "data": serializer.data}
        )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        total_files = self.get_queryset().count()
        total_size = self.get_queryset().aggregate(total=Sum("size"))["total"] or 0
        formats_stats = {}
        for file_format in ["pdf", "png", "jpg", "jpeg", "txt"]:
            count = self.get_queryset().filter(format=file_format).count()
            if count > 0:
                formats_stats[file_format] = count

        return Response(
            {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "formats": formats_stats,
                "average_size_mb": (
                    round(total_size / total_files / (1024 * 1024), 2) if total_files > 0 else 0
                ),
            }
        )

    @action(detail=False, methods=["delete"])
    def clear_old_files(self, request):
        from datetime import timedelta
        from django.utils import timezone

        days = int(request.data.get("days", 30))
        threshold_date = timezone.now().date() - timedelta(days=days)

        old_files = self.get_queryset().filter(creation_date__lt=threshold_date)
        count = old_files.count()
        old_files.delete()

        return Response(
            {"status": "success", "message": f"Удалено {count} файлов старше {days} дней"}
        )

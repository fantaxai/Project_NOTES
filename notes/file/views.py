import base64
import os
from io import BytesIO

from django.core.files.base import ContentFile
from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from note.models import Note
from .models import File, Format
from .serializers import FileCreateSerializer, FileSerializer


class FileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = File.objects.all().order_by("-creation_date")

    def get_queryset(self):
        """Фильтруем файлы по пользователю"""
        return File.objects.filter(note__user=self.request.user).order_by("-creation_date")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return FileCreateSerializer
        return FileSerializer

    def create(self, request, *args, **kwargs):
        """Создание файла с загрузкой base64 данных"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file_data_base64 = request.data.get('file_data')
        name = request.data.get('name')
        
        if file_data_base64:
            # Декодируем base64 в файл
            format, imgstr = file_data_base64.split(';base64,')
            ext = name.split('.')[-1].lower()
            
            file_content = ContentFile(
                base64.b64decode(imgstr),
                name=name
            )
            
            file_obj = File(
                name=name,
                file=file_content,
                size=request.data.get('size', len(file_content)),
                format=ext,
                note_id=request.data.get('note')
            )
            
            if request.data.get('thumbnail'):
                file_obj.thumbnail = request.data.get('thumbnail')
            
            file_obj.save()
            
            return Response(FileSerializer(file_obj).data, status=status.HTTP_201_CREATED)
        
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def by_note(self, request):
        note_id = request.query_params.get("note_id")
        if not note_id:
            return Response(
                {"error": "Параметр note_id обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            note = Note.objects.get(id=note_id, user=request.user)
            files = self.get_queryset().filter(note=note)
            serializer = self.get_serializer(files, many=True)
            return Response({
                "note_id": note_id,
                "note_title": note.title,
                "count": files.count(),
                "files": serializer.data,
            })
        except Note.DoesNotExist:
            return Response(
                {"error": f"Заметка с id {note_id} не найдена"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["get"])
    def serve(self, request, pk=None):
        """Отдать файл для просмотра"""
        file_obj = get_object_or_404(File, id=pk, note__user=request.user)
        
        if not file_obj.file:
            raise Http404("Файл не найден")
        
        # Открываем файл и отдаем
        file_path = file_obj.file.path
        
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            
            # Определяем Content-Type
            content_types = {
                'pdf': 'application/pdf',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'txt': 'text/plain',
            }
            
            response['Content-Type'] = content_types.get(file_obj.format, 'application/octet-stream')
            
            # Для PDF и изображений - просмотр в браузере
            if file_obj.format in ['pdf', 'jpg', 'jpeg', 'png']:
                response['Content-Disposition'] = f'inline; filename="{file_obj.name}"'
            else:
                response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
            
            return response
        
        raise Http404("Файл не найден")
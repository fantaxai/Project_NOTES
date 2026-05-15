from django.db import models
from django.conf import settings
import os


class Format(models.TextChoices):
    PDF = "pdf", "PDF"
    PNG = "png", "PNG"
    JPG = "jpg", "JPG"
    JPEG = "jpeg", "JPEG"
    TXT = "txt", "TXT"


def get_upload_path(instance, filename):
    """Генерация пути для загрузки файла"""
    return f'note_files/{instance.note_id}/{filename}'


class File(models.Model):
    name = models.CharField(verbose_name="Название файла", max_length=200)
    file = models.FileField(
        verbose_name="Файл",
        upload_to=get_upload_path,
        max_length=500,
        null=True,
        blank=True
    )
    thumbnail = models.CharField(verbose_name="Миниатюра", max_length=500, blank=True, null=True)
    size = models.IntegerField(verbose_name="Размер файла (в байтах)")
    format = models.CharField(verbose_name="Формат файла", max_length=10, choices=Format.choices)
    note = models.ForeignKey(
        "note.Note", on_delete=models.CASCADE, verbose_name="Заметка", related_name="files"
    )
    creation_date = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    
    @property
    def file_url(self):
        """Получить URL файла для просмотра"""
        if self.file:
            return f'/api/files/{self.id}/serve/'
        return None
    
    def __str__(self):
        return self.name
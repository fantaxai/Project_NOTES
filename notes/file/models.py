from django.db import models


class Format(models.TextChoices):
    PDF = "pdf", "PDF"
    PNG = "png", "PNG"
    JPG = "jpg", "JPG"
    JPEG = "jpeg", "JPEG"
    TXT = "txt", "TXT"


class File(models.Model):
    name = models.CharField(verbose_name="Название файла", max_length=200)
    thumbnail = models.CharField(verbose_name="Миниатюра", max_length=500, blank=True, null=True)
    size = models.IntegerField(verbose_name="Размер файла (в байтах)")
    format = models.CharField(verbose_name="Формат файла", max_length=10, choices=Format.choices)
    note = models.ForeignKey(
        "note.Note", on_delete=models.CASCADE, verbose_name="Заметка", related_name="files"
    )
    creation_date = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    file = models.FileField(upload_to='note_files/', null=True, blank=True, verbose_name="Файл")

    def __str__(self):
        return self.name

from django.db import models


class Theme(models.TextChoices):
    LIGHT = "light", "Светлая"
    DARK = "dark", "Темная"


class Settings(models.Model):
    theme = models.CharField(
        max_length=10, choices=Theme.choices, default=Theme.LIGHT, verbose_name="Тема оформления"
    )
    total_notes = models.IntegerField(default=0, verbose_name="Общее количество заметок")
    total_tags = models.IntegerField(default=0, verbose_name="Общее количество тегов")
    storage_used = models.IntegerField(default=0, verbose_name="Использовано памяти")

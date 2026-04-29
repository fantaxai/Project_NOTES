from django.db import models


class Tag(models.Model):
    name = models.CharField(verbose_name="Название тега", max_length=200)
    color = models.CharField(default="#7517CC", verbose_name="Цвет тега", max_length=7)
    creation_date = models.DateField(auto_now_add=True, verbose_name="Дата создания тега")

    def __str__(self):
        return self.name


class Note(models.Model):
    title = models.CharField(verbose_name="Название заметки", max_length=200)
    content = models.TextField(verbose_name="Содержание заметки")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    last_change_date = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")

    # Поля для идеи дня
    is_idea_candidate = models.BooleanField(default=True, verbose_name="Кандидат для идеи дня")
    shown_as_idea = models.BooleanField(default=False, verbose_name="Показана как идея дня")
    shown_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата последнего показа")
    times_shown_as_idea = models.PositiveIntegerField(
        default=0, verbose_name="Количество показов как идея дня"
    )
    
    # НОВОЕ: Привязка к пользователю
    user_id = models.CharField(max_length=36, db_index=True, verbose_name="ID пользователя", default='legacy')

    def __str__(self):
        return self.title


class IdeaOfTheDay(models.Model):
    note = models.ForeignKey("note.Note", on_delete=models.CASCADE, verbose_name="Заметка")
    date = models.DateField(auto_now_add=True, verbose_name="Дата показа")
    shown = models.BooleanField(default=True, verbose_name="Показана пользователю")
    
    # НОВОЕ: Привязка к пользователю
    user_id = models.CharField(max_length=36, db_index=True, verbose_name="ID пользователя", default='legacy')

    class Meta:
        unique_together = ["date", "note", "user_id"]  # Изменено: добавлен user_id
        verbose_name = "Идея дня"
        verbose_name_plural = "Идеи дня"

    def __str__(self):
        return f"{self.note.title} - {self.date}"
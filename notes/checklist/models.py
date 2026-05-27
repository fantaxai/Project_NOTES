from django.conf import settings
from django.db import models

from note.models import Note


class Idea(models.Model):
    class Category(models.TextChoices):
        STUDY = "study", "Учеба"
        TRAVEL = "travel", "Путешествия"
        ART = "art", "Искусство"
        FRIENDS = "friends", "Друзья"
        FAMILY = "family", "Семья"
        SPORT = "sport", "Спорт"
        WORK = "work", "Работа"
        SELF_DEVELOPMENT = "self_development", "Саморазвитие"

    text = models.TextField(verbose_name="Текст идеи")
    category = models.CharField(max_length=200, choices=Category.choices, verbose_name="Категория")


class CheckList(models.Model):
    creation_date = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    amount_of_ideas = models.PositiveSmallIntegerField(
        default=10, verbose_name="Количество идей", help_text="Не более 20"
    )
    categories = models.JSONField(default=list, blank=True, verbose_name="Выбранные категории")
    saved_as_note = models.OneToOneField(
        Note,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Сохранён как заметка",
        related_name="checklist_source",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="checklists",
        verbose_name="Пользователь",
        null=True,
        blank=True,
    )


class CheckListItem(models.Model):
    checklist = models.ForeignKey(
        CheckList, on_delete=models.CASCADE, verbose_name="Чек-лист", related_name="items"
    )
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, verbose_name="Идея из базы")
    date = models.PositiveSmallIntegerField(
        verbose_name="День месяца (1-31)", null=True, blank=True
    )
    completed = models.BooleanField(default=False, verbose_name="Выполнено")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ["order"]

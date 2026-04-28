import random

from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import IdeaOfTheDay, Note, Tag
from .serializers import (
    IdeaOfTheDaySerializer,
    NoteCreateUpdateSerializer,
    NoteSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(detail=True, methods=["get"])
    def notes(self, request, pk=None):
        """Получить все заметки с этим тегом"""
        tag = self.get_object()
        notes = tag.note_set.all().order_by("-creation_date")
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all().order_by("-creation_date")

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return NoteCreateUpdateSerializer
        return NoteSerializer

    @action(detail=True, methods=["post"])
    def add_tag(self, request, pk=None):
        note = self.get_object()
        tag_id = request.data.get("tag_id")
        try:
            tag = Tag.objects.get(id=tag_id)
            note.tags.add(tag)
            return Response({"status": "tag added"})
        except Tag.DoesNotExist:
            return Response({"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def remove_tag(self, request, pk=None):
        note = self.get_object()
        tag_id = request.data.get("tag_id")
        try:
            tag = Tag.objects.get(id=tag_id)
            note.tags.remove(tag)
            return Response({"status": "tag removed"})
        except Tag.DoesNotExist:
            return Response({"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)


class IdeaOfTheDayViewSet(viewsets.GenericViewSet):
    serializer_class = IdeaOfTheDaySerializer

    def get_queryset(self):
        today = timezone.now().date()
        return IdeaOfTheDay.objects.filter(date=today)

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Получить идею дня на сегодня"""
        today = timezone.now().date()

        # Проверяем, есть ли уже идея на сегодня
        today_idea = IdeaOfTheDay.objects.filter(date=today).first()

        if today_idea:
            serializer = self.get_serializer(today_idea)
            return Response(serializer.data)

        # Генерируем новую идею
        candidates = Note.objects.filter(is_idea_candidate=True)
        total = candidates.count()

        # Если меньше 20 заметок - идея дня не генерируется
        if total < 20:
            return Response(
                {"error": "Недостаточно заметок. Нужно минимум 20.", "total_candidates": total},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Алгоритм: показываем по кругу
        # Ищем непоказанные заметки
        unshown = candidates.filter(shown_as_idea=False)

        if unshown.exists():
            # Выбираем случайную из непоказанных
            idea_note = random.choice(list(unshown))
        else:
            # Все показаны - сбрасываем и начинаем заново
            candidates.update(shown_as_idea=False, shown_at=None)
            idea_note = random.choice(list(candidates))

        # Отмечаем как показанную
        idea_note.shown_as_idea = True
        idea_note.shown_at = timezone.now()
        idea_note.times_shown_as_idea += 1
        idea_note.save(update_fields=["shown_as_idea", "shown_at", "times_shown_as_idea"])

        # Создаём запись в истории
        idea = IdeaOfTheDay.objects.create(note=idea_note, date=today)

        serializer = self.get_serializer(idea)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_shown(self, request):
        """Отметить заметку как показанную"""
        note_id = request.data.get("note_id")

        if not note_id:
            return Response({"error": "note_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            note = Note.objects.get(id=note_id)
            note.shown_as_idea = True
            note.shown_at = timezone.now()
            note.times_shown_as_idea += 1
            note.save(update_fields=["shown_as_idea", "shown_at", "times_shown_as_idea"])

            return Response({"status": "success", "note_id": note_id, "shown_as_idea": True})
        except Note.DoesNotExist:
            return Response({"error": "Заметка не найдена"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def reset_shown(self, request):
        """Сбросить статус показа для всех заметок"""
        Note.objects.filter(is_idea_candidate=True).update(shown_as_idea=False, shown_at=None)

        return Response(
            {"status": "success", "message": "Статус показа сброшен для всех кандидатов"}
        )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Статистика по идеям дня"""
        total_candidates = Note.objects.filter(is_idea_candidate=True).count()
        shown_count = Note.objects.filter(is_idea_candidate=True, shown_as_idea=True).count()
        unshown_count = total_candidates - shown_count

        return Response(
            {
                "total_candidates": total_candidates,
                "shown_count": shown_count,
                "unshown_count": unshown_count,
                "can_generate": total_candidates >= 20,
                "needs_reset": shown_count >= total_candidates and total_candidates >= 20,
            }
        )

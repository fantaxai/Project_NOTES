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


def get_user_id(request):
    """Получает user_id из заголовка запроса"""
    user_id = request.headers.get('X-User-ID', 'unknown')
    return user_id


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    @action(detail=True, methods=["get"])
    def notes(self, request, pk=None):
        """Получить все заметки с этим тегом"""
        tag = self.get_object()
        user_id = get_user_id(request)
        notes = tag.note_set.filter(user_id=user_id).order_by("-creation_date")
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer  # По умолчанию

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return NoteCreateUpdateSerializer
        return NoteSerializer
    
    def get_queryset(self):
        """Фильтруем заметки по user_id"""
        user_id = get_user_id(self.request)
        return Note.objects.filter(user_id=user_id).order_by("-creation_date")
    
    def perform_create(self, serializer):
        """Автоматически добавляем user_id при создании заметки"""
        user_id = get_user_id(self.request)
        serializer.save(user_id=user_id)

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
        user_id = get_user_id(self.request)
        today = timezone.now().date()
        return IdeaOfTheDay.objects.filter(date=today, user_id=user_id)

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Получить идею дня на сегодня"""
        user_id = get_user_id(request)
        today = timezone.now().date()

        # Проверяем, есть ли уже идея на сегодня для этого пользователя
        today_idea = IdeaOfTheDay.objects.filter(date=today, user_id=user_id).first()

        if today_idea:
            serializer = self.get_serializer(today_idea)
            return Response(serializer.data)

        # Считаем кандидатов для пользователя
        total = Note.objects.filter(is_idea_candidate=True, user_id=user_id).count()

        # Если меньше 20 заметок - возвращаем статистику
        if total < 20:
            shown_ids = list(
                Note.objects.filter(
                    is_idea_candidate=True, shown_as_idea=True, user_id=user_id
                ).values_list("id", flat=True)
            )
            return Response({
                "note": None,
                "total_candidates": total,
                "shown_ids": shown_ids,
                "shown_count": len(shown_ids),
                "can_generate": False,
                "message": f"Модуль «Идея дня» работает от 20 заметок-кандидатов. Сейчас: {total}"
            })

        # Генерируем новую идею
        candidates = Note.objects.filter(is_idea_candidate=True, user_id=user_id)
        unshown = candidates.filter(shown_as_idea=False)

        if unshown.exists():
            idea_note = random.choice(list(unshown))
        else:
            candidates.update(shown_as_idea=False, shown_at=None)
            idea_note = random.choice(list(candidates))

        # Отмечаем как показанную
        idea_note.shown_as_idea = True
        idea_note.shown_at = timezone.now()
        idea_note.times_shown_as_idea += 1
        idea_note.save(update_fields=["shown_as_idea", "shown_at", "times_shown_as_idea"])

        # Создаём запись в истории
        idea = IdeaOfTheDay.objects.create(note=idea_note, date=today, user_id=user_id)

        serializer = self.get_serializer(idea)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_shown(self, request):
        """Отметить заметку как показанную"""
        user_id = get_user_id(request)
        note_id = request.data.get("note_id")

        if not note_id:
            return Response({"error": "note_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            note = Note.objects.get(id=note_id, user_id=user_id)
            note.shown_as_idea = True
            note.shown_at = timezone.now()
            note.times_shown_as_idea += 1
            note.save(update_fields=["shown_as_idea", "shown_at", "times_shown_as_idea"])

            return Response({"status": "success", "note_id": note_id, "shown_as_idea": True})
        except Note.DoesNotExist:
            return Response({"error": "Заметка не найдена"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def reset_shown(self, request):
        """Сбросить статус показа для всех заметок пользователя"""
        user_id = get_user_id(request)
        Note.objects.filter(is_idea_candidate=True, user_id=user_id).update(
            shown_as_idea=False, shown_at=None
        )

        return Response(
            {"status": "success", "message": "Статус показа сброшен для всех кандидатов"}
        )
    serializer_class = IdeaOfTheDaySerializer

    def get_queryset(self):
        user_id = get_user_id(self.request)
        today = timezone.now().date()
        return IdeaOfTheDay.objects.filter(date=today, user_id=user_id)

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Получить идею дня на сегодня"""
        user_id = get_user_id(request)
        today = timezone.now().date()

        today_idea = IdeaOfTheDay.objects.filter(date=today, user_id=user_id).first()

        if today_idea:
            serializer = self.get_serializer(today_idea)
            return Response(serializer.data)

        total = Note.objects.filter(is_idea_candidate=True, user_id=user_id).count()

        if total < 20:
            shown_ids = list(
                Note.objects.filter(
                    is_idea_candidate=True, shown_as_idea=True, user_id=user_id
                ).values_list("id", flat=True)
            )
            return Response({
                "note": None,
                "total_candidates": total,
                "shown_ids": shown_ids,
                "shown_count": len(shown_ids),
                "can_generate": False,
                "message": f"Модуль «Идея дня» работает от 20 заметок-кандидатов. Сейчас: {total}"
            })

        candidates = Note.objects.filter(is_idea_candidate=True, user_id=user_id)
        unshown = candidates.filter(shown_as_idea=False)

        if unshown.exists():
            idea_note = random.choice(list(unshown))
        else:
            candidates.update(shown_as_idea=False, shown_at=None)
            idea_note = random.choice(list(candidates))

        idea_note.shown_as_idea = True
        idea_note.shown_at = timezone.now()
        idea_note.times_shown_as_idea += 1
        idea_note.save(update_fields=["shown_as_idea", "shown_at", "times_shown_as_idea"])

        idea = IdeaOfTheDay.objects.create(note=idea_note, date=today, user_id=user_id)

        serializer = self.get_serializer(idea)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_shown(self, request):
        """Отметить заметку как показанную"""
        user_id = get_user_id(request)
        note_id = request.data.get("note_id")

        if not note_id:
            return Response({"error": "note_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            note = Note.objects.get(id=note_id, user_id=user_id)
            note.shown_as_idea = True
            note.shown_at = timezone.now()
            note.times_shown_as_idea += 1
            note.save(update_fields=["shown_as_idea", "shown_at", "times_shown_as_idea"])

            return Response({"status": "success", "note_id": note_id, "shown_as_idea": True})
        except Note.DoesNotExist:
            return Response({"error": "Заметка не найдена"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def reset_shown(self, request):
        """Сбросить статус показа для всех заметок пользователя"""
        user_id = get_user_id(request)
        Note.objects.filter(is_idea_candidate=True, user_id=user_id).update(
            shown_as_idea=False, shown_at=None
        )

        return Response(
            {"status": "success", "message": "Статус показа сброшен для всех кандидатов"}
        )

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Получить идею дня на сегодня"""
        user_id = get_user_id(request)
        today = timezone.now().date()

        # Проверяем, есть ли уже идея на сегодня для этого пользователя
        today_idea = IdeaOfTheDay.objects.filter(date=today, user_id=user_id).first()

        if today_idea:
            serializer = self.get_serializer(today_idea)
            return Response(serializer.data)

        # Считаем кандидатов для пользователя
        total = Note.objects.filter(is_idea_candidate=True, user_id=user_id).count()

        # Если меньше 20 заметок - возвращаем статистику
        if total < 20:
            shown_ids = list(
                Note.objects.filter(
                    is_idea_candidate=True, shown_as_idea=True, user_id=user_id
                ).values_list("id", flat=True)
            )
            return Response({
                "note": None,
                "total_candidates": total,
                "shown_ids": shown_ids,
                "shown_count": len(shown_ids),
                "can_generate": False,
                "message": f"Модуль «Идея дня» работает от 20 заметок-кандидатов. Сейчас: {total}"
            })

        # Генерируем новую идею
        candidates = Note.objects.filter(is_idea_candidate=True, user_id=user_id)
        unshown = candidates.filter(shown_as_idea=False)

        if unshown.exists():
            idea_note = random.choice(list(unshown))
        else:
            candidates.update(shown_as_idea=False, shown_at=None)
            idea_note = random.choice(list(candidates))

        # Отмечаем как показанную
        idea_note.shown_as_idea = True
        idea_note.shown_at = timezone.now()
        idea_note.times_shown_as_idea += 1
        idea_note.save(update_fields=["shown_as_idea", "shown_at", "times_shown_as_idea"])

        # Создаём запись в истории
        idea = IdeaOfTheDay.objects.create(note=idea_note, date=today, user_id=user_id)

        serializer = self.get_serializer(idea)
        return Response(serializer.data)
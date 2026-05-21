import random

from django.shortcuts import render
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission

from .models import IdeaOfTheDay, Note, Tag
from .serializers import (
    IdeaOfTheDaySerializer,
    NoteCreateUpdateSerializer,
    NoteSerializer,
    TagSerializer,
)


class AllowAnyOrAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return True

class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user).order_by("-creation_date")
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def notes(self, request, pk=None):
        """Получить все заметки с этим тегом"""
        tag = self.get_object()
        notes = tag.note_set.filter(user=request.user).order_by("-creation_date")
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

class NoteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return NoteCreateUpdateSerializer
        return NoteSerializer
    
    def get_queryset(self):
        """Фильтруем заметки по пользователю"""
        return Note.objects.filter(user=self.request.user).order_by("-creation_date")
    
    def perform_create(self, serializer):
        """Автоматически добавляем пользователя при создании заметки"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def add_tag(self, request, pk=None):
        note = self.get_object()
        tag_id = request.data.get("tag_id")
        try:
            tag = Tag.objects.get(id=tag_id, user=request.user)
            note.tags.add(tag)
            return Response({"status": "tag added"})
        except Tag.DoesNotExist:
            return Response({"error": "Tag not found or doesn't belong to user"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def remove_tag(self, request, pk=None):
        note = self.get_object()
        tag_id = request.data.get("tag_id")
        try:
            tag = Tag.objects.get(id=tag_id, user=request.user)
            note.tags.remove(tag)
            return Response({"status": "tag removed"})
        except Tag.DoesNotExist:
            return Response({"error": "Tag not found or doesn't belong to user"}, 
                          status=status.HTTP_404_NOT_FOUND)


class IdeaOfTheDayViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IdeaOfTheDaySerializer

    def get_queryset(self):
        today = timezone.now().date()
        return IdeaOfTheDay.objects.filter(date=today, user=self.request.user)

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Получить идею дня на сегодня"""
        today = timezone.now().date()

        # Проверяем, есть ли уже идея на сегодня для этого пользователя
        today_idea = IdeaOfTheDay.objects.filter(date=today, user=request.user).first()

        if today_idea:
            serializer = self.get_serializer(today_idea)
            return Response(serializer.data)

        # Считаем кандидатов для пользователя
        total = Note.objects.filter(is_idea_candidate=True, user=request.user).count()

        # Если меньше 20 заметок - возвращаем статистику
        if total < 20:
            shown_ids = list(
                Note.objects.filter(
                    is_idea_candidate=True, shown_as_idea=True, user=request.user
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
        candidates = Note.objects.filter(is_idea_candidate=True, user=request.user)
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
        idea = IdeaOfTheDay.objects.create(note=idea_note, date=today, user=request.user)

        serializer = self.get_serializer(idea)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_shown(self, request):
        """Отметить заметку как показанную"""
        note_id = request.data.get("note_id")

        if not note_id:
            return Response({"error": "note_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            note = Note.objects.get(id=note_id, user=request.user)
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
        Note.objects.filter(is_idea_candidate=True, user=request.user).update(
            shown_as_idea=False, shown_at=None
        )

        return Response(
            {"status": "success", "message": "Статус показа сброшен для всех кандидатов"}
        )
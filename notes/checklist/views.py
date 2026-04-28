import random

from django.db import transaction
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from note.models import Note

from .models import CheckList, CheckListItem, Idea
from .serializers import (
    CheckListGenerateSerializer,
    CheckListItemSerializer,
    CheckListSerializer,
    IdeaSerializer,
)


class IdeaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Idea.objects.all()
    serializer_class = IdeaSerializer

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        """Получить идеи по категории"""
        category = request.query_params.get("category")
        if category:
            ideas = Idea.objects.filter(category=category)
            serializer = self.get_serializer(ideas, many=True)
            return Response(serializer.data)
        return Response({"error": "category parameter required"}, status=400)


class CheckListViewSet(viewsets.ModelViewSet):
    queryset = CheckList.objects.all().order_by("-creation_date")
    serializer_class = CheckListSerializer

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """Генерация нового чек-листа"""
        serializer = CheckListGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data["amount_of_ideas"]
        categories = serializer.validated_data.get("categories", [])

        if categories:
            ideas = Idea.objects.filter(category__in=categories)
        else:
            ideas = Idea.objects.all()

        if ideas.count() == 0:
            return Response(
                {"error": "Нет идей в выбранных категориях"}, status=status.HTTP_400_BAD_REQUEST
            )
        actual_amount = min(
            amount, ideas.count()
        )  # если запрошено больше идей, чем есть — ограничиваем
        selected_ideas = random.sample(list(ideas), actual_amount)

        if categories and len(categories) > 1:
            selected_ideas = self._balance_by_category(selected_ideas, categories, actual_amount)

        # создаём чек-лист
        with transaction.atomic():
            checklist = CheckList.objects.create(
                amount_of_ideas=actual_amount, categories=categories
            )
            items = []
            for order, idea in enumerate(selected_ideas):
                items.append(CheckListItem(checklist=checklist, idea=idea, order=order))
            CheckListItem.objects.bulk_create(items)

        return Response(CheckListSerializer(checklist).data)

    def _balance_by_category(self, ideas, categories, total_amount):
        from collections import defaultdict

        ideas_by_category = defaultdict(list)
        for idea in ideas:
            ideas_by_category[idea.category].append(idea)

        num_categories = len(categories)
        base_per_category = total_amount // num_categories
        remainder = total_amount % num_categories

        balanced_ideas = []
        for i, category in enumerate(categories):
            count = base_per_category + (1 if i < remainder else 0)
            category_ideas = ideas_by_category.get(category, [])

            if len(category_ideas) >= count:
                balanced_ideas.extend(random.sample(category_ideas, count))
            else:
                balanced_ideas.extend(category_ideas)
        if len(balanced_ideas) < total_amount:
            remaining = total_amount - len(balanced_ideas)
            all_other_ideas = [i for i in ideas if i not in balanced_ideas]
            if all_other_ideas:
                balanced_ideas.extend(
                    random.sample(all_other_ideas, min(remaining, len(all_other_ideas)))
                )
        random.shuffle(balanced_ideas)
        return balanced_ideas

    @action(detail=True, methods=["post"])
    def save_as_note(self, request, pk=None):
        """Сохранить чек-лист как заметку"""
        checklist = self.get_object()

        if checklist.saved_as_note:
            return Response(
                {"error": "Чек-лист уже сохранён как заметка"}, status=status.HTTP_400_BAD_REQUEST
            )

        content_lines = []
        for item in checklist.items.all().order_by("order"):
            status_mark = "✅" if item.completed else "⬜"
            content_lines.append(f"{status_mark} {item.idea.text}")

        note = Note.objects.create(
            title=f"Чек-лист от {checklist.creation_date.strftime('%d.%m.%Y')}",
            content="\n".join(content_lines),
        )
        checklist.saved_as_note = note
        checklist.save()

        return Response({"message": "Чек-лист сохранён как заметка", "note_id": note.id})

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        """Перегенерировать чек-лист"""
        checklist = self.get_object()
        checklist.items.all().delete()

        amount = checklist.amount_of_ideas
        categories = checklist.categories
        if categories:
            ideas = Idea.objects.filter(category__in=categories)
        else:
            ideas = Idea.objects.all()

        if ideas.count() == 0:
            return Response(
                {"error": "Нет идей в выбранных категориях"}, status=status.HTTP_400_BAD_REQUEST
            )

        actual_amount = min(amount, ideas.count())
        selected_ideas = random.sample(list(ideas), actual_amount)

        items = []
        for order, idea in enumerate(selected_ideas):
            items.append(CheckListItem(checklist=checklist, idea=idea, order=order))
        CheckListItem.objects.bulk_create(items)

        return Response(CheckListSerializer(checklist).data)

    @action(detail=True, methods=["post"])
    def toggle_completed(self, request, pk=None):
        """Отметить/снять отметку выполнения пункта"""
        item_id = request.data.get("item_id")
        try:
            item = CheckListItem.objects.get(id=item_id, checklist_id=pk)
            item.completed = not item.completed
            item.save()
            return Response({"completed": item.completed})
        except CheckListItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

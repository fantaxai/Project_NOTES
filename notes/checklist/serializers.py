from rest_framework import serializers

from .models import CheckList, CheckListItem, Idea


class IdeaSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Idea
        fields = ["id", "text", "category", "category_display"]


class CheckListItemSerializer(serializers.ModelSerializer):
    idea_text = serializers.CharField(source="idea.text", read_only=True)
    category = serializers.CharField(source="idea.category", read_only=True)
    category_display = serializers.CharField(source="idea.get_category_display", read_only=True)

    class Meta:
        model = CheckListItem
        fields = [
            "id",
            "idea",
            "idea_text",
            "category",
            "category_display",
            "date",
            "completed",
            "order"
        ]
        read_only_fields = ["id", "idea", "idea_text", "category", "category_display"]


class CheckListSerializer(serializers.ModelSerializer):
    items = CheckListItemSerializer(many=True, read_only=True)
    categories_display = serializers.SerializerMethodField()

    class Meta:
        model = CheckList
        fields = [
            "id",
            "creation_date",
            "amount_of_ideas",
            "categories",
            "categories_display",
            "saved_as_note",
            "items",
            "user_id"
        ]
        read_only_fields = ["id", "creation_date", "saved_as_note", "user_id"]

    def get_categories_display(self, obj):
        return [Idea.Category(cat).label for cat in obj.categories]


class CheckListGenerateSerializer(serializers.Serializer):
    """Сериализатор для генерации чек-листа"""

    amount_of_ideas = serializers.IntegerField(min_value=1, max_value=20, default=10)
    categories = serializers.ListField(
        child=serializers.ChoiceField(choices=Idea.Category.choices), required=False, default=list
    )

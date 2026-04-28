from rest_framework import serializers

from .models import IdeaOfTheDay, Note, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color", "creation_date"]
        read_only_fields = ["id", "created_at"]


class NoteSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, source="tags", required=False
    )

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "content",
            "creation_date",
            "last_change_date",
            "tags",
            "tag_ids",
            "is_idea_candidate",
            "shown_as_idea",
            "shown_at",
            "times_shown_as_idea",
        ]
        read_only_fields = [
            "id",
            "creation_date",
            "last_change_date",
            "shown_at",
            "times_shown_as_idea",
        ]


class NoteCreateUpdateSerializer(serializers.ModelSerializer):
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=False, source="tags"
    )

    class Meta:
        model = Note
        fields = ["id", "title", "content", "tag_ids", "is_idea_candidate"]
        read_only_fields = ["id"]
        extra_kwargs = {"title": {"required": False}, "content": {"required": False}}

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        note = Note.objects.create(**validated_data)
        note.tags.set(tags)
        return note

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class IdeaOfTheDaySerializer(serializers.ModelSerializer):
    note = NoteSerializer(read_only=True)
    note_id = serializers.PrimaryKeyRelatedField(
        queryset=Note.objects.all(), write_only=True, source="note"
    )
    total_candidates = serializers.SerializerMethodField()
    shown_ids = serializers.SerializerMethodField()

    class Meta:
        model = IdeaOfTheDay
        fields = ["id", "note", "note_id", "date", "shown", "total_candidates", "shown_ids"]
        read_only_fields = ["id", "date"]

    def get_total_candidates(self, obj):
        return Note.objects.filter(is_idea_candidate=True).count()

    def get_shown_ids(self, obj):
        return list(
            Note.objects.filter(is_idea_candidate=True, shown_as_idea=True).values_list(
                "id", flat=True
            )
        )

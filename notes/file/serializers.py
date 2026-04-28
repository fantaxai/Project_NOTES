from rest_framework import serializers

from note.models import Note

from .models import File


class FileSerializer(serializers.ModelSerializer):
    note_title = serializers.ReadOnlyField(source="note.title")

    class Meta:
        model = File
        fields = [
            "id",
            "name",
            "thumbnail",
            "format",
            "size",
            "note",
            "note_title",
            "creation_date",
        ]
        read_only_fields = ["id", "creation_date"]


class FileCreateSerializer(serializers.ModelSerializer):
    note = serializers.PrimaryKeyRelatedField(queryset=Note.objects.all())
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = File
        fields = ["id", "name", "thumbnail", "format", "size", "note", "creation_date"]
        read_only_fields = ["id", "creation_date"]

    def validate_size(self, value):
        # Преобразуем в int если пришло как строка
        value = int(value) if isinstance(value, str) else value
        max_size = 10 * 1024 * 1024
        if value > max_size:
            raise serializers.ValidationError(
                f"Размер файла не должен превышать 10 МБ. Текущий: {value / (1024 * 1024):.2f} МБ"
            )
        return value

    def validate_format(self, value):
        allowed_formats = ["pdf", "png", "jpg", "jpeg", "txt"]
        if value.lower() not in allowed_formats:
            raise serializers.ValidationError(
                f'Недопустимый формат "{value}". Разрешены: {", ".join(allowed_formats)}'
            )
        return value.lower()

    def validate(self, data):
        print("Валидация данных:", data)  # Для отладки
        return data

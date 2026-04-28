from rest_framework import serializers

from .models import Settings


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ["id", "theme", "total_notes", "total_tags", "storage_used"]
        read_only_fields = ["id", "total_notes", "total_tags", "storage_used"]

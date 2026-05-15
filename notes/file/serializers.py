from rest_framework import serializers
from .models import File, Format


class FileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = File
        fields = ['id', 'name', 'thumbnail', 'size', 'format', 'note', 'creation_date', 'file_url']
    
    def get_file_url(self, obj):
        return obj.file_url


class FileCreateSerializer(serializers.ModelSerializer):
    file_data = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = File
        fields = ['id', 'name', 'thumbnail', 'size', 'format', 'note', 'file_data']
    
    def create(self, validated_data):
        file_data = validated_data.pop('file_data', None)
        instance = super().create(validated_data)
        return instance
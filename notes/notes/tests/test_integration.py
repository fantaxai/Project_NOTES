# notes/tests/test_integration.py
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestNoteTagIntegration:

    def test_create_note_with_new_tags(self, api_client):
        """Создание заметки с новыми тегами в одном запросе"""
        url = reverse("note-list")
        data = {
            "title": "Integration Test",
            "content": "Test Content",
            "tags": [
                {"name": "New Tag 1", "color": "#FFB3B3"},
                {"name": "New Tag 2", "color": "#A0C4FF"},
            ],
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_filter_notes_by_multiple_tags(self, api_client, note_factory, sample_tags):
        """Фильтрация заметок по нескольким тегам"""
        note1 = note_factory("Note 1", "Content", [sample_tags[0]])
        note2 = note_factory("Note 2", "Content", [sample_tags[1]])
        note3 = note_factory("Note 3", "Content", [sample_tags[0], sample_tags[1]])

        url = reverse("note-list")
        response = api_client.get(url, {"tags": f"{sample_tags[0].id},{sample_tags[1].id}"})
        assert response.status_code == status.HTTP_200_OK

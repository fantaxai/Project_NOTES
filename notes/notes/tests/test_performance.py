import pytest
import time
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.slow
class TestPerformance:

    def test_list_notes_performance(self, api_client, note_factory):
        """Проверка производительности при большом количестве заметок"""
        # Создаем 100 заметок
        for i in range(100):
            note_factory(f"Note {i}", f"Content {i}")

        url = reverse("note-list")

        start_time = time.time()
        response = api_client.get(url)
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Должно выполняться менее 1 секунды

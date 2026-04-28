import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from note.models import Note, Tag, IdeaOfTheDay


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Автоматически включает доступ к БД для всех тестов."""
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def tag_factory():
    """Фабрика для создания тегов"""

    def create_tag(name="Test Tag", color="#C9A9E8"):
        return Tag.objects.create(name=name, color=color)

    return create_tag


@pytest.fixture
def note_factory(tag_factory):
    """Фабрика для создания заметок"""

    def create_note(title="Test Note", content="Test Content", tags=None, is_idea_candidate=True):
        note = Note.objects.create(
            title=title, content=content, is_idea_candidate=is_idea_candidate
        )
        if tags:
            note.tags.set(tags)
        return note

    return create_note


@pytest.fixture
def sample_tags(tag_factory):
    """Создает набор тестовых тегов"""
    return [
        tag_factory("Любовь", "#FFB3B3"),
        tag_factory("Учеба", "#A0C4FF"),
        tag_factory("Работа", "#CAFFBF"),
    ]


@pytest.fixture
def sample_notes(note_factory, sample_tags):
    """Создает набор тестовых заметок"""
    notes = []
    notes.append(note_factory("Заметка 1", "Содержание 1", [sample_tags[0]]))
    notes.append(note_factory("Заметка 2", "Содержание 2", [sample_tags[1]]))
    notes.append(note_factory("Заметка 3", "Содержание 3", [sample_tags[0], sample_tags[1]]))
    return notes

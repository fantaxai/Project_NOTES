import pytest
from datetime import date
from note.models import Note, Tag, IdeaOfTheDay
from note.serializers import (
    TagSerializer,
    NoteSerializer,
    NoteCreateUpdateSerializer,
    IdeaOfTheDaySerializer,
)


@pytest.mark.django_db
class TestTagSerializer:

    def test_serialize_tag(self):
        tag = Tag.objects.create(name="Python", color="#A0C4FF")
        serializer = TagSerializer(tag)
        data = serializer.data

        assert data["name"] == "Python"
        assert data["color"] == "#A0C4FF"
        assert "id" in data
        assert "creation_date" in data

    def test_deserialize_tag(self):
        data = {"name": "Django", "color": "#CAFFBF"}
        serializer = TagSerializer(data=data)
        assert serializer.is_valid()

        tag = serializer.save()
        assert tag.name == "Django"
        assert tag.color == "#CAFFBF"

    def test_default_color(self):
        data = {"name": "Vue"}
        serializer = TagSerializer(data=data)
        assert serializer.is_valid()

        tag = serializer.save()
        assert tag.color == "#7517CC"  # Цвет по умолчанию из модели


@pytest.mark.django_db
class TestNoteSerializer:

    def test_serialize_note(self, sample_tags):
        note = Note.objects.create(title="Test", content="Content")
        note.tags.set(sample_tags[:2])

        serializer = NoteSerializer(note)
        data = serializer.data

        assert data["title"] == "Test"
        assert data["content"] == "Content"
        assert len(data["tags"]) == 2
        assert "creation_date" in data
        assert "last_change_date" in data

    def test_note_serializer_readonly_fields(self):
        note = Note.objects.create(title="Original", content="Content")
        data = {
            "title": "Changed",
            "content": "Changed content",
            "creation_date": "2020-01-01",
            "last_change_date": "2020-01-01",
        }
        serializer = NoteSerializer(note, data=data, partial=True)
        assert serializer.is_valid()

        updated = serializer.save()
        assert updated.title == "Changed"
        # Даты не должны измениться (read_only)
        assert updated.creation_date == note.creation_date


@pytest.mark.django_db
class TestNoteCreateUpdateSerializer:

    def test_create_note_with_tags(self, sample_tags):
        data = {
            "title": "New Note",
            "content": "New Content",
            "tag_ids": [sample_tags[0].id, sample_tags[1].id],
        }
        serializer = NoteCreateUpdateSerializer(data=data)
        assert serializer.is_valid()

        note = serializer.save()
        assert note.title == "New Note"
        assert note.tags.count() == 2

    def test_update_note_tags(self, sample_tags):
        note = Note.objects.create(title="Original", content="Content")
        note.tags.set([sample_tags[0]])

        data = {"title": "Updated", "tag_ids": [sample_tags[1].id, sample_tags[2].id]}
        serializer = NoteCreateUpdateSerializer(note, data=data, partial=True)
        assert serializer.is_valid()

        updated = serializer.save()
        assert updated.title == "Updated"
        assert updated.tags.count() == 2
        assert sample_tags[1] in updated.tags.all()

    def test_update_without_tags(self, sample_tags):
        note = Note.objects.create(title="Original", content="Content")
        note.tags.set([sample_tags[0]])

        data = {"title": "Updated only title"}
        serializer = NoteCreateUpdateSerializer(note, data=data, partial=True)
        assert serializer.is_valid()

        updated = serializer.save()
        assert updated.title == "Updated only title"
        assert updated.tags.count() == 1  # Теги не изменились


@pytest.mark.django_db
class TestIdeaOfTheDaySerializer:

    def test_serialize_idea(self, note_factory):
        note = note_factory("Idea Note", "Content")
        idea = IdeaOfTheDay.objects.create(note=note)
        serializer = IdeaOfTheDaySerializer(idea)
        data = serializer.data

        assert data["id"] == idea.id
        assert data["date"] == str(idea.date)
        assert data["shown"] == idea.shown
        assert data["note"]["title"] == note.title

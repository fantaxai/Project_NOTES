import pytest
from django.core.exceptions import ValidationError
from note.models import Note, Tag, IdeaOfTheDay
from file.models import File


@pytest.mark.django_db
class TestTagModel:

    def test_create_tag(self):
        tag = Tag.objects.create(name="Python", color="#A0C4FF")
        assert tag.name == "Python"
        assert tag.color == "#A0C4FF"
        assert tag.creation_date is not None

    def test_tag_str_representation(self):
        tag = Tag.objects.create(name="Django")
        assert str(tag) == "Django"

    def test_default_color(self):
        tag = Tag.objects.create(name="Vue")
        assert tag.color == "#7517CC"  # Реальный цвет из модели


@pytest.mark.django_db
class TestNoteModel:

    def test_create_note(self):
        note = Note.objects.create(title="Test", content="Test content")
        assert note.title == "Test"
        assert note.content == "Test content"
        assert note.creation_date is not None
        assert note.last_change_date is not None
        assert note.is_idea_candidate is True  # По умолчанию True

    def test_note_with_tags(self, sample_tags):
        note = Note.objects.create(title="Tagged", content="Content")
        note.tags.set(sample_tags[:2])
        assert note.tags.count() == 2

    def test_note_str_representation(self):
        note = Note.objects.create(title="My Note")
        assert str(note) == "My Note"


@pytest.mark.django_db
class TestIdeaOfTheDayModel:

    def test_create_idea_of_day(self, note_factory):
        note = note_factory("Idea", "Content")
        idea = IdeaOfTheDay.objects.create(note=note)
        assert idea.note == note
        assert idea.date is not None
        assert idea.shown is True


@pytest.mark.django_db
class TestFileModel:

    def test_create_file(self, note_factory):
        note = note_factory("Test Note", "Content")
        file = File.objects.create(name="test.pdf", size=1024, format="pdf", note=note)
        assert file.name == "test.pdf"
        assert file.size == 1024
        assert file.format == "pdf"
        assert file.note == note
        assert file.creation_date is not None

    def test_file_str_representation(self, note_factory):
        note = note_factory("Test Note")
        file = File.objects.create(name="document.pdf", size=2048, format="pdf", note=note)
        assert str(file) == "document.pdf"

    def test_file_with_thumbnail(self, note_factory):
        note = note_factory("Test Note")
        file = File.objects.create(
            name="image.jpg",
            size=512,
            format="jpg",
            note=note,
            thumbnail="data:image/jpeg;base64,...",
        )
        assert file.thumbnail is not None
        assert file.format == "jpg"

    def test_file_format_choices(self, note_factory):
        note = note_factory("Test Note")

        # Проверяем все допустимые форматы
        formats = ["pdf", "png", "jpg", "jpeg", "txt"]
        for fmt in formats:
            file = File.objects.create(name=f"test.{fmt}", size=100, format=fmt, note=note)
            assert file.format == fmt

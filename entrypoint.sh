#!/bin/sh

echo "=== Starting Notes App ==="

# Создаем папку для базы данных если её нет
mkdir -p /app/notes/data

echo "Applying database migrations..."
if ! python manage.py migrate --noinput; then
    echo "Migration failed! Removing corrupted database..."
    rm -f /app/notes/data/db.sqlite3
    echo "Retrying migrations..."
    python manage.py migrate --noinput
fi

# Загружаем фикстуры ТОЛЬКО если база пустая
echo "Checking if initial data needs to be loaded..."
python manage.py shell -c "
from checklist.models import Idea
if Idea.objects.count() == 0:
    from django.core.management import call_command
    call_command('loaddata', 'initial_ideas')
    print('Initial ideas loaded successfully!')
else:
    print(f'Database already has {Idea.objects.count()} ideas, skipping fixture loading.')
"

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 notes.wsgi:application
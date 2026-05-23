# Этап 1: Сборка фронтенда
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Копируем package.json (lockfile не используем — он битый, пересоздаём)
COPY notes_frontend/notes-vue-app/package.json ./

# npm install создаст корректный lockfile на месте
RUN npm install

# Копируем весь исходный код фронтенда
COPY notes_frontend/notes-vue-app/ .

# Собираем
RUN npm run build

# Этап 2: Финальный образ с бэкендом
FROM python:3.11-slim

WORKDIR /app

COPY notes/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

COPY notes/ /app/notes/

# Копируем собранный фронтенд
COPY --from=frontend-builder /frontend/dist /app/notes/static/frontend

WORKDIR /app/notes

RUN python manage.py collectstatic --noinput --clear

COPY docker/entrypoint.sh /app/notes/entrypoint.sh
RUN chmod +x /app/notes/entrypoint.sh

RUN mkdir -p /app/notes/data /app/notes/staticfiles && \
    chmod -R 777 /app/notes/data /app/notes/staticfiles

EXPOSE 8000

CMD ["/app/notes/entrypoint.sh"]

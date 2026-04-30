# Этап 1: Сборка фронтенда
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend
COPY notes_frontend/notes-vue-app/package*.json ./
RUN npm install
COPY notes_frontend/notes-vue-app/ .
RUN npm run build

# Этап 2: Финальный образ с бэкендом
FROM python:3.11-slim

WORKDIR /app

COPY notes/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

COPY notes/ /app/notes/
COPY --from=frontend-builder /frontend/dist /app/notes/static/frontend

WORKDIR /app/notes

RUN python manage.py collectstatic --noinput

COPY entrypoint.sh /app/notes/entrypoint.sh
RUN chmod +x /app/notes/entrypoint.sh

RUN mkdir -p /app/notes/data /app/notes/staticfiles && \
    chmod -R 777 /app/notes/data /app/notes/staticfiles

EXPOSE 8000

CMD ["/app/notes/entrypoint.sh"]
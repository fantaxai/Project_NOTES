# ============================================
# Stage 1: Сборка фронтенда (Vue)
# ============================================
FROM node:22-alpine AS frontend-build

WORKDIR /app
COPY notes_frontend/notes-vue-app/package*.json ./
RUN npm install
COPY notes_frontend/notes-vue-app/ .
RUN npm run build

# ============================================
# Stage 2: Финальный образ с Django + Vue
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Копируем и устанавливаем зависимости Python
COPY notes/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Копируем код Django
COPY notes/ /app/notes/

# Копируем собранный фронтенд в статику
COPY --from=frontend-build /app/dist /app/notes/static/frontend

WORKDIR /app/notes

# Собираем статику Django
RUN python manage.py collectstatic --noinput

# СОЗДАЕМ ТАБЛИЦЫ В БАЗЕ ДАННЫХ
RUN python manage.py migrate --noinput

# Фиксим права на папку со статикой и создаём home для appuser
RUN mkdir -p /home/appuser && \
    chown -R 1000:1000 /home/appuser /app

USER 1000

EXPOSE 8000

# Запуск через gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "notes.wsgi:application"]
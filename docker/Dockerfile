# ============================================
# Stage 1: Сборка фронтенда (Vue)
# ============================================
FROM node:22-alpine AS frontend-build

WORKDIR /app

# Настраиваем npm и добавляем DNS
RUN npm config set registry https://registry.npmjs.org/ && \
    npm config set fetch-timeout 120000 && \
    npm config set fetch-retries 5

COPY notes_frontend/notes-vue-app/package*.json ./
RUN npm install --no-audit --no-fund
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

# Копируем код Django (включая фикстуры)
COPY notes/ /app/notes/

# Копируем собранный фронтенд в статику
COPY --from=frontend-build /app/dist /app/notes/static/frontend

WORKDIR /app/notes

# Собираем статику Django
RUN python manage.py collectstatic --noinput

# Копируем entrypoint скрипт
COPY entrypoint.sh /app/notes/entrypoint.sh
RUN chmod +x /app/notes/entrypoint.sh

# Создаем папки и настраиваем права
RUN mkdir -p /app/notes/data /app/notes/staticfiles && \
    chmod -R 777 /app/notes/data /app/notes/staticfiles

EXPOSE 8000

CMD ["/app/notes/entrypoint.sh"]
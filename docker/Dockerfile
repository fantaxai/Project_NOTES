FROM python:3.11-slim

WORKDIR /app

# Копируем и устанавливаем зависимости Python
COPY notes/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Копируем код Django
COPY notes/ /app/notes/

# Копируем УЖЕ СОБРАННЫЙ фронтенд (ты его собрала локально командой npm run build)
COPY notes_frontend/notes-vue-app/dist /app/notes/static/frontend

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
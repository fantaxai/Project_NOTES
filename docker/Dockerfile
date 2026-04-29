# ============================================
# Stage 1: Сборка фронтенда (Vue)
# ============================================
FROM node:22-alpine AS frontend-build

WORKDIR /app
COPY notes_frontend/notes-vue-app/package*.json ./
RUN npm install
COPY notes_frontend/notes-vue-app/ .
RUN rm -rf dist
RUN npm run build

# ============================================
# Stage 2: Финальный образ с Django + Vue
# ============================================
FROM python:3.11-slim

WORKDIR /app

COPY notes/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY notes/ /app/notes/

WORKDIR /app/notes

RUN mkdir -p /app/notes/static/frontend
RUN rm -rf /app/notes/static/frontend/*
COPY --from=frontend-build /app/dist /app/notes/static/frontend

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
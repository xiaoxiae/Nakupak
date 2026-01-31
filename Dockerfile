# Build frontend
FROM node:20-slim AS frontend
WORKDIR /app/frontend

ARG VITE_UMAMI_URL
ARG VITE_UMAMI_WEBSITE_ID
ARG VITE_UMAMI_DOMAINS

COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Runtime
FROM python:3.11-slim
WORKDIR /app

COPY backend/pyproject.toml ./backend/
RUN pip install --no-cache-dir ./backend

# App code
COPY backend/alembic.ini ./backend/alembic.ini
COPY backend/alembic ./backend/alembic
COPY backend/app ./backend/app
COPY --from=frontend /app/frontend/dist ./frontend/dist

RUN mkdir -p /app/data/uploads

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

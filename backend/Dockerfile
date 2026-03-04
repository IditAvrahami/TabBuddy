FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY backend/pyproject.toml backend/uv.lock /app/backend/
RUN cd /app/backend && uv sync --frozen --no-dev --no-install-project

COPY backend /app/backend

ENV DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/tabbuddy

EXPOSE 8000
CMD ["uv", "run", "--no-dev", "--project", "/app/backend", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

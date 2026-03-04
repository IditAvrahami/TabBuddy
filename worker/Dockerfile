FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY worker/pyproject.toml worker/uv.lock /app/worker/
RUN cd /app/worker && uv sync --frozen --no-install-project

COPY worker/ ./worker/
COPY backend/ ./backend/

ENV PYTHONPATH=/app

CMD ["uv", "run", "--project", "/app/worker", "python", "-m", "worker.main"]

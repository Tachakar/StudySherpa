FROM node:22-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim AS backend
COPY --from=ghcr.io/astral-sh/uv:0.13.8 /uv /uvx ./bin
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./
COPY README.md ./
RUN uv sync --locked --no-dev
COPY --from=frontend frontend/dist /app/frontend/dist
ENV FRONTEND_DIR="/app/frontend/dist"
ENV PATH="/app/.venv/bin/:$PATH"
RUN useradd app
USER app
EXPOSE 8000
CMD ["uvicorn", "studysherpa.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

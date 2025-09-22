# syntax=docker/dockerfile:1

# Build stage using uv for fast, pinned installs
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS build
WORKDIR /app

# Leverage layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source
COPY . .

# Final runtime image
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app

# System deps for scientific stack (numpy/pandas) — slim images need these
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libblas3 liblapack3 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=build /app/.venv /app/.venv

# Copy application source (no dev files)
COPY . .

# Default to dev-friendly config; override in production
ENV PORT=8000 \
    METEOSTAT_SECRET_DISABLE=1

EXPOSE 8000

# Run via Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "server:app"]


# syntax=docker/dockerfile:1
# Container image for the Project 1 Python application.
#
# Dependencies are installed only from uv.lock (`uv sync --frozen`), so the image
# runs the same pinned versions as local development and CI.
# Building requires uv.lock, which is created with `uv lock` once uv is installed.

ARG PYTHON_VERSION=3.12.4
ARG UV_VERSION=0.13.7

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

# --- Build stage: resolve nothing, install exactly what uv.lock specifies ---
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

COPY --from=uv /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Dependency layer first, so it is reused from cache when only code changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Application packages (keep in step with [tool.setuptools] packages).
COPY README.md ./
COPY api/ api/
COPY ingest/ ingest/
COPY retrieval/ retrieval/
COPY eval/ eval/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# --- Runtime stage: only the virtual environment, run as a non-root user ---
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

RUN useradd --create-home --uid 10001 app

WORKDIR /app
COPY --from=builder --chown=app:app /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app

# Temporary smoke check that the packages import; replaced by the FastAPI
# server command in P1-15.
CMD ["python", "-c", "import api, ingest, retrieval, eval; print('ok')"]

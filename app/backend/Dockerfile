# <----------------------------------------------------------------------------------------->
#  Stage 1: Base Runtime & Shared Dependencies
# <----------------------------------------------------------------------------------------->
FROM python:3.12-slim@sha256:dd29372629eeba2dd003fd9e9d35a5b8236c44727875a0364254b5127af88e65 AS base

# Install UV from official standalone binary
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_COMPILE_BYTECODE=1

# Layer base lockfile early for docker caching
COPY app/backend/requirements.txt ./requirements.txt

# Install locked production dependencies with BuildKit Caching
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --require-hashes --only-binary :all: \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-first-match \
    -r requirements.txt


# <----------------------------------------------------------------------------------------->
#  Stage 2: Development Target (Hot reload + testing)
# <----------------------------------------------------------------------------------------->
FROM base AS dev

COPY app/backend/requirements-dev.txt ./requirements-dev.txt

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --require-hashes \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-first-match \
    -r requirements-dev.txt

COPY app/__init__.py    /app/app/__init__.py
EXPOSE 8000

CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# <----------------------------------------------------------------------------------------->
#  Stage 3: Production Target (Self-contained)
# <----------------------------------------------------------------------------------------->

FROM base AS prod 

RUN useradd -r -u 10001 -g users -s /usr/sbin/nologin appuser

COPY app/__init__.py    /app/app/__init__.py
COPY app/artifact_store /app/app/artifact_store
COPY app/backend        /app/app/backend

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
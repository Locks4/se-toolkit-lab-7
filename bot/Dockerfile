# Dockerfile for Telegram Bot
# Uses uv for dependency management

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/

# ---
# Stage 1: Build the application
# ---
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy bot pyproject.toml and sync dependencies
COPY bot/pyproject.toml /app/bot/pyproject.toml
RUN --mount=type=cache,target=/root/.cache/uv \
    mkdir -p /app/bot && \
    cd /app/bot && \
    uv sync --no-install-project

# Copy bot source code
COPY bot/ /app/bot/

# Sync with all files to get the final environment
RUN --mount=type=cache,target=/root/.cache/uv \
    cd /app/bot && \
    uv sync

# ---
# Stage 2: Final image
# ---
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Setup non-root user
RUN groupadd --system --gid 999 nonroot && \
    useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the application from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Add venv to PATH
ENV PATH="/app/bot/.venv/bin:$PATH"

# Use non-root user
USER nonroot

WORKDIR /app/bot

# Run the bot
CMD ["python", "bot.py"]

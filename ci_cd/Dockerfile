# ==============================================================================
# Multi-Stage Production Dockerfile for Autonomous Finance Agent Gateway
# Security-hardened, non-root user, optimized with uv package manager
# ==============================================================================

# Stage 1: Build & Dependency Resolution
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, deterministic dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project specification files
COPY pyproject.toml .

# Install dependencies into virtual environment using uv
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN uv pip install --no-cache \
    fastapi==0.110.0 \
    uvicorn==0.28.0 \
    pydantic==2.6.4 \
    pydantic-settings==2.2.1 \
    pyyaml==6.0.1 \
    httpx==0.27.0 \
    opentelemetry-api==1.23.0 \
    opentelemetry-sdk==1.23.0

# Stage 2: Final Minimal Runtime
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8080

# Security: Create non-root unprivileged service account user
RUN groupadd -r -g 1001 fpauser && \
    useradd -r -u 1001 -g fpauser -s /sbin/nologin -d /app fpauser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source code and configuration
COPY src/ /app/src/
COPY configs/ /app/configs/

# Set ownership to unprivileged user
RUN chown -R fpauser:fpauser /app

USER fpauser

EXPOSE 8080

# Health check probe
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/v1/health')" || exit 1

# Production WSGI/ASGI invocation
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2", "--loop", "uvloop", "--proxy-headers"]

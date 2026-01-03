# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Create virtual environment and install dependencies
RUN uv venv /app/.venv && \
    uv sync --frozen --no-dev

# Download spaCy German model
RUN /app/.venv/bin/python -m spacy download de_core_news_sm

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source
COPY src/ ./src/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "pii_shield.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

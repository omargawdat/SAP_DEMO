# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files needed for installation
COPY pyproject.toml uv.lock* README.md ./
COPY src/ ./src/

# Create virtual environment, install dependencies, and install the package
RUN uv venv /app/.venv && \
    uv sync --frozen --no-dev && \
    uv pip install .

# Install spaCy German medium model (good balance of accuracy and speed)
RUN uv pip install --python /app/.venv/bin/python https://github.com/explosion/spacy-models/releases/download/de_core_news_md-3.8.0/de_core_news_md-3.8.0-py3-none-any.whl

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder (includes installed package)
COPY --from=builder /app/.venv /app/.venv

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
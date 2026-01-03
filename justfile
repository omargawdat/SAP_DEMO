# Default recipe
default:
    @just --list

# First time setup (run after cloning)
setup: install setup-hooks
    @echo "Setup complete!"
    @echo "Run 'just download-model' if you need German NER support"

# Install dependencies
install:
    uv sync --all-extras

# Run tests
test *args:
    uv run pytest {{args}}

# Run tests with coverage
test-cov:
    uv run pytest --cov=pii_shield --cov-report=term-missing

# Run linter
lint:
    uv run ruff check src tests

# Fix linting issues
lint-fix:
    uv run ruff check --fix src tests

# Format code
format:
    uv run ruff format src tests

# Check formatting
format-check:
    uv run ruff format --check src tests

# Run all checks (lint + format + test)
check: lint format-check test

# Setup pre-commit hooks (pre-commit, commit-msg, pre-push)
setup-hooks:
    uv run pre-commit install --install-hooks -t pre-commit -t commit-msg -t pre-push

# Run pre-commit on all files
pre-commit:
    uv run pre-commit run --all-files

# Download spaCy German model
download-model:
    uv run python -m spacy download de_core_news_sm

# Run the API server
serve:
    uv run uvicorn pii_shield.api.main:app --reload

# Run Streamlit demo
demo:
    uv run streamlit run demo/app.py

# Build Docker image
docker-build:
    docker build -t pii-shield .

# Run Docker container
docker-run:
    docker run -p 8000:8000 pii-shield

# Build all Docker Compose services
compose-build:
    docker compose build

# Start all services (API + UI)
compose-up:
    docker compose up

# Start all services in detached mode
compose-up-d:
    docker compose up -d

# Stop all services
compose-down:
    docker compose down

# Clean build artifacts
clean:
    rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist build *.egg-info
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

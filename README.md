# PII Shield

Intelligent de-identification service for detecting and removing Personally Identifiable Information (PII).

## Quick Start

```bash
just setup
```

## Optional: German NER Support

If you need German name/address detection via Presidio:

```bash
just download-model
```

## Available Commands

```bash
just              # Show all commands
just test         # Run tests
just lint         # Check code style
just format       # Format code
just serve        # Run API server
```

## Docker

### Single Container (API only)

```bash
just docker-build   # Build image
just docker-run     # Run on port 8000
```

Then visit `http://localhost:8000`

### Docker Compose (API + UI)

Run both the API and Streamlit UI together:

```bash
just compose-build  # Build all images
just compose-up     # Start all services
```

Then visit:
- API: `http://localhost:8000`
- UI: `http://localhost:8501`

```bash
just compose-down   # Stop all services
```

### Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│   FastAPI API   │
│   (port 8501)   │     │   (port 8000)   │
└─────────────────┘     └─────────────────┘
    Dockerfile.ui           Dockerfile
```

Each service has its own optimized Docker image for independent scaling.

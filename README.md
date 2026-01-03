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

Build and run the containerized API:

```bash
just docker-build   # Build image
just docker-run     # Run on port 8000
```

Then visit `http://localhost:8000`

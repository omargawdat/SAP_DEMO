<div align="center">
  <img src="sap.svg" alt="SAP" width="100"/>
  <h1>PII Shield</h1>
  <p><strong>Intelligent De-identification Service for German PII Detection</strong></p>
  <p>
    <img src="https://img.shields.io/badge/python-3.13+-blue.svg" alt="Python 3.13+"/>
    <img src="https://img.shields.io/badge/FastAPI-0.115+-green.svg" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker"/>
    <img src="https://img.shields.io/badge/AWS-App%20Runner-orange.svg" alt="AWS"/>
    <img src="https://img.shields.io/badge/Presidio-ML-purple.svg" alt="Presidio"/>
    <img src="https://img.shields.io/badge/Claude-AI-red.svg" alt="Claude AI"/>
  </p>
</div>

---

A production-ready PII detection and de-identification service built for the **SAP EDT Data Protection team**. Features German-specific PII patterns (IBAN, Personalausweis, German phone formats), ML-powered named entity recognition, and optional LLM validation for context-aware detection.

## Key Features

| Feature | Description |
|---------|-------------|
| **8 PII Detectors** | Rule-based + ML + LLM validation |
| **German Focus** | IBAN (MOD-97), Personalausweis (check digit), German phone formats |
| **3 Strategies** | Redaction, Masking, Hashing (GDPR pseudonymization) |
| **Human-in-the-Loop** | Interactive review for low-confidence detections |
| **REST API** | FastAPI with OpenAPI docs |
| **Interactive Demo** | Streamlit UI with analytics dashboard |
| **Production Ready** | Docker, CI/CD, AWS deployment, comprehensive tests |

---

## Quick Start

### Docker Compose (Recommended)

```bash
# Clone and start
git clone <repo-url> && cd SAP_DEOM
docker compose -f docker-compose-local.yml up --build
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Demo UI: http://localhost:8501

### Local Development

```bash
# Prerequisites: Python 3.13+, uv
just setup                    # Install dependencies + pre-commit hooks
just download-model           # Download German NER model (optional)
cp .env.example .env          # Configure environment

just serve                    # Start API on :8000
just demo                     # Start Streamlit on :8501
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              PII Shield Pipeline                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  INPUT TEXT                                                                  │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         DETECTORS (Parallel)                         │    │
│  ├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┤    │
│  │   Email     │   Phone     │    IBAN     │  German ID  │ Credit Card │    │
│  │   (Regex)   │  (+49/0xxx) │  (MOD-97)   │(Check Digit)│   (Luhn)    │    │
│  ├─────────────┼─────────────┼─────────────┴─────────────┴─────────────┤    │
│  │ IP Address  │  Presidio   │           LLM Validator                 │    │
│  │ (IPv4/IPv6) │(German NER) │         (Claude AI)                     │    │
│  └─────────────┴─────────────┴─────────────────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  DEDUPLICATION ──► Keep highest confidence per position                      │
│       │                                                                      │
│       ▼                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      STRATEGY APPLICATION                            │    │
│  ├───────────────────┬───────────────────┬─────────────────────────────┤    │
│  │    Redaction      │     Masking       │         Hashing             │    │
│  │    [EMAIL]        │    han***com      │      a7f3d2c1...            │    │
│  └───────────────────┴───────────────────┴─────────────────────────────┘    │
│       │                                                                      │
│       ▼                                                                      │
│  OUTPUT: Processed text + Detection report + Metadata                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/detect` | POST | Detect PII in text (with optional LLM validation) |
| `/api/v1/anonymize` | POST | Apply de-identification strategy to matches |
| `/api/v1/process` | POST | One-shot detect + anonymize |
| `/api/v1/process-csv` | POST | Batch process CSV file |
| `/api/v1/process-json` | POST | Batch process JSON file |
| `/api/v1/health` | GET | Health check |

### Example

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contact Hans Mueller at hans@sap.com or +49 170 1234567. IBAN: DE89370400440532013000",
    "strategy": "redaction"
  }'
```

**Response:**
```json
{
  "original_text": "Contact Hans Mueller at hans@sap.com or +49 170 1234567. IBAN: DE89370400440532013000",
  "processed_text": "Contact [NAME] at [EMAIL] or [PHONE]. IBAN: [IBAN]",
  "matches": [
    {"type": "NAME", "text": "Hans Mueller", "confidence": 0.85, "detector": "presidio"},
    {"type": "EMAIL", "text": "hans@sap.com", "confidence": 1.0, "detector": "email"},
    {"type": "PHONE", "text": "+49 170 1234567", "confidence": 1.0, "detector": "phone"},
    {"type": "IBAN", "text": "DE89370400440532013000", "confidence": 1.0, "detector": "iban"}
  ],
  "summary": {"pii_found": true, "total_count": 4}
}
```

---

## Detectors

| Detector | Type | German Specific | Validation Method |
|----------|------|-----------------|-------------------|
| **Email** | Regex | - | RFC 5322 pattern |
| **Phone** | Regex | `+49`, `0xxx`, mobile prefixes | Min 10 digits, known area codes |
| **IBAN** | Regex + Math | DE format (22 chars) | **MOD-97 checksum** |
| **German ID** | Regex + Math | Personalausweis (L-Y prefix) | **Check digit algorithm** |
| **Credit Card** | Regex + Math | - | **Luhn algorithm** |
| **IP Address** | Regex | - | IPv4/IPv6 validation |
| **Presidio** | ML/NER | German spaCy model | Named entity recognition |
| **LLM Validator** | Claude API | German context | Context-aware validation |

### German-Specific Patterns

**IBAN Validation (MOD-97):**
```
DE89 3704 0044 0532 0130 00
│  │    └─────────────────── Bank account number
│  └─────────────────────── Check digits (validated)
└────────────────────────── Country code
```

**Personalausweis Validation:**
```
L01X00T471
│        └── Check digit (weighted sum mod 10)
└─────────── Issuing authority (L-Y)
```

---

## De-identification Strategies

| Strategy | Output Example | Use Case |
|----------|----------------|----------|
| **Redaction** | `hans@sap.com` → `[EMAIL]` | Full privacy - complete removal |
| **Masking** | `hans@sap.com` → `han***com` | Partial visibility for debugging |
| **Hashing** | `hans@sap.com` → `a7f3d2c1e9b4` | GDPR pseudonymization (re-linkable with salt) |

---

## Interactive Demo

The Streamlit demo provides a **3-step Human-in-the-Loop workflow**:

1. **Analyze** - Input text, select LLM model (None/Haiku/Sonnet/Opus)
2. **Review** - Adjust confidence threshold, approve/reject low-confidence matches
3. **Result** - View before/after comparison with analytics

**Features:**
- Confidence threshold slider for auto-approval
- Color-coded PII highlighting with tooltips
- Analytics dashboard (Precision, Recall, F1 metrics)
- API transparency panels

```bash
just demo                                    # Local
docker compose -f docker-compose-local.yml up ui  # Docker
```

---

## Technology Stack

| Category | Technologies |
|----------|--------------|
| **Core** | Python 3.13+, uv, ruff, pytest, pre-commit |
| **ML/AI** | Presidio, spaCy (German NER), Anthropic Claude API |
| **API** | FastAPI, Pydantic v2, uvicorn |
| **Demo** | Streamlit, Plotly |
| **DevOps** | Docker (multi-stage), GitHub Actions |
| **Cloud** | AWS App Runner, ECR, Secrets Manager, Terraform |

---

## Development

```bash
just                  # Show all commands
just setup            # Initial setup (install + hooks)
just test             # Run pytest
just test-cov         # Run with coverage report
just lint             # Check code style (ruff)
just format           # Format code (ruff)
just check            # Run all checks (lint + format + test)
just serve            # Start API with hot reload
just demo             # Start Streamlit demo
just compose-up       # Start Docker Compose stack
just compose-down     # Stop Docker Compose stack
```

### Pre-commit Hooks

Automatically runs on commit/push:
- **ruff** - Linting and formatting
- **gitleaks** - Secret detection
- **bandit** - Security scanning
- **pytest** - Tests on push

---

## Project Structure

```
SAP_DEOM/
├── src/pii_shield/
│   ├── core/              # PIIType, PIIMatch, DetectionResult
│   ├── detectors/         # 8 detector implementations
│   ├── strategies/        # Redaction, Masking, Hashing
│   ├── preprocessing/     # Text normalization
│   ├── pipeline/          # TextProcessor orchestration
│   └── api/               # FastAPI routes, models, middleware
├── tests/                 # Mirrors src structure
├── demo/                  # Streamlit application
├── infrastructure/
│   └── terraform/         # AWS IaC (ECR, App Runner, IAM)
├── Dockerfile             # Multi-stage (builder → test → prod)
├── Dockerfile.ui          # Streamlit image
├── docker-compose-local.yml
├── pyproject.toml         # Dependencies and tool config
├── justfile               # Command runner
└── .github/workflows/     # CI/CD pipeline
```

---

## AWS Deployment

The infrastructure uses **AWS App Runner** for serverless container deployment:

```
GitHub Push → CI/CD → ECR → App Runner (auto-deploy)
```

**Resources:**
- **ECR**: Container registry with lifecycle policy
- **App Runner**: 512 CPU, 1024MB RAM, auto-scaling
- **Secrets Manager**: ANTHROPIC_API_KEY storage
- **Terraform**: Infrastructure as Code

See [`infrastructure/README.md`](infrastructure/README.md) for deployment guide.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Optional | Claude API key for LLM validation. Get at [console.anthropic.com](https://console.anthropic.com/) |

```bash
cp .env.example .env
# Edit .env with your API key
```

> **Note:** LLM validation is optional. Without an API key, the system uses rule-based and ML detection only.

---

## License

MIT License

---

<div align="center">
  <sub>Built for <strong>SAP EDT Data Protection Team</strong> - Working Student Position Demo</sub>
</div>

# PII Shield - Development Guidelines

## Context

See `requirements.xml` for full project requirements and specifications.

## Project Structure

```
src/pii_shield/           # Main package (PEP 517 src layout)
├── core/                 # Shared types: PIIType, PIIMatch, DetectionResult
├── detectors/            # PII detection (rule-based + ML/Presidio)
├── strategies/           # De-identification: redaction, masking, hashing
├── preprocessing/        # Text normalization, encoding, chunking
├── pipeline/             # Data processing: CSV, JSON, text + reports
└── api/                  # FastAPI service
tests/                    # Mirrors src structure
demo/                     # Streamlit demo
notebooks/                # Databricks/PySpark notebooks
```

## Technology Stack

- **Core**: Python 3.13+, uv, pytest, pre-commit, just, ruff
- **ML**: presidio-analyzer, presidio-anonymizer, spaCy (German model)
- **API**: FastAPI, Pydantic v2
- **Deploy**: Docker, GitHub Actions
- **Demo**: Streamlit, Databricks Community Edition

## Key Patterns

- Imports: `from pii_shield.detectors import EmailDetector`
- All detectors inherit from `Detector` ABC in `detectors/base.py`
- All strategies inherit from `Strategy` ABC in `strategies/base.py`
- All preprocessors inherit from `Preprocessor` ABC in `preprocessing/base.py`
- Shared types in `core/`: `PIIType` (enum), `PIIMatch` (dataclass)

## Development Principles

- Use modern, recommended approaches
- Keep it simple - avoid over-engineering
- Prefer standard library over external dependencies when possible
- Write clean, readable code over clever code
- Only add complexity when it solves a real problem

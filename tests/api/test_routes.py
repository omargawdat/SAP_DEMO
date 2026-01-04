"""Tests for API routes."""

from fastapi.testclient import TestClient

from pii_shield.api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_200(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_response_structure(self):
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestDetectEndpoint:
    """Tests for /api/v1/detect endpoint."""

    def test_detect_finds_email(self):
        response = client.post("/api/v1/detect", json={"text": "Contact hans@sap.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["pii_found"] is True
        assert data["summary"]["total_count"] == 1
        assert len(data["matches"]) == 1
        assert data["matches"][0]["type"] == "EMAIL"

    def test_detect_no_pii(self):
        response = client.post("/api/v1/detect", json={"text": "Hello world"})
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["pii_found"] is False
        assert data["summary"]["total_count"] == 0

    def test_detect_multiple_emails(self):
        response = client.post(
            "/api/v1/detect", json={"text": "Email a@b.com or c@d.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_count"] == 2

    def test_detect_empty_text_rejected(self):
        response = client.post("/api/v1/detect", json={"text": ""})
        assert response.status_code == 422  # Validation error

    def test_detect_returns_processing_time(self):
        response = client.post("/api/v1/detect", json={"text": "test@example.com"})
        data = response.json()
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] >= 0

    def test_detect_includes_review_required_field(self):
        """Matches include review_required based on confidence threshold."""
        response = client.post("/api/v1/detect", json={"text": "test@example.com"})
        data = response.json()
        assert "review_required" in data["matches"][0]
        # Email detector has confidence 1.0, so review_required should be False
        assert data["matches"][0]["review_required"] is False


class TestAnonymizeEndpoint:
    """Tests for /api/v1/anonymize endpoint - requires explicit matches."""

    def test_anonymize_with_matches(self):
        """Anonymize with explicitly provided matches."""
        response = client.post(
            "/api/v1/anonymize",
            json={
                "text": "Contact hans@sap.com for help.",
                "matches": [{"type": "EMAIL", "start": 8, "end": 20}],
                "strategy": "redaction",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed_text"] == "Contact [EMAIL] for help."
        assert data["original_text"] == "Contact hans@sap.com for help."
        assert data["summary"]["total_count"] == 1
        assert data["matches"][0]["detector"] == "manual"

    def test_anonymize_requires_matches(self):
        """Matches field is required."""
        response = client.post(
            "/api/v1/anonymize",
            json={"text": "Contact hans@sap.com", "strategy": "redaction"},
        )
        assert response.status_code == 422  # Validation error - matches required

    def test_anonymize_invalid_strategy(self):
        response = client.post(
            "/api/v1/anonymize",
            json={
                "text": "test",
                "matches": [{"type": "EMAIL", "start": 0, "end": 4}],
                "strategy": "invalid",
            },
        )
        assert response.status_code == 422  # Validation error from Literal type

    def test_anonymize_partial_matches(self):
        """Only anonymize specific matches, not all PII."""
        text = "Email a@b.com or c@d.com"
        # Only anonymize first email
        response = client.post(
            "/api/v1/anonymize",
            json={
                "text": text,
                "matches": [{"type": "EMAIL", "start": 6, "end": 13}],
                "strategy": "redaction",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed_text"] == "Email [EMAIL] or c@d.com"
        assert data["summary"]["total_count"] == 1

    def test_anonymize_returns_summary(self):
        response = client.post(
            "/api/v1/anonymize",
            json={
                "text": "Email hans@sap.com",
                "matches": [{"type": "EMAIL", "start": 6, "end": 18}],
            },
        )
        data = response.json()
        assert data["summary"]["pii_found"] is True
        assert data["summary"]["by_type"]["EMAIL"] == 1


class TestProcessEndpoint:
    """Tests for /api/v1/process endpoint - one-shot detect + anonymize."""

    def test_process_detects_and_anonymizes(self):
        """Process endpoint detects and anonymizes in one call."""
        response = client.post(
            "/api/v1/process",
            json={"text": "Contact hans@sap.com", "strategy": "redaction"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed_text"] == "Contact [EMAIL]"
        assert data["original_text"] == "Contact hans@sap.com"
        assert data["matches"][0]["detector"] == "email"

    def test_process_default_strategy(self):
        """Default strategy is redaction."""
        response = client.post("/api/v1/process", json={"text": "Contact hans@sap.com"})
        assert response.status_code == 200
        data = response.json()
        assert data["processed_text"] == "Contact [EMAIL]"

    def test_process_with_min_confidence(self):
        """Filter matches by confidence threshold."""
        # Email detector returns confidence 1.0, so setting threshold to 0.99 should include it
        response = client.post(
            "/api/v1/process",
            json={
                "text": "Contact hans@sap.com",
                "strategy": "redaction",
                "min_confidence": 0.99,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed_text"] == "Contact [EMAIL]"
        assert data["summary"]["total_count"] == 1

    def test_process_high_confidence_filters_out_matches(self):
        """High confidence threshold filters out low-confidence matches."""
        # Email detector returns confidence 1.0, threshold > 1.0 filters everything
        response = client.post(
            "/api/v1/process",
            json={
                "text": "Contact hans@sap.com",
                "strategy": "redaction",
                "min_confidence": 1.01,  # Higher than any possible confidence
            },
        )
        # Should fail validation since max is 1.0
        assert response.status_code == 422

    def test_process_no_pii(self):
        """Process text without PII."""
        response = client.post(
            "/api/v1/process", json={"text": "Hello world", "strategy": "redaction"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed_text"] == "Hello world"
        assert data["summary"]["pii_found"] is False

    def test_process_invalid_strategy(self):
        response = client.post(
            "/api/v1/process", json={"text": "test", "strategy": "invalid"}
        )
        assert response.status_code == 422

    def test_process_returns_summary(self):
        response = client.post(
            "/api/v1/process", json={"text": "Email hans@sap.com and anna@sap.de"}
        )
        data = response.json()
        assert data["summary"]["pii_found"] is True
        assert data["summary"]["total_count"] == 2
        assert data["summary"]["by_type"]["EMAIL"] == 2

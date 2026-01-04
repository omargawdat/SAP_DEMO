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


class TestAnonymizeEndpoint:
    """Tests for /api/v1/anonymize endpoint."""

    def test_anonymize_redacts_email(self):
        response = client.post(
            "/api/v1/anonymize",
            json={"text": "Contact hans@sap.com", "strategy": "redaction"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed_text"] == "Contact [EMAIL]"
        assert data["original_text"] == "Contact hans@sap.com"

    def test_anonymize_default_strategy(self):
        response = client.post(
            "/api/v1/anonymize", json={"text": "Contact hans@sap.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["processed_text"] == "Contact [EMAIL]"

    def test_anonymize_invalid_strategy(self):
        response = client.post(
            "/api/v1/anonymize",
            json={"text": "test", "strategy": "invalid"},
        )
        assert response.status_code == 422  # Validation error from Literal type

    def test_anonymize_returns_summary(self):
        response = client.post(
            "/api/v1/anonymize", json={"text": "Email hans@sap.com"}
        )
        data = response.json()
        assert data["summary"]["pii_found"] is True
        assert data["summary"]["by_type"]["EMAIL"] == 1

import pytest
from fastapi.testclient import TestClient


class TestWebhookEndpoints:
    """Test webhook endpoints."""

    def test_realestate_webhook_success(
        self,
        client: TestClient,
        valid_api_key: str,
        sample_realestate_payload: dict,
    ) -> None:
        """Test successful real estate webhook."""
        response = client.post(
            "/webhook/realestate",
            json=sample_realestate_payload,
            headers={"X-Api-Key": valid_api_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "posted"

    def test_realestate_webhook_missing_api_key(
        self,
        client: TestClient,
        sample_realestate_payload: dict,
    ) -> None:
        """Test webhook without API key."""
        response = client.post(
            "/webhook/realestate",
            json=sample_realestate_payload,
        )

        assert response.status_code == 401

    def test_realestate_webhook_invalid_api_key(
        self,
        client: TestClient,
        sample_realestate_payload: dict,
    ) -> None:
        """Test webhook with invalid API key."""
        response = client.post(
            "/webhook/realestate",
            json=sample_realestate_payload,
            headers={"X-Api-Key": "invalid-key"},
        )

        assert response.status_code == 401

    def test_realestate_webhook_validation_error(
        self,
        client: TestClient,
        valid_api_key: str,
    ) -> None:
        """Test webhook with invalid payload."""
        response = client.post(
            "/webhook/realestate",
            json={"id": "test"},  # Missing required fields
            headers={"X-Api-Key": valid_api_key},
        )

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    def test_realestate_webhook_batch(
        self,
        client: TestClient,
        valid_api_key: str,
        sample_realestate_payload: dict,
    ) -> None:
        """Test batch webhook endpoint."""
        payloads = [
            sample_realestate_payload,
            {**sample_realestate_payload, "id": "xyz789"},
        ]

        response = client.post(
            "/webhook/realestate/batch",
            json=payloads,
            headers={"X-Api-Key": valid_api_key},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client: TestClient) -> None:
        """Test main health endpoint."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["ok", "degraded"]
        assert "version" in data
        assert "checks" in data

    def test_readiness_check(self, client: TestClient) -> None:
        """Test readiness endpoint."""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_liveness_check(self, client: TestClient) -> None:
        """Test liveness endpoint."""
        response = client.get("/api/v1/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"

    def test_legacy_health_endpoint(self, client: TestClient) -> None:
        """Test legacy health endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

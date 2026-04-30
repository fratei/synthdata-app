"""Tests for SynthData API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests for /health."""

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SynthData"


class TestGenerateEndpoint:
    """Tests for POST /api/v1/generate."""

    def test_generate_tabular(self):
        payload = {
            "data_type": "tabular",
            "schema_definition": {
                "columns": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                ]
            },
            "count": 10,
            "output_format": "json",
        }
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"

    def test_generate_text(self):
        payload = {
            "data_type": "text",
            "count": 5,
            "text_options": {
                "domain": "finance",
                "tone": "formal",
                "document_type": "email",
            },
        }
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 200

    def test_generate_invalid_count(self):
        payload = {
            "data_type": "tabular",
            "count": 0,
        }
        response = client.post("/api/v1/generate", json=payload)
        assert response.status_code == 422


class TestSchemasEndpoint:
    """Tests for GET /api/v1/schemas."""

    def test_list_schemas(self):
        response = client.get("/api/v1/schemas")
        assert response.status_code == 200
        schemas = response.json()
        assert len(schemas) >= 3
        assert any(s["id"] == "users" for s in schemas)


class TestJobsEndpoint:
    """Tests for GET /api/v1/jobs/{job_id}."""

    def test_get_job_status(self):
        # First, create a job
        payload = {"data_type": "tabular", "count": 10}
        create_resp = client.post("/api/v1/generate", json=payload)
        job_id = create_resp.json()["job_id"]

        # Then check its status
        response = client.get(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["job_id"] == job_id

    def test_get_nonexistent_job(self):
        response = client.get("/api/v1/jobs/nonexistent-id")
        assert response.status_code == 404


class TestDatasetsEndpoint:
    """Tests for GET /api/v1/datasets/{dataset_id}."""

    def test_get_nonexistent_dataset(self):
        response = client.get("/api/v1/datasets/nonexistent-id")
        assert response.status_code == 404

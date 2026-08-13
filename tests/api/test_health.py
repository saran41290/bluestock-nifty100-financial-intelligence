"""
API unit test for /api/v1/health endpoint (Sprint 6 Day 42).
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_endpoint_200():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert "db_row_counts" in data
    assert len(data["db_row_counts"]) >= 7

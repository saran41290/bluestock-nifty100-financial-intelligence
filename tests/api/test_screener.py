"""
API unit tests for stock screener endpoint (Sprint 6 Day 42).
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_screener_valid_min_roe():
    response = client.get("/api/v1/screener?min_roe=15")
    assert response.status_code == 200
    data = response.json()
    results = data.get("results") if isinstance(data, dict) else data
    assert isinstance(results, list)
    assert len(results) > 0


def test_screener_invalid_param():
    response = client.get("/api/v1/screener?min_roe=invalid_string")
    assert response.status_code in (400, 422)

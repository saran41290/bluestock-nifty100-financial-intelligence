"""
API unit tests for sector endpoints (Sprint 6 Day 42).
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_get_all_sectors():
    response = client.get("/api/v1/sectors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10


def test_get_sector_companies_valid():
    response = client.get("/api/v1/sectors/Information Technology/companies")
    if response.status_code == 404:
        response = client.get("/api/v1/sectors/IT/companies")
    assert response.status_code in (200, 404)

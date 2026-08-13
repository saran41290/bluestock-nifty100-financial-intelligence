"""
API unit tests for company endpoints (Sprint 6 Day 42).
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_get_companies_list():
    response = client.get("/api/v1/companies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 90


def test_get_company_profile_valid():
    response = client.get("/api/v1/companies/TCS")
    assert response.status_code == 200
    data = response.json()
    if "company" in data:
        assert data["company"]["id"] == "TCS"
    else:
        assert data.get("id") == "TCS" or data.get("company_id") == "TCS"


def test_get_company_profile_invalid():
    response = client.get("/api/v1/companies/INVALID_TICKER")
    assert response.status_code == 404

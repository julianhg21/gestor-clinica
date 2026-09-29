import os

import httpx
import pytest

BASE = os.getenv("STAGING_BASE_URL", "").rstrip("/")


pytestmark = pytest.mark.integration


@pytest.mark.skipif(not BASE, reason="Defina STAGING_BASE_URL para ejecutar integración")
def test_staging_web_is_available():
    response = httpx.get(BASE + "/", timeout=10)
    assert response.status_code == 200
    assert "DUALITY" in response.text


@pytest.mark.skipif(not BASE, reason="Defina STAGING_BASE_URL para ejecutar integración")
def test_auth_health_through_reverse_proxy():
    response = httpx.get(BASE + "/api/auth/health", timeout=10)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.skipif(not BASE, reason="Defina STAGING_BASE_URL para ejecutar integración")
def test_protected_catalog_requires_authentication():
    response = httpx.get(BASE + "/api/catalogo/patients", timeout=10)
    assert response.status_code == 401

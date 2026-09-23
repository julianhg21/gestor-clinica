import os
import pytest
import httpx

BASE = os.getenv("SMOKE_BASE_URL")


@pytest.mark.skipif(not BASE, reason="Defina SMOKE_BASE_URL para ejecutar la prueba contra Docker")
def test_web_is_reachable():
    response = httpx.get(BASE, timeout=5)
    assert response.status_code == 200
    assert "DUALITY" in response.text

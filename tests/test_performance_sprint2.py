import os
import statistics
import time

import httpx
import pytest

BASE = os.getenv("STAGING_BASE_URL", "").rstrip("/")


@pytest.mark.performance
@pytest.mark.skipif(not BASE, reason="Defina STAGING_BASE_URL para ejecutar rendimiento")
def test_auth_health_average_response_under_two_seconds():
    samples = []
    with httpx.Client(timeout=10) as client:
        for _ in range(5):
            start = time.perf_counter()
            response = client.get(BASE + "/api/auth/health")
            samples.append(time.perf_counter() - start)
            assert response.status_code == 200
    assert statistics.mean(samples) < 2.0

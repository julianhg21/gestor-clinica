from pathlib import Path

TEXT = (Path(__file__).resolve().parents[1] / "docker-compose.yml").read_text(encoding="utf-8")


def test_compose_contains_required_services():
    for service in ["postgres:", "redis:", "auth:", "catalog:", "orders:", "payments:"]:
        assert service in TEXT

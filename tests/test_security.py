import pytest
import redis
from fastapi import HTTPException

from common import security
from common.security import hash_password, verify_password


def test_password_roundtrip():
    encoded = hash_password("Prueba123!", iterations=10_000)
    assert verify_password("Prueba123!", encoded)
    assert not verify_password("incorrecta", encoded)


def _token():
    return security.create_access_token({
        "id_usuario": "test-user", "correo": "test@example.invalid",
        "nombre_completo": "Cuenta de prueba", "id_rol": "ROL_ADMIN",
    })


def test_token_accepted_when_revocation_store_is_available(monkeypatch):
    monkeypatch.setattr(security._redis, "get", lambda *_args, **_kwargs: None)
    assert security.decode_token(_token())["sub"] == "test-user"


def test_logout_records_revocation_when_store_is_available(monkeypatch):
    recorded = []
    monkeypatch.setattr(security._redis, "setex", lambda *args: recorded.append(args))
    security.revoke_token({"jti": "test-jti", "exp": 4_102_444_800})
    assert recorded[0][0] == "revoked:test-jti"
    assert recorded[0][1] > 0


def test_token_rejected_when_revocation_store_is_unavailable(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise redis.ConnectionError("unavailable")

    monkeypatch.setattr(security._redis, "get", unavailable)
    with pytest.raises(HTTPException) as exc:
        security.decode_token(_token())
    assert exc.value.status_code == 503


def test_logout_does_not_claim_success_when_revocation_fails(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise redis.ConnectionError("unavailable")

    monkeypatch.setattr(security._redis, "setex", unavailable)
    payload = {"jti": "test-jti", "exp": 4_102_444_800}
    with pytest.raises(HTTPException) as exc:
        security.revoke_token(payload)
    assert exc.value.status_code == 503

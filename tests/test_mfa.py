from contextlib import contextmanager

import jwt
import pytest
import redis
from fastapi import HTTPException

from auth import main as auth
from common import mfa, security
from common.config import settings


ADMIN = {
    "id_usuario": "USR_TEST", "id_rol": "ROL_ADMIN",
    "nombre_completo": "Doctora de prueba", "correo": "test@example.invalid",
    "activo": True, "password_hash": "test-hash",
    "requiere_cambio_password": False, "secret_ciphertext": "encrypted",
}


def test_totp_rfc_vector_single_use_and_window():
    # RFC 6238 SHA-1 vector at Unix time 59, truncated to six digits.
    secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
    assert mfa.match_step(secret, "287082", None, now=59) == 1
    assert mfa.match_step(secret, "287082", 1, now=59) is None
    assert mfa.match_step(secret, "287082", None, now=120) is None
    assert mfa.match_step(secret, "28a082", None, now=59) is None


def test_mfa_secret_encrypted_and_bound_to_user():
    secret = mfa.new_secret()
    ciphertext = mfa.encrypt_secret(secret, "USR_TEST")
    assert secret not in ciphertext
    assert mfa.decrypt_secret(ciphertext, "USR_TEST") == secret
    with pytest.raises(HTTPException) as exc:
        mfa.decrypt_secret(ciphertext, "OTHER")
    assert exc.value.status_code == 503


def test_admin_token_requires_verified_factor(monkeypatch):
    with pytest.raises(ValueError):
        security.create_access_token(ADMIN)
    old_token = jwt.encode({"sub": "USR_TEST", "role": "ROL_ADMIN", "jti": "legacy"}, settings.jwt_secret, algorithm="HS256")
    with pytest.raises(HTTPException) as exc:
        security.decode_token(old_token)
    assert exc.value.status_code == 401
    monkeypatch.setattr(security._redis, "get", lambda *_: None)
    verified = security.create_access_token(ADMIN, mfa_verified=True)
    assert security.decode_token(verified)["amr"] == ["pwd", "otp"]


def test_mfa_challenge_cannot_authorize_protected_api(monkeypatch):
    monkeypatch.setattr(security._redis, "get", lambda *_: None)
    challenge = mfa.create_challenge("USR_TEST", "mfa_verify")
    with pytest.raises(HTTPException) as exc:
        security.decode_token(challenge)
    assert exc.value.status_code == 401


def test_password_only_admin_login_never_returns_session(monkeypatch):
    monkeypatch.setattr(auth, "query_one", lambda *_: ADMIN)
    monkeypatch.setattr(auth, "verify_password", lambda *_: True)
    monkeypatch.setattr(auth, "check_attempts", lambda *_: None)
    monkeypatch.setattr(auth, "create_challenge", lambda *_: "short-lived-challenge")
    response = auth.login(auth.LoginRequest(correo=ADMIN["correo"], password="long-password"))
    assert response == {"mfa_required": True, "setup_required": False, "challenge_token": "short-lived-challenge"}
    assert "access_token" not in response


def test_demo_account_and_inactive_account_cannot_login(monkeypatch):
    monkeypatch.setattr(auth, "check_attempts", lambda *_: None)
    monkeypatch.setattr(auth, "verify_password", lambda *_: True)
    monkeypatch.setattr(auth, "query_one", lambda *_: {**ADMIN, "requiere_cambio_password": True})
    with pytest.raises(HTTPException) as exc:
        auth.login(auth.LoginRequest(correo=ADMIN["correo"], password="long-password"))
    assert exc.value.status_code == 403
    monkeypatch.setattr(auth, "query_one", lambda *_: {**ADMIN, "activo": False})
    monkeypatch.setattr(auth, "failed_attempt", lambda *_: None)
    with pytest.raises(HTTPException) as exc:
        auth.login(auth.LoginRequest(correo=ADMIN["correo"], password="long-password"))
    assert exc.value.status_code == 401


def test_attempt_limit_blocks_after_five_failures(monkeypatch):
    values = {}
    monkeypatch.setattr(mfa._redis, "get", lambda key: values.get(key))
    monkeypatch.setattr(mfa._redis, "set", lambda key, value, **_: values.setdefault(key, value))
    monkeypatch.setattr(mfa._redis, "incr", lambda key: values.__setitem__(key, str(int(values[key]) + 1)))
    for _ in range(5):
        mfa.failed_attempt("mfa", "USR_TEST")
    with pytest.raises(HTTPException) as exc:
        mfa.check_attempts("mfa", "USR_TEST")
    assert exc.value.status_code == 429


def test_login_fails_closed_if_attempt_store_unavailable(monkeypatch):
    def unavailable(*_):
        raise redis.ConnectionError("unavailable")

    monkeypatch.setattr(mfa._redis, "get", unavailable)
    with pytest.raises(HTTPException) as exc:
        mfa.check_attempts("password", ADMIN["correo"])
    assert exc.value.status_code == 503


def test_mfa_confirmation_requires_valid_code_and_rejects_reuse(monkeypatch):
    secret = mfa.new_secret()
    code = mfa._code_for_step(secret, int(mfa.time.time() // 30))
    user = {**ADMIN, "pending_ciphertext": None, "last_accepted_step": None}
    conn = type("FakeConnection", (), {})()
    conn.rowcount = 1
    conn.fetchone = lambda: user
    conn.execute = lambda *_: conn

    @contextmanager
    def fake_transaction():
        yield conn

    monkeypatch.setattr(auth, "transaction", fake_transaction)
    monkeypatch.setattr(auth, "decode_challenge", lambda *_: {"sub": "USR_TEST", "purpose": "mfa_verify"})
    monkeypatch.setattr(auth, "decrypt_secret", lambda *_: secret)
    monkeypatch.setattr(auth, "check_attempts", lambda *_: None)
    monkeypatch.setattr(auth, "clear_attempts", lambda *_: None)
    monkeypatch.setattr(auth, "failed_attempt", lambda *_: None)
    bad = auth.MfaConfirmRequest(challenge_token="x" * 20, code="000000")
    if code == "000000":
        bad.code = "111111"
    with pytest.raises(HTTPException) as exc:
        auth.confirm_mfa(bad)
    assert exc.value.status_code == 401
    good = auth.MfaConfirmRequest(challenge_token="x" * 20, code=code)
    response = auth.confirm_mfa(good)
    assert "access_token" in response
    assert jwt.decode(response["access_token"], settings.jwt_secret, algorithms=["HS256"])["amr"] == ["pwd", "otp"]
    user["last_accepted_step"] = int(mfa.time.time() // 30)
    with pytest.raises(HTTPException) as exc:
        auth.confirm_mfa(good)
    assert exc.value.status_code == 401

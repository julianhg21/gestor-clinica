"""Pruebas locales; Redis/BD simulados explícitamente, sin datos de pacientes."""
from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace

import jwt
import pytest
import redis
from fastapi import HTTPException
from fastapi.testclient import TestClient
from psycopg import OperationalError

import auth.main as auth
import common.security as sec
from common.config import settings
from catalogo.main import app as catalog
from pagos.main import app as payments
from pedidos.main import app as orders

pytestmark = pytest.mark.security
USER = {"id_usuario": "TEST_USER", "id_rol": "ROL_ADMIN", "nombre_completo": "Cuenta sintética", "correo": "test@example.com", "activo": True}


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    revoked = {}
    monkeypatch.setattr(sec._redis, "get", lambda key: revoked.get(key))
    monkeypatch.setattr(sec._redis, "setex", lambda key, ttl, value: revoked.__setitem__(key, value))
    monkeypatch.setattr(sec, "query_one", lambda *args: {"activo": True, "id_rol": "ROL_ADMIN"})


def token(**changes):
    now = int(datetime.now(timezone.utc).timestamp())
    payload = dict(sub="TEST_USER", role="ROL_ADMIN", jti="test-jti", iat=now, exp=now+300)
    payload.update(changes)
    return jwt.encode(payload, settings.jwt_secret, algorithm=sec.ALGORITHM)


def client(app=auth.app):
    # No context manager: lifespan no abre una BD real; sus accesos se sustituyen.
    return TestClient(app)


def headers(value=None):
    return {"Authorization": "Bearer " + (value or token())}


def test_password_salts_and_malformed_hashes():
    a, b = sec.hash_password("Synthetic123!"), sec.hash_password("Synthetic123!")
    assert a != b and sec.verify_password("Synthetic123!", a)
    for value in ["broken", "other$1$AA$AA", "pbkdf2_sha256$bad$AA$AA"]:
        assert not sec.verify_password("Synthetic123!", value)


@pytest.mark.parametrize("app,path", [(auth.app,"/api/users"),(catalog,"/api/catalogo/patients"),(orders,"/api/pedidos"),(payments,"/api/pagos")])
def test_missing_token_all_services(app, path):
    assert client(app).get(path).status_code == 401


@pytest.mark.parametrize("value", [token(exp=1), token(role=""), token(jti=[]), token(exp="9999999999"), token(iat=True), "invalid"], ids=["expired", "empty-role", "invalid-jti", "string-exp", "boolean-iat", "malformed"])
def test_invalid_tokens(value):
    assert client().get("/api/auth/me", headers=headers(value)).status_code == 401


@pytest.mark.parametrize("claim", ["sub", "exp", "iat", "jti", "role"])
def test_required_claims(claim):
    payload = jwt.decode(token(), settings.jwt_secret, algorithms=[sec.ALGORITHM])
    del payload[claim]
    value = jwt.encode(payload, settings.jwt_secret, algorithm=sec.ALGORITHM)
    assert client().get("/api/auth/me", headers=headers(value)).status_code == 401


def test_tampered_signature():
    value = jwt.encode({"sub":"test"}, "synthetic-different-key", algorithm="HS256")
    assert client().get("/api/auth/me", headers=headers(value)).status_code == 401


def test_logout_revokes_token():
    value = sec.create_access_token(USER)
    assert client().get("/api/auth/me", headers=headers(value)).status_code == 200
    assert client().post("/api/auth/logout", headers=headers(value)).status_code == 204
    assert client().get("/api/auth/me", headers=headers(value)).status_code == 401


@pytest.mark.parametrize("operation", ["get", "setex"])
def test_redis_failure_is_not_success(monkeypatch, operation):
    def fail(*args):
        raise redis.ConnectionError("synthetic outage")
    monkeypatch.setattr(sec._redis, operation, fail)
    response = client().get("/api/auth/me", headers=headers()) if operation == "get" else client().post("/api/auth/logout", headers=headers())
    assert response.status_code == 503
    assert "synthetic" not in response.text


@pytest.mark.parametrize("record", [None, {"activo":False,"id_rol":"ROL_ADMIN"}, {"activo":True,"id_rol":"ROL_CONS"}])
def test_user_removed_disabled_or_role_changed(monkeypatch, record):
    monkeypatch.setattr(sec, "query_one", lambda *args: record)
    assert client().get("/api/auth/me", headers=headers()).status_code == 401


def test_database_unavailable(monkeypatch):
    def fail(*args):
        raise OperationalError("synthetic connection details")
    monkeypatch.setattr(sec, "query_one", fail)
    r = client().get("/api/auth/me", headers=headers())
    assert r.status_code == 503 and "synthetic" not in r.text


def test_role_denied(monkeypatch):
    monkeypatch.setattr(sec, "query_one", lambda *args: {"activo":True,"id_rol":"ROL_CONS"})
    assert client().get("/api/users", headers=headers(token(role="ROL_CONS"))).status_code == 403


@pytest.mark.parametrize("active,password,expected", [(True,"Synthetic123!",200),(True,"Incorrect123!",401),(False,"Synthetic123!",401)], ids=["valid", "wrong-password", "inactive"])
def test_login(monkeypatch, active, password, expected):
    record = dict(USER, activo=active, password_hash=sec.hash_password("Synthetic123!", iterations=10000))
    monkeypatch.setattr(auth, "query_one", lambda *args: record)
    @contextmanager
    def transaction():
        yield SimpleNamespace(execute=lambda *args: None)
    monkeypatch.setattr(auth, "transaction", transaction)
    response = client().post("/api/auth/login", json={"correo":"test@example.com","password":password})
    assert response.status_code == expected
    assert "password_hash" not in response.text


def test_parameterized_login_injection(monkeypatch):
    captured = []
    monkeypatch.setattr(auth, "query_one", lambda sql, params: captured.append((sql,params)))
    payload = "' OR 1=1 --"
    assert client().post("/api/auth/login", json={"correo":payload,"password":"Synthetic123!"}).status_code == 401
    assert payload not in captured[0][0] and captured[0][1] == (payload,)


def test_invalid_payment_input():
    response = client(payments).post("/api/pagos", headers=headers(), json={"id_venta":"test","id_metodo_pago":"test","monto":-1})
    assert response.status_code == 422


def test_self_deactivation():
    assert client().delete("/api/users/TEST_USER", headers=headers()).status_code == 409

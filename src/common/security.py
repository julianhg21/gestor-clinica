import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt
import redis
from psycopg import Error as DatabaseError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from common.config import settings
from common.db import query_one

ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)
_redis = redis.Redis.from_url(
    settings.redis_url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2,
)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def hash_password(password: str, iterations: int = 390_000) -> str:
    salt = secrets.token_bytes(18)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, raw_iterations, raw_salt, raw_digest = encoded.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), _unb64(raw_salt), int(raw_iterations))
        return hmac.compare_digest(digest, _unb64(raw_digest))
    except (ValueError, TypeError):
        return False


def create_access_token(user: dict) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user["id_usuario"],
        "email": user["correo"],
        "name": user["nombre_completo"],
        "role": user["id_rol"],
        "jti": secrets.token_urlsafe(18),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_exp_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[ALGORITHM],
            options={"require": ["sub", "exp", "iat", "jti", "role"]},
        )
        if any(not isinstance(payload[key], str) or not payload[key] for key in ("sub", "jti", "role")):
            raise jwt.InvalidTokenError("Invalid identity claims")
        if any(isinstance(payload[key], bool) or not isinstance(payload[key], (int, float)) for key in ("exp", "iat")):
            raise jwt.InvalidTokenError("Invalid temporal claims")
        if payload["exp"] <= payload["iat"]:
            raise jwt.InvalidTokenError("Invalid lifetime")
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Sesión expirada") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Token inválido") from exc
    try:
        if _redis.get(f"revoked:{payload['jti']}"):
            raise HTTPException(status_code=401, detail="Sesión cerrada")
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Verificación de sesión no disponible") from exc
    return payload


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticación requerida")
    payload = decode_token(credentials.credentials)
    try:
        user = query_one(
            "SELECT activo,id_rol FROM duality.usuario WHERE id_usuario=%s", (payload["sub"],),
        )
    except DatabaseError as exc:
        raise HTTPException(status_code=503, detail="Verificación de identidad no disponible") from exc
    if not user or not user["activo"] or user["id_rol"] != payload["role"]:
        raise HTTPException(status_code=401, detail="Sesión no vigente")
    return payload


def require_roles(*roles: str) -> Callable:
    def dependency(user: dict = Depends(current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="No tiene permisos para esta operación")
        return user
    return dependency


def revoke_token(payload: dict) -> None:
    exp = payload.get("exp")
    if not exp or not payload.get("jti"):
        return
    ttl = max(1, int(exp - datetime.now(timezone.utc).timestamp()))
    try:
        _redis.setex(f"revoked:{payload['jti']}", ttl, "1")
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Cierre de sesión no disponible") from exc

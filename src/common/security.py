import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt
import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from common.config import settings

ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)
_redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)


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


def create_access_token(user: dict, *, mfa_verified: bool = False, mfa_method: str = "otp") -> str:
    if user["id_rol"] == "ROL_ADMIN" and not mfa_verified:
        raise ValueError("La cuenta administrativa requiere MFA")
    if mfa_verified and mfa_method not in {"otp", "recovery"}:
        raise ValueError("Método MFA inválido")
    now = datetime.now(timezone.utc)
    payload = {
        "typ": "access",
        "sub": user["id_usuario"],
        "email": user["correo"],
        "name": user["nombre_completo"],
        "role": user["id_rol"],
        "amr": ["pwd", mfa_method] if mfa_verified else ["pwd"],
        "jti": secrets.token_urlsafe(18),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_exp_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Sesión expirada") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Token inválido") from exc
    if payload.get("typ") != "access" or not payload.get("sub") or not payload.get("jti"):
        raise HTTPException(status_code=401, detail="Token inválido")
    if payload.get("role") == "ROL_ADMIN" and not {"otp", "recovery"}.intersection(payload.get("amr", [])):
        raise HTTPException(status_code=401, detail="Se requiere autenticación multifactor")
    try:
        if _redis.get(f"revoked:{payload['jti']}"):
            raise HTTPException(status_code=401, detail="Sesión cerrada")
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Validación de sesión no disponible") from exc
    return payload


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticación requerida")
    return decode_token(credentials.credentials)


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
        raise HTTPException(status_code=503, detail="No se pudo cerrar la sesión") from exc

"""TOTP and short-lived, password-only MFA challenges for administrator access."""

import base64
import hashlib
import hmac
import secrets
import struct
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import jwt
import redis
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import HTTPException

from common.config import settings


_redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)
_LOCK_SECONDS = 15 * 60
_MAX_FAILURES = 5
_STEP_SECONDS = 30


def _limit_key(kind: str, identifier: str) -> str:
    digest = hashlib.sha256(identifier.lower().encode()).hexdigest()
    return f"auth:{kind}:{digest}"


def check_attempts(kind: str, identifier: str) -> None:
    try:
        count = _redis.get(_limit_key(kind, identifier))
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Autenticación temporalmente no disponible") from exc
    if count is not None and int(count) >= _MAX_FAILURES:
        raise HTTPException(status_code=429, detail="Demasiados intentos; intente más tarde")


def failed_attempt(kind: str, identifier: str) -> None:
    key = _limit_key(kind, identifier)
    try:
        _redis.set(key, "0", nx=True, ex=_LOCK_SECONDS)
        _redis.incr(key)
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Autenticación temporalmente no disponible") from exc


def clear_attempts(kind: str, identifier: str) -> None:
    try:
        _redis.delete(_limit_key(kind, identifier))
    except redis.RedisError as exc:
        raise HTTPException(status_code=503, detail="Autenticación temporalmente no disponible") from exc


def create_challenge(user_id: str, purpose: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"typ": "mfa_challenge", "sub": user_id, "purpose": purpose, "iat": now,
         "exp": now + timedelta(minutes=10), "jti": secrets.token_urlsafe(18)},
        settings.jwt_secret, algorithm="HS256",
    )


def decode_challenge(token: str, purpose: str | None = None) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Desafío MFA inválido o expirado") from exc
    if payload.get("typ") != "mfa_challenge" or payload.get("purpose") not in {"mfa_setup", "mfa_verify"} or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Desafío MFA inválido o expirado")
    if purpose is not None and payload["purpose"] != purpose:
        raise HTTPException(status_code=401, detail="Desafío MFA inválido o expirado")
    return payload


def new_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def _encryption_key() -> bytes:
    return hmac.new(settings.jwt_secret.encode(), b"duality-mfa-storage-v1", hashlib.sha256).digest()


def encrypt_secret(secret: str, user_id: str) -> str:
    nonce = secrets.token_bytes(12)
    encrypted = AESGCM(_encryption_key()).encrypt(nonce, secret.encode(), user_id.encode())
    return base64.urlsafe_b64encode(nonce + encrypted).decode()


def decrypt_secret(ciphertext: str, user_id: str) -> str:
    try:
        data = base64.urlsafe_b64decode(ciphertext)
        return AESGCM(_encryption_key()).decrypt(data[:12], data[12:], user_id.encode()).decode()
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=503, detail="Factor MFA no disponible") from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Factor MFA no disponible") from exc


def provisioning_uri(secret: str, email: str) -> str:
    label = quote(f"Duality:{email}", safe="")
    return f"otpauth://totp/{label}?secret={secret}&issuer=Duality&algorithm=SHA1&digits=6&period=30"


def _code_for_step(secret: str, step: int) -> str:
    key = base64.b32decode(secret + "=" * (-len(secret) % 8))
    digest = hmac.new(key, struct.pack(">Q", step), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    number = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{number % 1_000_000:06d}"


def match_step(secret: str, code: str, last_step: int | None, now: float | None = None) -> int | None:
    if len(code) != 6 or not code.isascii() or not code.isdecimal():
        return None
    current = int((time.time() if now is None else now) // _STEP_SECONDS)
    for step in (current - 1, current, current + 1):
        if step >= 0 and (last_step is None or step > last_step):
            if hmac.compare_digest(_code_for_step(secret, step), code):
                return step
    return None

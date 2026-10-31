from datetime import datetime
from typing import Literal

from fastapi import Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from common.app import create_app
from common.db import query_all, query_one, transaction
from common.mfa import (
    check_attempts, clear_attempts, create_challenge, decode_challenge,
    decrypt_secret, encrypt_secret, failed_attempt, match_step, new_secret,
    provisioning_uri,
)
from common.security import (
    create_access_token, current_user, decode_token, hash_password,
    require_roles, revoke_token, verify_password, bearer,
)
from common.utils import new_id

app = create_app("Duality Auth Service")


class LoginRequest(BaseModel):
    # El usuario académico inicial usa @duality.local. EmailStr rechaza
    # dominios reservados como .local, por eso en login validamos longitud
    # y dejamos que la autenticación compruebe el correo contra PostgreSQL.
    correo: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=8, max_length=128)


class MfaChallengeRequest(BaseModel):
    challenge_token: str = Field(min_length=20, max_length=2000)


class MfaConfirmRequest(MfaChallengeRequest):
    code: str = Field(min_length=6, max_length=6)


class UserCreate(BaseModel):
    nombre_completo: str = Field(min_length=3, max_length=120)
    correo: EmailStr
    password: str = Field(min_length=12, max_length=128)
    id_rol: Literal["ROL_ADMIN", "ROL_OPER", "ROL_CONS"] = "ROL_OPER"
    telefono: str | None = Field(default=None, max_length=25)


class UserUpdate(BaseModel):
    nombre_completo: str | None = Field(default=None, min_length=3, max_length=120)
    telefono: str | None = Field(default=None, max_length=25)
    id_rol: Literal["ROL_ADMIN", "ROL_OPER", "ROL_CONS"] | None = None
    activo: bool | None = None
    password: str | None = Field(default=None, min_length=12, max_length=128)


@app.get("/api/auth/health")
def health():
    return {"service": "auth", "status": "ok", "time": datetime.utcnow()}


@app.post("/api/auth/login")
def login(body: LoginRequest):
    check_attempts("password", body.correo)
    user = query_one(
        """SELECT u.id_usuario,u.id_rol,u.nombre_completo,u.correo,u.password_hash,
                  u.activo,u.requiere_cambio_password,m.secret_ciphertext
             FROM duality.usuario u LEFT JOIN duality.usuario_mfa m USING(id_usuario)
             WHERE LOWER(u.correo)=LOWER(%s)""",
        (body.correo,),
    )
    if not user or not user["activo"] or not verify_password(body.password, user["password_hash"]):
        failed_attempt("password", body.correo)
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if user["requiere_cambio_password"]:
        raise HTTPException(status_code=403, detail="La cuenta requiere activar una contraseña propia")
    if user["id_rol"] == "ROL_ADMIN":
        purpose = "mfa_verify" if user["secret_ciphertext"] else "mfa_setup"
        return {
            "mfa_required": True,
            "setup_required": purpose == "mfa_setup",
            "challenge_token": create_challenge(user["id_usuario"], purpose),
        }
    clear_attempts("password", body.correo)
    with transaction() as conn:
        conn.execute("UPDATE duality.usuario SET ultimo_acceso=CURRENT_TIMESTAMP WHERE id_usuario=%s", (user["id_usuario"],))
    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {k: user[k] for k in ("id_usuario", "id_rol", "nombre_completo", "correo")},
    }


@app.post("/api/auth/mfa/setup")
def setup_mfa(body: MfaChallengeRequest):
    challenge = decode_challenge(body.challenge_token, "mfa_setup")
    check_attempts("mfa", challenge["sub"])
    with transaction() as conn:
        user = conn.execute(
            """SELECT id_usuario,correo,activo,id_rol,requiere_cambio_password
               FROM duality.usuario WHERE id_usuario=%s FOR UPDATE""",
            (challenge["sub"],),
        ).fetchone()
        if not user or not user["activo"] or user["id_rol"] != "ROL_ADMIN" or user["requiere_cambio_password"]:
            raise HTTPException(status_code=401, detail="Desafío MFA inválido")
        conn.execute(
            "INSERT INTO duality.usuario_mfa(id_usuario) VALUES(%s) ON CONFLICT DO NOTHING",
            (user["id_usuario"],),
        )
        factor = conn.execute(
            "SELECT secret_ciphertext,pending_ciphertext FROM duality.usuario_mfa WHERE id_usuario=%s FOR UPDATE",
            (user["id_usuario"],),
        ).fetchone()
        if factor["secret_ciphertext"]:
            raise HTTPException(status_code=409, detail="MFA ya está activado")
        secret = decrypt_secret(factor["pending_ciphertext"], user["id_usuario"]) if factor["pending_ciphertext"] else new_secret()
        if not factor["pending_ciphertext"]:
            conn.execute(
                "UPDATE duality.usuario_mfa SET pending_ciphertext=%s WHERE id_usuario=%s",
                (encrypt_secret(secret, user["id_usuario"]), user["id_usuario"]),
            )
    return {"secret": secret, "otpauth_uri": provisioning_uri(secret, user["correo"])}


@app.post("/api/auth/mfa/confirm")
def confirm_mfa(body: MfaConfirmRequest):
    challenge = decode_challenge(body.challenge_token)
    user_id = challenge["sub"]
    check_attempts("mfa", user_id)
    with transaction() as conn:
        user = conn.execute(
            """SELECT u.id_usuario,u.id_rol,u.nombre_completo,u.correo,u.activo,
                      u.requiere_cambio_password,m.secret_ciphertext,m.pending_ciphertext,
                      m.last_accepted_step
               FROM duality.usuario u LEFT JOIN duality.usuario_mfa m USING(id_usuario)
               WHERE u.id_usuario=%s FOR UPDATE OF u""",
            (user_id,),
        ).fetchone()
        if not user or not user["activo"] or user["id_rol"] != "ROL_ADMIN" or user["requiere_cambio_password"]:
            raise HTTPException(status_code=401, detail="Desafío MFA inválido")
        setup = challenge["purpose"] == "mfa_setup"
        ciphertext = user["pending_ciphertext"] if setup and not user["secret_ciphertext"] else user["secret_ciphertext"] if not setup else None
        if not ciphertext:
            raise HTTPException(status_code=401, detail="Desafío MFA inválido")
        secret = decrypt_secret(ciphertext, user_id)
        step = match_step(secret, body.code, None if setup else user["last_accepted_step"])
        if step is None:
            failed_attempt("mfa", user_id)
            raise HTTPException(status_code=401, detail="Código inválido")
        if setup:
            conn.execute(
                """UPDATE duality.usuario_mfa
                   SET secret_ciphertext=pending_ciphertext,pending_ciphertext=NULL,
                       last_accepted_step=%s,enabled_at=CURRENT_TIMESTAMP WHERE id_usuario=%s""",
                (step, user_id),
            )
        else:
            updated = conn.execute(
                """UPDATE duality.usuario_mfa SET last_accepted_step=%s
                   WHERE id_usuario=%s AND (last_accepted_step IS NULL OR last_accepted_step<%s)""",
                (step, user_id, step),
            )
            if updated.rowcount != 1:
                raise HTTPException(status_code=401, detail="Código ya utilizado")
        conn.execute("UPDATE duality.usuario SET ultimo_acceso=CURRENT_TIMESTAMP WHERE id_usuario=%s", (user_id,))
    clear_attempts("mfa", user_id)
    clear_attempts("password", user["correo"])
    return {
        "access_token": create_access_token(user, mfa_verified=True),
        "token_type": "bearer",
        "user": {k: user[k] for k in ("id_usuario", "id_rol", "nombre_completo", "correo")},
    }


@app.get("/api/auth/me")
def me(user: dict = Depends(current_user)):
    return user


@app.post("/api/auth/logout", status_code=204)
def logout(credentials=Depends(bearer)):
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    revoke_token(payload)
    return None


@app.get("/api/roles")
def roles(_: dict = Depends(current_user)):
    return query_all("SELECT id_rol,nombre,descripcion,activo FROM duality.rol ORDER BY nombre")


@app.get("/api/users")
def users(_: dict = Depends(require_roles("ROL_ADMIN"))):
    return query_all(
        """SELECT u.id_usuario,u.nombre_completo,u.correo,u.telefono,u.id_rol,r.nombre AS rol,u.activo,u.fecha_creacion,u.ultimo_acceso
             FROM duality.usuario u JOIN duality.rol r USING(id_rol) ORDER BY u.nombre_completo"""
    )


@app.post("/api/users", status_code=201)
def create_user(body: UserCreate, _: dict = Depends(require_roles("ROL_ADMIN"))):
    uid = new_id("USR")
    try:
        with transaction() as conn:
            row = conn.execute(
                """INSERT INTO duality.usuario(id_usuario,id_rol,nombre_completo,correo,telefono,password_hash)
                     VALUES(%s,%s,%s,LOWER(%s),%s,%s)
                     RETURNING id_usuario,id_rol,nombre_completo,correo,telefono,activo,fecha_creacion""",
                (uid, body.id_rol, body.nombre_completo, body.correo, body.telefono, hash_password(body.password)),
            ).fetchone()
        return row
    except Exception as exc:
        if "unique" in str(exc).lower():
            raise HTTPException(status_code=409, detail="El correo ya está registrado") from exc
        raise


@app.put("/api/users/{user_id}")
def update_user(user_id: str, body: UserUpdate, user: dict = Depends(require_roles("ROL_ADMIN"))):
    if user_id == user["sub"] and body.activo is False:
        raise HTTPException(status_code=409, detail="No puede desactivar su propio usuario")
    fields, values = [], []
    for name in ("nombre_completo", "telefono", "id_rol", "activo"):
        value = getattr(body, name)
        if value is not None:
            fields.append(f"{name}=%s")
            values.append(value)
    if body.password is not None:
        fields.append("password_hash=%s")
        values.append(hash_password(body.password))
    if not fields:
        raise HTTPException(status_code=400, detail="No hay cambios")
    values.append(user_id)
    with transaction() as conn:
        row = conn.execute(
            f"UPDATE duality.usuario SET {', '.join(fields)} WHERE id_usuario=%s RETURNING id_usuario,id_rol,nombre_completo,correo,telefono,activo",
            values,
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return row


@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: str, user: dict = Depends(require_roles("ROL_ADMIN"))):
    if user_id == user["sub"]:
        raise HTTPException(status_code=409, detail="No puede desactivar su propio usuario")
    with transaction() as conn:
        row = conn.execute(
            "UPDATE duality.usuario SET activo=FALSE WHERE id_usuario=%s AND activo=TRUE RETURNING id_usuario",
            (user_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o ya inactivo")
    return None

from datetime import datetime
from typing import Literal

from fastapi import Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from common.app import create_app
from common.db import query_all, query_one, transaction
from common.security import (
    create_access_token, current_user, decode_token, hash_password,
    require_roles, revoke_token, verify_password, bearer,
)
from common.utils import new_id

app = create_app("Duality Auth Service")


class LoginRequest(BaseModel):
    # El usuario administrador académico usa un dominio local; para login
    # validamos longitud y normalizamos en la consulta, sin exigir DNS/TLD público.
    correo: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=8, max_length=128)


class UserCreate(BaseModel):
    nombre_completo: str = Field(min_length=3, max_length=120)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=128)
    id_rol: Literal["ROL_ADMIN", "ROL_OPER", "ROL_CONS"] = "ROL_OPER"
    telefono: str | None = Field(default=None, max_length=25)


class UserUpdate(BaseModel):
    nombre_completo: str | None = Field(default=None, min_length=3, max_length=120)
    telefono: str | None = Field(default=None, max_length=25)
    id_rol: Literal["ROL_ADMIN", "ROL_OPER", "ROL_CONS"] | None = None
    activo: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


@app.get("/api/auth/health")
def health():
    return {"service": "auth", "status": "ok", "time": datetime.utcnow()}


@app.post("/api/auth/login")
def login(body: LoginRequest):
    user = query_one(
        """SELECT id_usuario,id_rol,nombre_completo,correo,password_hash,activo
             FROM duality.usuario WHERE LOWER(correo)=LOWER(%s)""",
        (body.correo,),
    )
    if not user or not user["activo"] or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    with transaction() as conn:
        conn.execute("UPDATE duality.usuario SET ultimo_acceso=CURRENT_TIMESTAMP WHERE id_usuario=%s", (user["id_usuario"],))
    token = create_access_token(user)
    return {
        "access_token": token,
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
def update_user(user_id: str, body: UserUpdate, _: dict = Depends(require_roles("ROL_ADMIN"))):
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

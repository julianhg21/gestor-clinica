from datetime import datetime
from decimal import Decimal

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field

from common.app import create_app
from common.db import query_all, transaction
from common.security import current_user, require_roles

app = create_app("Duality Payments Service")


class PaymentIn(BaseModel):
    id_venta: str
    id_metodo_pago: str
    monto: Decimal = Field(gt=0)
    referencia: str | None = Field(default=None, max_length=120)


class PaymentMethodIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=60)


@app.get("/api/payments/health")
def health():
    return {"service": "payments", "status": "ok", "time": datetime.utcnow()}


@app.get("/api/payment-methods")
def methods(_: dict = Depends(current_user)):
    return query_all("SELECT * FROM duality.metodo_pago WHERE activo=TRUE ORDER BY nombre")


@app.post("/api/payment-methods", status_code=201)
def add_method(body: PaymentMethodIn, _: dict = Depends(require_roles("ROL_ADMIN"))):
    key = "MP_" + ''.join(c for c in body.nombre.upper() if c.isalnum())[:16]
    with transaction() as conn:
        return conn.execute(
            "INSERT INTO duality.metodo_pago(id_metodo_pago,nombre) VALUES(%s,%s) RETURNING *",
            (key, body.nombre),
        ).fetchone()


@app.get("/api/payments")
def payments(order_id: str | None = None, limit: int = Query(100, ge=1, le=500), _: dict = Depends(current_user)):
    if order_id:
        return query_all("SELECT * FROM duality.vw_pagos_resumen WHERE id_venta=%s ORDER BY fecha_hora DESC", (order_id,))
    return query_all("SELECT * FROM duality.vw_pagos_resumen ORDER BY fecha_hora DESC LIMIT %s", (limit,))


@app.post("/api/payments", status_code=201)
def register_payment(body: PaymentIn, user: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    try:
        with transaction() as conn:
            conn.execute(
                "CALL duality.sp_registrar_pago(%s,%s,%s,%s,%s)",
                (body.id_venta, body.id_metodo_pago, user["sub"], body.monto, body.referencia),
            )
            return conn.execute("SELECT * FROM duality.vw_estado_cuenta_venta WHERE id_venta=%s", (body.id_venta,)).fetchone()
    except Exception as exc:
        raise HTTPException(409, detail=str(exc).splitlines()[0]) from exc

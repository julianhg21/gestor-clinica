from datetime import datetime
from decimal import Decimal

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field

from common.app import create_app
from common.db import query_all, transaction
from common.security import current_user, require_roles

app = create_app("Duality Pagos Service")


class PaymentIn(BaseModel):
    id_venta: str
    id_metodo_pago: str
    monto: Decimal = Field(gt=0)
    referencia: str | None = Field(default=None, max_length=120)


class PaymentUpdate(BaseModel):
    id_metodo_pago: str
    monto: Decimal = Field(gt=0)
    referencia: str | None = Field(default=None, max_length=120)


class PaymentMethodIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=60)


@app.get("/api/pagos/health")
def health():
    return {"service": "pagos", "status": "ok", "time": datetime.utcnow()}


@app.get("/api/metodos-pago")
def methods(_: dict = Depends(current_user)):
    return query_all("SELECT * FROM duality.metodo_pago WHERE activo=TRUE ORDER BY nombre")


@app.post("/api/metodos-pago", status_code=201)
def add_method(body: PaymentMethodIn, _: dict = Depends(require_roles("ROL_ADMIN"))):
    key = "MP_" + ''.join(c for c in body.nombre.upper() if c.isalnum())[:16]
    with transaction() as conn:
        return conn.execute(
            "INSERT INTO duality.metodo_pago(id_metodo_pago,nombre) VALUES(%s,%s) RETURNING *",
            (key, body.nombre),
        ).fetchone()


@app.get("/api/pagos")
def payments(order_id: str | None = None, limit: int = Query(100, ge=1, le=500), _: dict = Depends(current_user)):
    if order_id:
        return query_all("SELECT * FROM duality.vw_pagos_resumen WHERE id_venta=%s ORDER BY fecha_hora DESC", (order_id,))
    return query_all("SELECT * FROM duality.vw_pagos_resumen ORDER BY fecha_hora DESC LIMIT %s", (limit,))


@app.post("/api/pagos", status_code=201)
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


@app.put("/api/pagos/{payment_id}")
def update_payment(payment_id: str, body: PaymentUpdate, _: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    with transaction() as conn:
        payment = conn.execute(
            """SELECT p.id_pago,p.id_venta,p.estado,v.estado AS venta_estado,v.total
                 FROM duality.pago p JOIN duality.venta v USING(id_venta)
                WHERE p.id_pago=%s FOR UPDATE""",
            (payment_id,),
        ).fetchone()
        if not payment:
            raise HTTPException(404, "Pago no encontrado")
        if payment["estado"] != "REGISTRADO" or payment["venta_estado"] != "PENDIENTE":
            raise HTTPException(409, "Solo pueden editarse pagos registrados de ventas pendientes")

        paid_others = conn.execute(
            """SELECT COALESCE(SUM(monto),0) AS total
                 FROM duality.pago
                WHERE id_venta=%s AND id_pago<>%s AND estado='REGISTRADO'""",
            (payment["id_venta"], payment_id),
        ).fetchone()["total"]
        if paid_others + body.monto > payment["total"]:
            raise HTTPException(409, "El pago excede el saldo pendiente")

        return conn.execute(
            """UPDATE duality.pago
                  SET id_metodo_pago=%s,monto=%s,referencia=%s
                WHERE id_pago=%s
                RETURNING *""",
            (body.id_metodo_pago, body.monto, body.referencia, payment_id),
        ).fetchone()


@app.delete("/api/pagos/{payment_id}", status_code=204)
def cancel_payment(payment_id: str, _: dict = Depends(require_roles("ROL_ADMIN"))):
    with transaction() as conn:
        row = conn.execute(
            """UPDATE duality.pago p
                  SET estado='ANULADO'
                 FROM duality.venta v
                WHERE p.id_pago=%s
                  AND p.id_venta=v.id_venta
                  AND p.estado='REGISTRADO'
                  AND v.estado='PENDIENTE'
                RETURNING p.id_pago""",
            (payment_id,),
        ).fetchone()
    if not row:
        raise HTTPException(409, "Solo pueden anularse pagos de ventas pendientes")
    return None

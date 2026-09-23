from datetime import datetime
from decimal import Decimal

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field

from common.app import create_app
from common.db import query_all, query_one, transaction
from common.security import current_user, require_roles
from common.utils import new_id

app = create_app("Duality Orders Service")


class OrderItem(BaseModel):
    id_producto: str
    cantidad: Decimal = Field(gt=0)
    precio_unitario: Decimal | None = Field(default=None, ge=0)


class OrderCreate(BaseModel):
    id_paciente: str | None = None
    id_metodo_pago: str = "MP_EFECTIVO"
    descuento: Decimal = Field(default=0, ge=0)
    observaciones: str | None = Field(default=None, max_length=300)
    items: list[OrderItem] = Field(min_length=1)


class OrderUpdate(BaseModel):
    descuento: Decimal = Field(default=0, ge=0)
    id_metodo_pago: str
    observaciones: str | None = Field(default=None, max_length=300)


@app.get("/api/orders/health")
def health():
    return {"service": "orders", "status": "ok", "time": datetime.utcnow()}


@app.get("/api/orders")
def list_orders(status: str | None = None, limit: int = Query(100, ge=1, le=500), _: dict = Depends(current_user)):
    if status:
        return query_all("SELECT * FROM duality.vw_ventas_resumen WHERE estado=%s ORDER BY fecha_hora DESC LIMIT %s", (status, limit))
    return query_all("SELECT * FROM duality.vw_ventas_resumen ORDER BY fecha_hora DESC LIMIT %s", (limit,))


@app.get("/api/orders/{order_id}")
def get_order(order_id: str, _: dict = Depends(current_user)):
    order = query_one("SELECT * FROM duality.vw_ventas_resumen WHERE id_venta=%s", (order_id,))
    if not order:
        raise HTTPException(404, "Venta no encontrada")
    items = query_all(
        """SELECT d.*,p.nombre,p.sku FROM duality.detalle_venta d
             JOIN duality.producto p USING(id_producto) WHERE id_venta=%s ORDER BY p.nombre""",
        (order_id,),
    )
    account = query_one("SELECT * FROM duality.vw_estado_cuenta_venta WHERE id_venta=%s", (order_id,))
    return {"order": order, "items": items, "account": account}


@app.post("/api/orders", status_code=201)
def create_order(body: OrderCreate, user: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    order_id = new_id("VTA")
    try:
        with transaction() as conn:
            conn.execute(
                """INSERT INTO duality.venta(id_venta,id_paciente,id_usuario,id_metodo_pago,descuento,observaciones)
                     VALUES(%s,%s,%s,%s,%s,%s)""",
                (order_id, body.id_paciente, user["sub"], body.id_metodo_pago, 0, body.observaciones),
            )
            for item in body.items:
                price = item.precio_unitario
                if price is None:
                    product = conn.execute("SELECT precio_venta FROM duality.producto WHERE id_producto=%s AND activo=TRUE", (item.id_producto,)).fetchone()
                    if not product:
                        raise ValueError(f"Producto {item.id_producto} inexistente o inactivo")
                    price = product["precio_venta"]
                conn.execute(
                    """INSERT INTO duality.detalle_venta(id_detalle_venta,id_venta,id_producto,cantidad,precio_unitario)
                         VALUES(%s,%s,%s,%s,%s)""",
                    (new_id("DTV"), order_id, item.id_producto, item.cantidad, price),
                )
            conn.execute("UPDATE duality.venta SET descuento=%s,total=GREATEST(subtotal-%s,0) WHERE id_venta=%s", (body.descuento, body.descuento, order_id))
            row = conn.execute("SELECT * FROM duality.venta WHERE id_venta=%s", (order_id,)).fetchone()
        return row
    except Exception as exc:
        raise HTTPException(409, detail=str(exc).splitlines()[0]) from exc


@app.put("/api/orders/{order_id}")
def update_order(order_id: str, body: OrderUpdate, _: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    with transaction() as conn:
        row = conn.execute(
            """UPDATE duality.venta SET descuento=%s,id_metodo_pago=%s,observaciones=%s,
                 total=GREATEST(subtotal-%s,0) WHERE id_venta=%s AND estado='PENDIENTE' RETURNING *""",
            (body.descuento, body.id_metodo_pago, body.observaciones, body.descuento, order_id),
        ).fetchone()
    if not row:
        raise HTTPException(409, "Venta no encontrada o ya no es editable")
    return row


@app.post("/api/orders/{order_id}/confirm")
def confirm_order(order_id: str, user: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    try:
        with transaction() as conn:
            conn.execute("CALL duality.sp_confirmar_venta(%s,%s)", (order_id, user["sub"]))
            return conn.execute("SELECT * FROM duality.vw_ventas_resumen WHERE id_venta=%s", (order_id,)).fetchone()
    except Exception as exc:
        raise HTTPException(409, detail=str(exc).splitlines()[0]) from exc


@app.post("/api/orders/{order_id}/cancel")
def cancel_order(order_id: str, _: dict = Depends(require_roles("ROL_ADMIN"))):
    with transaction() as conn:
        row = conn.execute("UPDATE duality.venta SET estado='ANULADA' WHERE id_venta=%s AND estado='PENDIENTE' RETURNING *", (order_id,)).fetchone()
    if not row:
        raise HTTPException(409, "Solo pueden anularse ventas pendientes")
    return row


@app.get("/api/orders/reports/daily")
def daily_report(days: int = Query(30, ge=1, le=365), _: dict = Depends(current_user)):
    return query_all(
        """SELECT DATE(fecha_hora) AS fecha,COUNT(*) AS ventas,SUM(total) AS ingresos
             FROM duality.venta WHERE estado='CONFIRMADA' AND fecha_hora >= CURRENT_DATE-(%s * INTERVAL '1 day')
             GROUP BY DATE(fecha_hora) ORDER BY fecha""",
        (days,),
    )

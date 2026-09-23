from datetime import date, datetime
from decimal import Decimal

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

from common.app import create_app
from common.db import query_all, query_one, transaction
from common.security import current_user, require_roles
from common.utils import new_id

app = create_app("Duality Catálogo Service")


class PatientIn(BaseModel):
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    fecha_nacimiento: date | None = None
    telefono: str | None = Field(default=None, max_length=25)
    correo: EmailStr | None = None
    observaciones: str | None = None


class ProductIn(BaseModel):
    sku: str | None = Field(default=None, max_length=50)
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: str | None = Field(default=None, max_length=300)
    costo_unitario: Decimal | None = Field(default=None, ge=0)
    precio_venta: Decimal = Field(ge=0)
    stock_minimo: Decimal | None = Field(default=0, ge=0)


class ServiceIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: str | None = Field(default=None, max_length=300)
    precio_base: Decimal = Field(ge=0)
    duracion_min: int | None = Field(default=None, gt=0)


class InventoryMovementIn(BaseModel):
    id_producto: str
    tipo_movimiento: str
    cantidad: Decimal = Field(gt=0)
    origen_tipo: str = "AJUSTE"
    origen_id: str | None = None
    motivo: str | None = Field(default=None, max_length=250)


class ClinicalServiceIn(BaseModel):
    id_paciente: str
    id_servicio: str
    precio_aplicado: Decimal | None = Field(default=None, ge=0)
    id_venta: str | None = None
    observaciones: str | None = None


class ConsumptionIn(BaseModel):
    id_producto: str
    cantidad: Decimal = Field(gt=0)
    observaciones: str | None = Field(default=None, max_length=200)


@app.get("/api/catalogo/health")
def health():
    return {"service": "catalogo", "status": "ok", "time": datetime.utcnow()}


@app.get("/api/catalogo/dashboard")
def dashboard(_: dict = Depends(current_user)):
    return query_one("SELECT * FROM duality.vw_dashboard") or {}


@app.get("/api/catalogo/patients")
def list_patients(search: str = "", _: dict = Depends(current_user)):
    term = f"%{search.strip()}%"
    return query_all(
        """SELECT * FROM duality.paciente WHERE activo=TRUE
             AND (%s='' OR nombres ILIKE %s OR apellidos ILIKE %s OR COALESCE(correo,'') ILIKE %s)
             ORDER BY apellidos,nombres""",
        (search.strip(), term, term, term),
    )


@app.get("/api/catalogo/patients/{patient_id}")
def get_patient(patient_id: str, _: dict = Depends(current_user)):
    row = query_one("SELECT * FROM duality.paciente WHERE id_paciente=%s", (patient_id,))
    if not row:
        raise HTTPException(404, "Paciente no encontrado")
    history = query_all("SELECT * FROM duality.vw_historial_paciente WHERE id_paciente=%s ORDER BY fecha_hora DESC", (patient_id,))
    return {"patient": row, "history": history}


@app.post("/api/catalogo/patients", status_code=201)
def create_patient(body: PatientIn, _: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    pid = new_id("PAC")
    with transaction() as conn:
        return conn.execute(
            """INSERT INTO duality.paciente(id_paciente,nombres,apellidos,fecha_nacimiento,telefono,correo,observaciones)
                 VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
            (pid, body.nombres, body.apellidos, body.fecha_nacimiento, body.telefono, body.correo, body.observaciones),
        ).fetchone()


@app.put("/api/catalogo/patients/{patient_id}")
def update_patient(patient_id: str, body: PatientIn, _: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    with transaction() as conn:
        row = conn.execute(
            """UPDATE duality.paciente SET nombres=%s,apellidos=%s,fecha_nacimiento=%s,telefono=%s,correo=%s,observaciones=%s
                 WHERE id_paciente=%s RETURNING *""",
            (body.nombres, body.apellidos, body.fecha_nacimiento, body.telefono, body.correo, body.observaciones, patient_id),
        ).fetchone()
    if not row:
        raise HTTPException(404, "Paciente no encontrado")
    return row


@app.delete("/api/catalogo/patients/{patient_id}", status_code=204)
def delete_patient(patient_id: str, _: dict = Depends(require_roles("ROL_ADMIN"))):
    with transaction() as conn:
        if conn.execute("UPDATE duality.paciente SET activo=FALSE WHERE id_paciente=%s", (patient_id,)).rowcount == 0:
            raise HTTPException(404, "Paciente no encontrado")


@app.get("/api/catalogo/products")
def list_products(include_inactive: bool = False, _: dict = Depends(current_user)):
    sql = "SELECT p.*,s.stock_actual,s.bajo_minimo FROM duality.producto p LEFT JOIN duality.vw_stock_actual s USING(id_producto)"
    if not include_inactive:
        sql += " WHERE p.activo=TRUE"
    return query_all(sql + " ORDER BY p.nombre")


@app.post("/api/catalogo/products", status_code=201)
def create_product(body: ProductIn, _: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    with transaction() as conn:
        return conn.execute(
            """INSERT INTO duality.producto(id_producto,sku,nombre,descripcion,costo_unitario,precio_venta,stock_minimo)
                 VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
            (new_id("PRO"), body.sku, body.nombre, body.descripcion, body.costo_unitario, body.precio_venta, body.stock_minimo),
        ).fetchone()


@app.put("/api/catalogo/products/{product_id}")
def update_product(product_id: str, body: ProductIn, _: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    with transaction() as conn:
        row = conn.execute(
            """UPDATE duality.producto SET sku=%s,nombre=%s,descripcion=%s,costo_unitario=%s,precio_venta=%s,stock_minimo=%s
                 WHERE id_producto=%s RETURNING *""",
            (body.sku, body.nombre, body.descripcion, body.costo_unitario, body.precio_venta, body.stock_minimo, product_id),
        ).fetchone()
    if not row:
        raise HTTPException(404, "Producto no encontrado")
    return row


@app.delete("/api/catalogo/products/{product_id}", status_code=204)
def delete_product(product_id: str, _: dict = Depends(require_roles("ROL_ADMIN"))):
    with transaction() as conn:
        if conn.execute("UPDATE duality.producto SET activo=FALSE WHERE id_producto=%s", (product_id,)).rowcount == 0:
            raise HTTPException(404, "Producto no encontrado")


@app.get("/api/catalogo/services")
def list_services(_: dict = Depends(current_user)):
    return query_all("SELECT * FROM duality.servicio WHERE activo=TRUE ORDER BY nombre")


@app.post("/api/catalogo/services", status_code=201)
def create_service(body: ServiceIn, _: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    with transaction() as conn:
        return conn.execute(
            """INSERT INTO duality.servicio(id_servicio,nombre,descripcion,precio_base,duracion_min)
                 VALUES(%s,%s,%s,%s,%s) RETURNING *""",
            (new_id("SER"), body.nombre, body.descripcion, body.precio_base, body.duracion_min),
        ).fetchone()


@app.put("/api/catalogo/services/{service_id}")
def update_service(service_id: str, body: ServiceIn, _: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    with transaction() as conn:
        row = conn.execute(
            "UPDATE duality.servicio SET nombre=%s,descripcion=%s,precio_base=%s,duracion_min=%s WHERE id_servicio=%s RETURNING *",
            (body.nombre, body.descripcion, body.precio_base, body.duracion_min, service_id),
        ).fetchone()
    if not row:
        raise HTTPException(404, "Servicio no encontrado")
    return row


@app.delete("/api/catalogo/services/{service_id}", status_code=204)
def delete_service(service_id: str, _: dict = Depends(require_roles("ROL_ADMIN"))):
    with transaction() as conn:
        if conn.execute("UPDATE duality.servicio SET activo=FALSE WHERE id_servicio=%s", (service_id,)).rowcount == 0:
            raise HTTPException(404, "Servicio no encontrado")


@app.get("/api/catalogo/inventory")
def stock(_: dict = Depends(current_user)):
    return query_all("SELECT * FROM duality.vw_stock_actual ORDER BY nombre")


@app.get("/api/catalogo/inventory/movements")
def movements(limit: int = Query(100, ge=1, le=500), _: dict = Depends(current_user)):
    return query_all("SELECT * FROM duality.vw_movimientos_inventario_auditoria ORDER BY fecha_hora DESC LIMIT %s", (limit,))


@app.post("/api/catalogo/inventory/movements", status_code=201)
def add_movement(body: InventoryMovementIn, user: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    try:
        with transaction() as conn:
            conn.execute(
                "CALL duality.sp_registrar_movimiento_inventario(%s,%s,%s,%s,%s,%s,%s)",
                (body.id_producto, user["sub"], body.tipo_movimiento, body.cantidad, body.origen_tipo, body.origen_id, body.motivo),
            )
            row = conn.execute("SELECT * FROM duality.vw_stock_actual WHERE id_producto=%s", (body.id_producto,)).fetchone()
        return row
    except Exception as exc:
        raise HTTPException(409, detail=str(exc).splitlines()[0]) from exc


@app.get("/api/catalogo/clinical-services")
def clinical_services(_: dict = Depends(current_user)):
    return query_all(
        """SELECT sr.*,p.nombres||' '||p.apellidos AS paciente,s.nombre AS servicio,u.nombre_completo AS responsable
             FROM duality.servicio_realizado sr JOIN duality.paciente p USING(id_paciente)
             JOIN duality.servicio s USING(id_servicio) JOIN duality.usuario u USING(id_usuario)
             ORDER BY sr.fecha_hora DESC"""
    )


@app.post("/api/catalogo/clinical-services", status_code=201)
def create_clinical_service(body: ClinicalServiceIn, user: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    with transaction() as conn:
        return conn.execute(
            """INSERT INTO duality.servicio_realizado(id_servicio_realizado,id_paciente,id_servicio,id_usuario,id_venta,precio_aplicado,observaciones)
                 VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
            (new_id("SRV"), body.id_paciente, body.id_servicio, user["sub"], body.id_venta, body.precio_aplicado, body.observaciones),
        ).fetchone()


@app.post("/api/catalogo/clinical-services/{record_id}/consumptions", status_code=201)
def add_consumption(record_id: str, body: ConsumptionIn, _: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    with transaction() as conn:
        return conn.execute(
            """INSERT INTO duality.consumo_servicio(id_consumo,id_servicio_realizado,id_producto,cantidad,observaciones)
                 VALUES(%s,%s,%s,%s,%s) RETURNING *""",
            (new_id("CON"), record_id, body.id_producto, body.cantidad, body.observaciones),
        ).fetchone()


@app.post("/api/catalogo/clinical-services/{record_id}/finalize")
def finalize_clinical_service(record_id: str, user: dict = Depends(require_roles("ROL_ADMIN", "ROL_OPER"))):
    try:
        with transaction() as conn:
            conn.execute("CALL duality.sp_finalizar_servicio(%s,%s)", (record_id, user["sub"]))
            return conn.execute("SELECT * FROM duality.servicio_realizado WHERE id_servicio_realizado=%s", (record_id,)).fetchone()
    except Exception as exc:
        raise HTTPException(409, detail=str(exc).splitlines()[0]) from exc

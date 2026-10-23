"""Solo contenedor desechable sin red, etiqueta y nombre verificados; nunca DATABASE_URL."""
import json
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTAINER = os.getenv("AUDIT_DB_CONTAINER", "")
pytestmark = [pytest.mark.security, pytest.mark.skipif(not CONTAINER, reason="Requiere AUDIT_DB_CONTAINER desechable validado")]


def docker(*args, data=None, check=True):
    return subprocess.run(["docker", *args], input=data, text=True, encoding="utf-8", capture_output=True, check=check)


def sql(text, database="postgres", check=True):
    return docker("exec", "-i", CONTAINER, "psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", database, data=text, check=check)


@pytest.fixture(scope="module", autouse=True)
def disposable_database():
    if not CONTAINER:
        return
    assert CONTAINER == "duality-audit-postgres-20261023", "Contenedor no autorizado"
    info = json.loads(docker("inspect", CONTAINER).stdout)[0]
    assert info["Config"]["Labels"].get("duality.audit") == "20261023"
    assert info["HostConfig"]["NetworkMode"] == "none"
    assert not any(m["Type"] == "bind" for m in info["Mounts"])
    sql("DROP DATABASE IF EXISTS audit_restore;")
    for file in sorted((ROOT / "docker/postgres/init").glob("*.sql")):
        sql(file.read_text(encoding="utf-8"))
    sql("""
    INSERT INTO duality.producto(id_producto,nombre,precio_venta) VALUES ('AUDIT_PROD','Producto sintético',10);
    CALL duality.sp_registrar_movimiento_inventario('AUDIT_PROD','USR_ADMIN','ENTRADA',10,'AJUSTE',NULL,'Ensayo');
    """)


def test_database_constraints_and_immutable_inventory():
    result = sql("INSERT INTO duality.producto(id_producto,nombre,precio_venta) VALUES ('BAD','Inválido',-1);", check=False)
    assert result.returncode != 0 and "ck_producto_precio" in result.stderr
    result = sql("UPDATE duality.movimiento_inventario SET cantidad=99 WHERE id_producto='AUDIT_PROD';", check=False)
    assert result.returncode != 0
    assert sql("SELECT duality.fn_stock_producto('AUDIT_PROD');").stdout.strip() == "10.00"


def test_concurrent_inventory_no_negative_stock():
    command = "CALL duality.sp_registrar_movimiento_inventario('AUDIT_PROD','USR_ADMIN','SALIDA',7,'AJUSTE',NULL,'Concurrencia');"
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: sql(command, check=False), range(2)))
    assert sorted(r.returncode == 0 for r in results) == [False, True]
    assert sql("SELECT duality.fn_stock_producto('AUDIT_PROD');").stdout.strip() == "3.00"


def test_concurrent_payments_and_rollback():
    sql("""
    INSERT INTO duality.venta(id_venta,id_usuario,id_metodo_pago) VALUES ('AUDIT_SALE','USR_ADMIN','MP_EFECTIVO');
    INSERT INTO duality.detalle_venta(id_detalle_venta,id_venta,id_producto,cantidad,precio_unitario)
      VALUES ('AUDIT_DETAIL','AUDIT_SALE','AUDIT_PROD',1,10);
    """)
    command = "CALL duality.sp_registrar_pago('AUDIT_SALE','MP_EFECTIVO','USR_ADMIN',7,'Ensayo');"
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: sql(command, check=False), range(2)))
    assert sorted(r.returncode == 0 for r in results) == [False, True]
    assert sql("SELECT pagado FROM duality.vw_estado_cuenta_venta WHERE id_venta='AUDIT_SALE';").stdout.strip() == "7.00"
    sql("CALL duality.sp_registrar_pago('AUDIT_SALE','MP_EFECTIVO','USR_ADMIN',3,'Ensayo');")
    assert sql("SELECT estado FROM duality.venta WHERE id_venta='AUDIT_SALE';").stdout.strip() == "CONFIRMADA"
    assert sql("SELECT COUNT(*) FROM duality.movimiento_inventario WHERE origen_id='AUDIT_SALE';").stdout.strip() == "1"


def test_payment_failed_confirmation_rolls_back():
    sql("""
    INSERT INTO duality.venta(id_venta,id_usuario,id_metodo_pago) VALUES ('AUDIT_FAIL','USR_ADMIN','MP_EFECTIVO');
    INSERT INTO duality.detalle_venta(id_detalle_venta,id_venta,id_producto,cantidad,precio_unitario)
      VALUES ('AUDIT_FAIL_DETAIL','AUDIT_FAIL','AUDIT_PROD',100,10);
    """)
    result = sql("CALL duality.sp_registrar_pago('AUDIT_FAIL','MP_EFECTIVO','USR_ADMIN',1000,'Ensayo');", check=False)
    assert result.returncode != 0
    assert sql("SELECT COUNT(*) FROM duality.pago WHERE id_venta='AUDIT_FAIL';").stdout.strip() == "0"
    assert sql("SELECT estado FROM duality.venta WHERE id_venta='AUDIT_FAIL';").stdout.strip() == "PENDIENTE"


def test_backup_restore_in_separate_database():
    backup = docker("exec", CONTAINER, "pg_dump", "-U", "postgres", "-n", "duality", "--no-owner", "postgres").stdout
    # No se exporta el dump: incluye credencial académica precargada por el esquema.
    sql("CREATE DATABASE audit_restore;")
    sql(backup, database="audit_restore")
    for query in ["SELECT COUNT(*) FROM duality.producto;", "SELECT COUNT(*) FROM duality.movimiento_inventario;", "SELECT COUNT(*) FROM duality.pago;", "SELECT SUM(monto) FROM duality.pago;", "SELECT duality.fn_stock_producto('AUDIT_PROD');"]:
        assert sql(query).stdout == sql(query, database="audit_restore").stdout
    result = sql("UPDATE duality.movimiento_inventario SET cantidad=99 WHERE id_producto='AUDIT_PROD';", database="audit_restore", check=False)
    assert result.returncode != 0

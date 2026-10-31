import pytest
from fastapi.testclient import TestClient

from api.core import app as core_app
from api.sales import app as sales_app
from common import security
from catalogo import main as catalogo


def _cons_headers(monkeypatch):
    monkeypatch.setattr(security._redis, "get", lambda *_args, **_kwargs: None)
    token = security.create_access_token({
        "id_usuario": "USR_CONS", "id_rol": "ROL_CONS",
        "correo": "cons@example.invalid", "nombre_completo": "Consulta ficticia",
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    ("app", "path"),
    [
        (core_app, "/api/catalogo/dashboard"),
        (core_app, "/api/catalogo/patients"),
        (core_app, "/api/catalogo/patients/PAC_DEMO001"),
        (core_app, "/api/catalogo/inventory"),
        (core_app, "/api/catalogo/inventory/movements"),
        (core_app, "/api/catalogo/clinical-services"),
        (core_app, "/api/roles"),
        (sales_app, "/api/pedidos"),
        (sales_app, "/api/pedidos/VTA_DEMO001"),
        (sales_app, "/api/pedidos/reportes/diario"),
        (sales_app, "/api/pagos"),
        (sales_app, "/api/pagos?order_id=VTA_DEMO001"),
        (sales_app, "/api/metodos-pago"),
    ],
)
def test_cons_cannot_read_restricted_resources(app, path, monkeypatch):
    assert TestClient(app).get(path, headers=_cons_headers(monkeypatch)).status_code == 403


def test_cons_catalog_excludes_cost_inventory_and_inactive(monkeypatch):
    statements = []

    def fake_query(sql, *args):
        statements.append(sql)
        return [{"id_producto": "PRD_DEMO001", "nombre": "Producto de prueba", "precio_venta": 10}]

    monkeypatch.setattr(catalogo, "query_all", fake_query)
    response = TestClient(core_app).get("/api/catalogo/products?include_inactive=true", headers=_cons_headers(monkeypatch))
    assert response.status_code == 200
    assert response.json()[0]["id_producto"] == "PRD_DEMO001"
    assert "costo_unitario" not in statements[0]
    assert "stock_actual" not in statements[0]
    assert "activo=TRUE" in statements[0]

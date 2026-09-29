from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CATALOGO = (ROOT / "src/catalogo/main.py").read_text(encoding="utf-8")
PEDIDOS = (ROOT / "src/pedidos/main.py").read_text(encoding="utf-8")
PAGOS = (ROOT / "src/pagos/main.py").read_text(encoding="utf-8")
AUTH = (ROOT / "src/auth/main.py").read_text(encoding="utf-8")
WEB = (ROOT / "src/web/app.js").read_text(encoding="utf-8")
CSS = (ROOT / "src/web/styles.css").read_text(encoding="utf-8")
JENKINS = (ROOT / "Jenkinsfile").read_text(encoding="utf-8") if (ROOT / "Jenkinsfile").exists() else ""


@pytest.mark.unit
def test_patient_update_route_exists():
    assert '@app.put("/api/catalogo/patients/{patient_id}")' in CATALOGO


@pytest.mark.unit
def test_patient_soft_delete_route_exists():
    assert '@app.delete("/api/catalogo/patients/{patient_id}"' in CATALOGO
    assert "SET activo=FALSE" in CATALOGO


@pytest.mark.unit
def test_product_update_and_delete_routes_exist():
    assert '@app.put("/api/catalogo/products/{product_id}")' in CATALOGO
    assert '@app.delete("/api/catalogo/products/{product_id}"' in CATALOGO


@pytest.mark.unit
def test_service_update_and_delete_routes_exist():
    assert '@app.put("/api/catalogo/services/{service_id}")' in CATALOGO
    assert '@app.delete("/api/catalogo/services/{service_id}"' in CATALOGO


@pytest.mark.unit
def test_clinical_record_can_be_edited_before_close():
    assert '@app.put("/api/catalogo/clinical-services/{record_id}")' in CATALOGO
    assert "NOT IN ('FINALIZADO','ANULADO')" in CATALOGO


@pytest.mark.unit
def test_clinical_record_uses_auditable_cancel():
    assert '@app.delete("/api/catalogo/clinical-services/{record_id}"' in CATALOGO
    assert "SET estado='ANULADO'" in CATALOGO


@pytest.mark.unit
def test_pending_order_has_update_route():
    assert '@app.put("/api/pedidos/{order_id}")' in PEDIDOS
    assert "estado='PENDIENTE'" in PEDIDOS


@pytest.mark.unit
def test_order_delete_is_logical_cancel():
    assert '@app.delete("/api/pedidos/{order_id}"' in PEDIDOS
    assert "SET estado='ANULADA'" in PEDIDOS


@pytest.mark.unit
def test_order_cancel_annuls_registered_payments():
    assert "UPDATE duality.pago SET estado='ANULADO'" in PEDIDOS


@pytest.mark.unit
def test_payment_update_route_exists():
    assert '@app.put("/api/pagos/{payment_id}")' in PAGOS


@pytest.mark.unit
def test_payment_delete_is_logical_cancel():
    assert '@app.delete("/api/pagos/{payment_id}"' in PAGOS
    assert "SET estado='ANULADO'" in PAGOS


@pytest.mark.security
def test_payment_edit_requires_pending_sale():
    assert 'payment["venta_estado"] != "PENDIENTE"' in PAGOS


@pytest.mark.security
def test_admin_cannot_deactivate_self():
    assert "No puede desactivar su propio usuario" in AUTH
    assert '@app.delete("/api/users/{user_id}"' in AUTH


@pytest.mark.unit
def test_frontend_exposes_edit_and_delete_actions():
    for token in ["editPatient", "deleteProduct", "editService", "deleteOrder", "editPayment", "deleteUser"]:
        assert token in WEB


@pytest.mark.unit
def test_frontend_explains_inventory_auditability():
    assert "ajustes compensatorios" in WEB


@pytest.mark.unit
def test_new_visual_system_is_present():
    for token in ["login-shell", "user-pill", "table-btn", "toast-host", "linear-gradient"]:
        assert token in CSS or token in WEB


@pytest.mark.unit
def test_jenkinsfile_has_required_pipeline_stages():
    for stage in ["Checkout", "Build", "Test", "Deploy staging"]:
        assert f"stage('{stage}')" in JENKINS

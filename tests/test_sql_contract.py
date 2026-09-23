from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL = (ROOT / "docker/postgres/init/001_schema.sql").read_text(encoding="utf-8") + (ROOT / "docker/postgres/init/002_app_extensions.sql").read_text(encoding="utf-8")


def test_required_database_objects_exist():
    required = [
        "CREATE TABLE movimiento_inventario",
        "FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)",
        "CREATE OR REPLACE PROCEDURE sp_confirmar_venta",
        "CREATE OR REPLACE PROCEDURE sp_registrar_pago",
        "CREATE OR REPLACE VIEW vw_stock_actual",
        "CREATE OR REPLACE VIEW vw_dashboard",
        "FOR UPDATE",
    ]
    for token in required:
        assert token in SQL

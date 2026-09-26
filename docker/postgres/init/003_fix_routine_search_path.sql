-- ============================================================================
-- DUALITY - REPARACION DE SEARCH_PATH PARA RUTINAS EXISTENTES
-- Puede ejecutarse sobre una base ya creada sin borrar datos.
-- ============================================================================

BEGIN;

ALTER FUNCTION duality.fn_generar_id20()
SET search_path TO duality, public;

ALTER FUNCTION duality.fn_stock_producto(VARCHAR)
SET search_path TO duality, public;

ALTER FUNCTION duality.fn_total_venta(VARCHAR)
SET search_path TO duality, public;

ALTER FUNCTION duality.tg_detalle_venta_calcular_subtotal()
SET search_path TO duality, public;

ALTER FUNCTION duality.tg_recalcular_totales_venta()
SET search_path TO duality, public;

ALTER FUNCTION duality.tg_movimiento_validar_stock()
SET search_path TO duality, public;

ALTER FUNCTION duality.tg_movimiento_inmutable()
SET search_path TO duality, public;

ALTER PROCEDURE duality.sp_registrar_movimiento_inventario(
    VARCHAR, VARCHAR, VARCHAR, NUMERIC, VARCHAR, VARCHAR, VARCHAR
)
SET search_path TO duality, public;

ALTER PROCEDURE duality.sp_confirmar_venta(VARCHAR, VARCHAR)
SET search_path TO duality, public;

ALTER PROCEDURE duality.sp_finalizar_servicio(VARCHAR, VARCHAR)
SET search_path TO duality, public;

ALTER PROCEDURE duality.sp_registrar_pago(
    VARCHAR, VARCHAR, VARCHAR, NUMERIC, VARCHAR
)
SET search_path TO duality, public;

COMMIT;

-- Verificacion:
-- SELECT * FROM duality.vw_stock_actual;
-- SELECT * FROM duality.vw_dashboard;

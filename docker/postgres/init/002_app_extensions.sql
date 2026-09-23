-- ============================================================================
-- DUALITY - EXTENSION PARA APLICACION WEB Y MICROSERVICIOS
-- Se ejecuta despues de 001_schema.sql
-- ============================================================================

BEGIN;
SET search_path TO duality, public;

ALTER TABLE usuario ADD COLUMN IF NOT EXISTS password_hash VARCHAR(300);
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS ultimo_acceso TIMESTAMP;
ALTER TABLE usuario ADD COLUMN IF NOT EXISTS requiere_cambio_password BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS pago (
    id_pago          VARCHAR(20) PRIMARY KEY,
    id_venta         VARCHAR(20) NOT NULL,
    id_metodo_pago   VARCHAR(20) NOT NULL,
    id_usuario       VARCHAR(20) NOT NULL,
    monto            NUMERIC(10,2) NOT NULL,
    fecha_hora       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    referencia       VARCHAR(120),
    estado           VARCHAR(20) NOT NULL DEFAULT 'REGISTRADO',
    CONSTRAINT fk_pago_venta FOREIGN KEY(id_venta) REFERENCES venta(id_venta) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pago_metodo FOREIGN KEY(id_metodo_pago) REFERENCES metodo_pago(id_metodo_pago) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pago_usuario FOREIGN KEY(id_usuario) REFERENCES usuario(id_usuario) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_pago_monto CHECK(monto > 0),
    CONSTRAINT ck_pago_estado CHECK(estado IN ('REGISTRADO','ANULADO'))
);
CREATE INDEX IF NOT EXISTS idx_pago_venta ON pago(id_venta);
CREATE INDEX IF NOT EXISTS idx_pago_fecha ON pago(fecha_hora);

CREATE OR REPLACE VIEW vw_estado_cuenta_venta AS
SELECT v.id_venta,v.total,v.estado,
       COALESCE(SUM(p.monto) FILTER (WHERE p.estado='REGISTRADO'),0)::NUMERIC(10,2) AS pagado,
       GREATEST(v.total-COALESCE(SUM(p.monto) FILTER (WHERE p.estado='REGISTRADO'),0),0)::NUMERIC(10,2) AS saldo
FROM venta v LEFT JOIN pago p USING(id_venta)
GROUP BY v.id_venta,v.total,v.estado;

CREATE OR REPLACE PROCEDURE sp_confirmar_venta(p_id_venta VARCHAR,p_id_usuario VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_estado VARCHAR(20); v_total NUMERIC(10,2); v_pagado NUMERIC(10,2); r RECORD; v_stock NUMERIC(10,2);
BEGIN
    SELECT estado,total INTO v_estado,v_total FROM venta WHERE id_venta=p_id_venta FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'Venta % no existe',p_id_venta; END IF;
    IF v_estado <> 'PENDIENTE' THEN RAISE EXCEPTION 'La venta % no esta PENDIENTE. Estado actual: %',p_id_venta,v_estado; END IF;
    IF NOT EXISTS(SELECT 1 FROM usuario WHERE id_usuario=p_id_usuario AND activo=TRUE) THEN RAISE EXCEPTION 'Usuario % inexistente o inactivo',p_id_usuario; END IF;
    IF NOT EXISTS(SELECT 1 FROM detalle_venta WHERE id_venta=p_id_venta) THEN RAISE EXCEPTION 'La venta % no contiene productos',p_id_venta; END IF;
    SELECT COALESCE(SUM(monto),0) INTO v_pagado FROM pago WHERE id_venta=p_id_venta AND estado='REGISTRADO';
    IF v_pagado < v_total THEN RAISE EXCEPTION 'Pago insuficiente. Total %, pagado %',v_total,v_pagado; END IF;

    FOR r IN SELECT id_producto FROM detalle_venta WHERE id_venta=p_id_venta GROUP BY id_producto ORDER BY id_producto LOOP
        PERFORM 1 FROM producto WHERE id_producto=r.id_producto FOR UPDATE;
    END LOOP;
    FOR r IN SELECT id_producto,SUM(cantidad)::NUMERIC(10,2) cantidad FROM detalle_venta WHERE id_venta=p_id_venta GROUP BY id_producto ORDER BY id_producto LOOP
        v_stock:=fn_stock_producto(r.id_producto);
        IF v_stock < r.cantidad THEN RAISE EXCEPTION 'Stock insuficiente. Producto %, disponible %, requerido %',r.id_producto,v_stock,r.cantidad; END IF;
    END LOOP;
    FOR r IN SELECT id_producto,SUM(cantidad)::NUMERIC(10,2) cantidad FROM detalle_venta WHERE id_venta=p_id_venta GROUP BY id_producto ORDER BY id_producto LOOP
        INSERT INTO movimiento_inventario(id_movimiento,id_producto,id_usuario,tipo_movimiento,cantidad,fecha_hora,origen_tipo,origen_id,motivo)
        VALUES(fn_generar_id20(),r.id_producto,p_id_usuario,'SALIDA',r.cantidad,CURRENT_TIMESTAMP,'VENTA',p_id_venta,'Salida automatica por confirmacion de venta');
    END LOOP;
    UPDATE venta SET estado='CONFIRMADA',total=fn_total_venta(p_id_venta) WHERE id_venta=p_id_venta;
END; $$;

CREATE OR REPLACE PROCEDURE sp_registrar_pago(
    p_id_venta VARCHAR,p_id_metodo_pago VARCHAR,p_id_usuario VARCHAR,p_monto NUMERIC,p_referencia VARCHAR DEFAULT NULL
) LANGUAGE plpgsql AS $$
DECLARE v_total NUMERIC(10,2); v_estado VARCHAR(20); v_pagado NUMERIC(10,2);
BEGIN
    SELECT total,estado INTO v_total,v_estado FROM venta WHERE id_venta=p_id_venta FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'Venta % no existe',p_id_venta; END IF;
    IF v_estado <> 'PENDIENTE' THEN RAISE EXCEPTION 'La venta ya no acepta pagos. Estado: %',v_estado; END IF;
    IF p_monto IS NULL OR p_monto <= 0 THEN RAISE EXCEPTION 'El monto debe ser mayor que cero'; END IF;
    SELECT COALESCE(SUM(monto),0) INTO v_pagado FROM pago WHERE id_venta=p_id_venta AND estado='REGISTRADO';
    IF v_pagado+p_monto > v_total THEN RAISE EXCEPTION 'El pago excede el saldo pendiente de %',v_total-v_pagado; END IF;
    INSERT INTO pago(id_pago,id_venta,id_metodo_pago,id_usuario,monto,referencia)
    VALUES(fn_generar_id20(),p_id_venta,p_id_metodo_pago,p_id_usuario,p_monto,p_referencia);
    IF v_pagado+p_monto >= v_total THEN CALL sp_confirmar_venta(p_id_venta,p_id_usuario); END IF;
END; $$;

CREATE OR REPLACE VIEW vw_pagos_resumen AS
SELECT p.id_pago,p.id_venta,p.fecha_hora,p.monto,p.referencia,p.estado,mp.nombre AS metodo_pago,u.nombre_completo AS usuario_responsable
FROM pago p JOIN metodo_pago mp USING(id_metodo_pago) JOIN usuario u USING(id_usuario);

CREATE OR REPLACE VIEW vw_dashboard AS
SELECT
  (SELECT COUNT(*) FROM paciente WHERE activo=TRUE) AS pacientes_activos,
  (SELECT COUNT(*) FROM producto WHERE activo=TRUE) AS productos_activos,
  (SELECT COUNT(*) FROM servicio WHERE activo=TRUE) AS servicios_activos,
  (SELECT COUNT(*) FROM vw_productos_bajo_minimo) AS productos_bajo_minimo,
  (SELECT COUNT(*) FROM venta WHERE estado='CONFIRMADA' AND fecha_hora::date=CURRENT_DATE) AS ventas_hoy,
  (SELECT COALESCE(SUM(total),0) FROM venta WHERE estado='CONFIRMADA' AND fecha_hora::date=CURRENT_DATE)::NUMERIC(10,2) AS ingresos_hoy;

-- Usuario administrador academico inicial. Contraseña: Admin123!
INSERT INTO usuario(id_usuario,id_rol,nombre_completo,correo,telefono,activo,password_hash,requiere_cambio_password)
VALUES('USR_ADMIN','ROL_ADMIN','Administrador Duality','admin@duality.local',NULL,TRUE,
'pbkdf2_sha256$390000$ZHVhbGl0eS1hZG1pbi1zYWx0LTIwMjY$2MW2B_GpBlgNrs7VVsSCxpVZgcQ7o6DY59HGJmwHlfk',TRUE)
ON CONFLICT(correo) DO UPDATE SET password_hash=EXCLUDED.password_hash,id_rol='ROL_ADMIN',activo=TRUE;

COMMIT;

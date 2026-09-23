-- ============================================================================
-- DUALITY - CLINICA DE MEDICINA ESTETICA
-- IMPLEMENTACION DE BASE DE DATOS - POSTGRESQL 16+
-- Entrega academica: 12 de septiembre de 2026
-- ============================================================================
-- El script crea el esquema, tablas, restricciones, indices, funciones,
-- disparadores, procedimientos almacenados, vistas y datos catalogo iniciales.
-- Para un entorno academico reproducible se elimina y recrea el esquema DUALITY.
-- En produccion, sustituir esta estrategia por migraciones versionadas.
-- ============================================================================

BEGIN;

DROP SCHEMA IF EXISTS duality CASCADE;
CREATE SCHEMA duality;
SET search_path TO duality, public;

-- ==========================================================================
-- 1. TABLAS
-- ==========================================================================

CREATE TABLE rol (
    id_rol          VARCHAR(20)  PRIMARY KEY,
    nombre          VARCHAR(50)  NOT NULL UNIQUE,
    descripcion     VARCHAR(200),
    activo          BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE usuario (
    id_usuario      VARCHAR(20)  PRIMARY KEY,
    id_rol          VARCHAR(20)  NOT NULL,
    nombre_completo VARCHAR(120) NOT NULL,
    correo          VARCHAR(150) NOT NULL UNIQUE,
    telefono        VARCHAR(25),
    activo          BOOLEAN      NOT NULL DEFAULT TRUE,
    fecha_creacion  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_rol
        FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_usuario_correo
        CHECK (POSITION('@' IN correo) > 1)
);

CREATE TABLE paciente (
    id_paciente      VARCHAR(20)  PRIMARY KEY,
    nombres          VARCHAR(100) NOT NULL,
    apellidos        VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    telefono         VARCHAR(25),
    correo           VARCHAR(150),
    observaciones    TEXT,
    fecha_registro   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activo           BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_paciente_correo
        CHECK (correo IS NULL OR POSITION('@' IN correo) > 1)
);

CREATE TABLE servicio (
    id_servicio   VARCHAR(20)   PRIMARY KEY,
    nombre        VARCHAR(120)  NOT NULL UNIQUE,
    descripcion   VARCHAR(300),
    precio_base   NUMERIC(10,2) NOT NULL,
    duracion_min  INTEGER,
    activo        BOOLEAN       NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_servicio_precio CHECK (precio_base >= 0),
    CONSTRAINT ck_servicio_duracion CHECK (duracion_min IS NULL OR duracion_min > 0)
);

CREATE TABLE producto (
    id_producto    VARCHAR(20)   PRIMARY KEY,
    sku            VARCHAR(50)   UNIQUE,
    nombre         VARCHAR(150)  NOT NULL,
    descripcion    VARCHAR(300),
    costo_unitario NUMERIC(10,2),
    precio_venta   NUMERIC(10,2) NOT NULL,
    stock_minimo   NUMERIC(10,2),
    activo         BOOLEAN       NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_producto_costo CHECK (costo_unitario IS NULL OR costo_unitario >= 0),
    CONSTRAINT ck_producto_precio CHECK (precio_venta >= 0),
    CONSTRAINT ck_producto_stock_minimo CHECK (stock_minimo IS NULL OR stock_minimo >= 0)
);

-- stock_actual NO se persiste fisicamente. Se calcula a partir de
-- movimiento_inventario y se expone mediante vw_stock_actual.

CREATE TABLE metodo_pago (
    id_metodo_pago VARCHAR(20) PRIMARY KEY,
    nombre         VARCHAR(60) NOT NULL UNIQUE,
    activo         BOOLEAN     NOT NULL DEFAULT TRUE
);

CREATE TABLE venta (
    id_venta        VARCHAR(20)   PRIMARY KEY,
    id_paciente     VARCHAR(20),
    id_usuario      VARCHAR(20)   NOT NULL,
    id_metodo_pago  VARCHAR(20)   NOT NULL,
    fecha_hora      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    subtotal        NUMERIC(10,2) NOT NULL DEFAULT 0,
    descuento       NUMERIC(10,2) NOT NULL DEFAULT 0,
    total           NUMERIC(10,2) NOT NULL DEFAULT 0,
    estado          VARCHAR(20)   NOT NULL DEFAULT 'PENDIENTE',
    observaciones   VARCHAR(300),
    CONSTRAINT fk_venta_paciente
        FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_venta_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_venta_metodo_pago
        FOREIGN KEY (id_metodo_pago) REFERENCES metodo_pago(id_metodo_pago)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_venta_montos CHECK (
        subtotal >= 0 AND descuento >= 0 AND total >= 0 AND descuento <= subtotal
    ),
    CONSTRAINT ck_venta_estado CHECK (estado IN ('PENDIENTE','CONFIRMADA','ANULADA'))
);

CREATE TABLE detalle_venta (
    id_detalle_venta VARCHAR(20)   PRIMARY KEY,
    id_venta         VARCHAR(20)   NOT NULL,
    id_producto      VARCHAR(20)   NOT NULL,
    cantidad         NUMERIC(10,2) NOT NULL,
    precio_unitario  NUMERIC(10,2) NOT NULL,
    subtotal         NUMERIC(10,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_detalle_venta_venta
        FOREIGN KEY (id_venta) REFERENCES venta(id_venta)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_detalle_venta_producto
        FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_detalle_venta_producto UNIQUE (id_venta, id_producto),
    CONSTRAINT ck_detalle_venta_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_detalle_venta_precio CHECK (precio_unitario >= 0),
    CONSTRAINT ck_detalle_venta_subtotal CHECK (subtotal >= 0)
);

CREATE TABLE servicio_realizado (
    id_servicio_realizado VARCHAR(20)   PRIMARY KEY,
    id_paciente           VARCHAR(20)   NOT NULL,
    id_servicio           VARCHAR(20)   NOT NULL,
    id_usuario            VARCHAR(20)   NOT NULL,
    id_venta              VARCHAR(20),
    fecha_hora            TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    precio_aplicado       NUMERIC(10,2),
    estado                VARCHAR(20)   NOT NULL DEFAULT 'BORRADOR',
    observaciones         TEXT,
    CONSTRAINT fk_servicio_realizado_paciente
        FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_servicio_realizado_servicio
        FOREIGN KEY (id_servicio) REFERENCES servicio(id_servicio)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_servicio_realizado_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_servicio_realizado_venta
        FOREIGN KEY (id_venta) REFERENCES venta(id_venta)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT ck_servicio_realizado_precio CHECK (precio_aplicado IS NULL OR precio_aplicado >= 0),
    CONSTRAINT ck_servicio_realizado_estado CHECK (
        estado IN ('BORRADOR','VALIDADO','CONFIRMADO','FINALIZADO','ANULADO')
    )
);

CREATE TABLE consumo_servicio (
    id_consumo              VARCHAR(20)   PRIMARY KEY,
    id_servicio_realizado   VARCHAR(20)   NOT NULL,
    id_producto             VARCHAR(20)   NOT NULL,
    cantidad                NUMERIC(10,2) NOT NULL,
    observaciones           VARCHAR(200),
    CONSTRAINT fk_consumo_servicio_realizado
        FOREIGN KEY (id_servicio_realizado) REFERENCES servicio_realizado(id_servicio_realizado)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_consumo_producto
        FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_consumo_servicio_producto UNIQUE (id_servicio_realizado, id_producto),
    CONSTRAINT ck_consumo_cantidad CHECK (cantidad > 0)
);

CREATE TABLE movimiento_inventario (
    id_movimiento     VARCHAR(20)   PRIMARY KEY,
    id_producto       VARCHAR(20)   NOT NULL,
    id_usuario        VARCHAR(20)   NOT NULL,
    tipo_movimiento   VARCHAR(20)   NOT NULL,
    cantidad          NUMERIC(10,2) NOT NULL,
    fecha_hora        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    origen_tipo       VARCHAR(30),
    origen_id         VARCHAR(20),
    motivo            VARCHAR(250),
    stock_resultante  NUMERIC(10,2),
    CONSTRAINT fk_movimiento_producto
        FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_movimiento_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT ck_movimiento_tipo CHECK (
        tipo_movimiento IN ('ENTRADA','SALIDA','AJUSTE_POSITIVO','AJUSTE_NEGATIVO')
    ),
    CONSTRAINT ck_movimiento_cantidad CHECK (cantidad > 0),
    CONSTRAINT ck_movimiento_origen CHECK (
        origen_tipo IS NULL OR origen_tipo IN ('VENTA','SERVICIO','COMPRA','AJUSTE')
    ),
    CONSTRAINT ck_movimiento_stock_resultante CHECK (
        stock_resultante IS NULL OR stock_resultante >= 0
    )
);

-- Indices para claves foraneas y consultas operativas frecuentes.
CREATE INDEX idx_usuario_rol ON usuario(id_rol);
CREATE INDEX idx_venta_paciente ON venta(id_paciente);
CREATE INDEX idx_venta_usuario ON venta(id_usuario);
CREATE INDEX idx_venta_fecha ON venta(fecha_hora);
CREATE INDEX idx_detalle_venta_venta ON detalle_venta(id_venta);
CREATE INDEX idx_detalle_venta_producto ON detalle_venta(id_producto);
CREATE INDEX idx_servicio_realizado_paciente ON servicio_realizado(id_paciente);
CREATE INDEX idx_servicio_realizado_fecha ON servicio_realizado(fecha_hora);
CREATE INDEX idx_consumo_servicio_realizado ON consumo_servicio(id_servicio_realizado);
CREATE INDEX idx_movimiento_producto_fecha ON movimiento_inventario(id_producto, fecha_hora);
CREATE INDEX idx_movimiento_usuario ON movimiento_inventario(id_usuario);
CREATE INDEX idx_movimiento_origen ON movimiento_inventario(origen_tipo, origen_id);

-- ==========================================================================
-- 2. FUNCIONES
-- ==========================================================================

CREATE OR REPLACE FUNCTION fn_generar_id20()
RETURNS VARCHAR(20)
LANGUAGE plpgsql
VOLATILE
AS $$
BEGIN
    RETURN SUBSTRING(MD5(CLOCK_TIMESTAMP()::TEXT || RANDOM()::TEXT) FROM 1 FOR 20);
END;
$$;

CREATE OR REPLACE FUNCTION fn_stock_producto(p_id_producto VARCHAR)
RETURNS NUMERIC(10,2)
LANGUAGE sql
STABLE
AS $$
    SELECT COALESCE(SUM(
        CASE
            WHEN tipo_movimiento IN ('ENTRADA','AJUSTE_POSITIVO') THEN cantidad
            WHEN tipo_movimiento IN ('SALIDA','AJUSTE_NEGATIVO') THEN -cantidad
            ELSE 0
        END
    ), 0)::NUMERIC(10,2)
    FROM movimiento_inventario
    WHERE id_producto = p_id_producto;
$$;

CREATE OR REPLACE FUNCTION fn_total_venta(p_id_venta VARCHAR)
RETURNS NUMERIC(10,2)
LANGUAGE sql
STABLE
AS $$
    SELECT GREATEST(
        COALESCE(SUM(d.subtotal), 0) - COALESCE(v.descuento, 0),
        0
    )::NUMERIC(10,2)
    FROM venta v
    LEFT JOIN detalle_venta d ON d.id_venta = v.id_venta
    WHERE v.id_venta = p_id_venta
    GROUP BY v.id_venta, v.descuento;
$$;

-- ==========================================================================
-- 3. FUNCIONES DE TRIGGER Y DISPARADORES
-- ==========================================================================

CREATE OR REPLACE FUNCTION tg_detalle_venta_calcular_subtotal()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.cantidad <= 0 THEN
        RAISE EXCEPTION 'La cantidad del detalle debe ser mayor que cero';
    END IF;
    IF NEW.precio_unitario < 0 THEN
        RAISE EXCEPTION 'El precio unitario no puede ser negativo';
    END IF;

    NEW.subtotal := ROUND(NEW.cantidad * NEW.precio_unitario, 2);
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_detalle_venta_calcular_subtotal
BEFORE INSERT OR UPDATE OF cantidad, precio_unitario
ON detalle_venta
FOR EACH ROW
EXECUTE FUNCTION tg_detalle_venta_calcular_subtotal();

CREATE OR REPLACE FUNCTION tg_recalcular_totales_venta()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_venta VARCHAR(20);
    v_subtotal NUMERIC(10,2);
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_id_venta := OLD.id_venta;
    ELSE
        v_id_venta := NEW.id_venta;
    END IF;

    SELECT COALESCE(SUM(subtotal), 0)::NUMERIC(10,2)
      INTO v_subtotal
      FROM detalle_venta
     WHERE id_venta = v_id_venta;

    UPDATE venta
       SET subtotal = v_subtotal,
           total = GREATEST(v_subtotal - descuento, 0)
     WHERE id_venta = v_id_venta;

    IF TG_OP = 'UPDATE' AND OLD.id_venta <> NEW.id_venta THEN
        SELECT COALESCE(SUM(subtotal), 0)::NUMERIC(10,2)
          INTO v_subtotal
          FROM detalle_venta
         WHERE id_venta = OLD.id_venta;

        UPDATE venta
           SET subtotal = v_subtotal,
               total = GREATEST(v_subtotal - descuento, 0)
         WHERE id_venta = OLD.id_venta;
    END IF;

    RETURN NULL;
END;
$$;

CREATE TRIGGER trg_recalcular_totales_venta
AFTER INSERT OR UPDATE OR DELETE
ON detalle_venta
FOR EACH ROW
EXECUTE FUNCTION tg_recalcular_totales_venta();

CREATE OR REPLACE FUNCTION tg_movimiento_validar_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_stock_actual NUMERIC(10,2);
    v_delta        NUMERIC(10,2);
    v_stock_nuevo  NUMERIC(10,2);
BEGIN
    -- Bloqueo de la fila del producto: serializa movimientos concurrentes
    -- del mismo producto y sustituye el mecanismo LockService usado en la
    -- arquitectura inicial con Google Sheets.
    PERFORM 1
      FROM producto
     WHERE id_producto = NEW.id_producto
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Producto % no existe', NEW.id_producto;
    END IF;

    v_stock_actual := fn_stock_producto(NEW.id_producto);

    v_delta := CASE
        WHEN NEW.tipo_movimiento IN ('ENTRADA','AJUSTE_POSITIVO') THEN NEW.cantidad
        WHEN NEW.tipo_movimiento IN ('SALIDA','AJUSTE_NEGATIVO') THEN -NEW.cantidad
        ELSE 0
    END;

    v_stock_nuevo := v_stock_actual + v_delta;

    IF v_stock_nuevo < 0 THEN
        RAISE EXCEPTION
            'Stock insuficiente para producto %. Stock actual: %, movimiento: % %',
            NEW.id_producto, v_stock_actual, NEW.tipo_movimiento, NEW.cantidad;
    END IF;

    NEW.stock_resultante := v_stock_nuevo;
    NEW.fecha_hora := COALESCE(NEW.fecha_hora, CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_movimiento_validar_stock
BEFORE INSERT
ON movimiento_inventario
FOR EACH ROW
EXECUTE FUNCTION tg_movimiento_validar_stock();

CREATE OR REPLACE FUNCTION tg_movimiento_inmutable()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION
        'Los movimientos de inventario son inmutables. Registre un ajuste compensatorio.';
END;
$$;

CREATE TRIGGER trg_movimiento_inmutable
BEFORE UPDATE OR DELETE
ON movimiento_inventario
FOR EACH ROW
EXECUTE FUNCTION tg_movimiento_inmutable();

-- ==========================================================================
-- 4. PROCEDIMIENTOS ALMACENADOS
-- ==========================================================================

CREATE OR REPLACE PROCEDURE sp_registrar_movimiento_inventario(
    p_id_producto      VARCHAR,
    p_id_usuario       VARCHAR,
    p_tipo_movimiento  VARCHAR,
    p_cantidad         NUMERIC,
    p_origen_tipo      VARCHAR DEFAULT 'AJUSTE',
    p_origen_id        VARCHAR DEFAULT NULL,
    p_motivo           VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_cantidad IS NULL OR p_cantidad <= 0 THEN
        RAISE EXCEPTION 'La cantidad debe ser mayor que cero';
    END IF;

    IF p_tipo_movimiento NOT IN ('ENTRADA','SALIDA','AJUSTE_POSITIVO','AJUSTE_NEGATIVO') THEN
        RAISE EXCEPTION 'Tipo de movimiento invalido: %', p_tipo_movimiento;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM usuario WHERE id_usuario = p_id_usuario AND activo = TRUE) THEN
        RAISE EXCEPTION 'Usuario % inexistente o inactivo', p_id_usuario;
    END IF;

    INSERT INTO movimiento_inventario (
        id_movimiento, id_producto, id_usuario, tipo_movimiento,
        cantidad, fecha_hora, origen_tipo, origen_id, motivo
    ) VALUES (
        fn_generar_id20(), p_id_producto, p_id_usuario, p_tipo_movimiento,
        p_cantidad, CURRENT_TIMESTAMP, p_origen_tipo, p_origen_id, p_motivo
    );
END;
$$;

CREATE OR REPLACE PROCEDURE sp_confirmar_venta(
    p_id_venta   VARCHAR,
    p_id_usuario VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_estado VARCHAR(20);
    r RECORD;
    v_stock NUMERIC(10,2);
BEGIN
    SELECT estado
      INTO v_estado
      FROM venta
     WHERE id_venta = p_id_venta
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Venta % no existe', p_id_venta;
    END IF;

    IF v_estado <> 'PENDIENTE' THEN
        RAISE EXCEPTION 'La venta % no esta PENDIENTE. Estado actual: %', p_id_venta, v_estado;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM usuario WHERE id_usuario = p_id_usuario AND activo = TRUE) THEN
        RAISE EXCEPTION 'Usuario % inexistente o inactivo', p_id_usuario;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM detalle_venta WHERE id_venta = p_id_venta) THEN
        RAISE EXCEPTION 'La venta % no contiene productos', p_id_venta;
    END IF;

    -- Bloqueo deterministico de productos involucrados para reducir riesgo
    -- de deadlocks cuando existan ventas concurrentes con productos comunes.
    FOR r IN
        SELECT id_producto
          FROM detalle_venta
         WHERE id_venta = p_id_venta
         GROUP BY id_producto
         ORDER BY id_producto
    LOOP
        PERFORM 1 FROM producto WHERE id_producto = r.id_producto FOR UPDATE;
    END LOOP;

    -- Validacion integral antes de generar cualquier salida.
    FOR r IN
        SELECT id_producto, SUM(cantidad)::NUMERIC(10,2) AS cantidad
          FROM detalle_venta
         WHERE id_venta = p_id_venta
         GROUP BY id_producto
         ORDER BY id_producto
    LOOP
        v_stock := fn_stock_producto(r.id_producto);
        IF v_stock < r.cantidad THEN
            RAISE EXCEPTION
                'Stock insuficiente. Producto %, disponible %, requerido %',
                r.id_producto, v_stock, r.cantidad;
        END IF;
    END LOOP;

    -- Insercion de movimientos. Si cualquier paso falla, la llamada completa
    -- se revierte por la transaccion que contiene el CALL.
    FOR r IN
        SELECT id_producto, SUM(cantidad)::NUMERIC(10,2) AS cantidad
          FROM detalle_venta
         WHERE id_venta = p_id_venta
         GROUP BY id_producto
         ORDER BY id_producto
    LOOP
        INSERT INTO movimiento_inventario (
            id_movimiento, id_producto, id_usuario, tipo_movimiento,
            cantidad, fecha_hora, origen_tipo, origen_id, motivo
        ) VALUES (
            fn_generar_id20(), r.id_producto, p_id_usuario, 'SALIDA',
            r.cantidad, CURRENT_TIMESTAMP, 'VENTA', p_id_venta,
            'Salida automatica por confirmacion de venta'
        );
    END LOOP;

    UPDATE venta
       SET estado = 'CONFIRMADA',
           total = fn_total_venta(p_id_venta)
     WHERE id_venta = p_id_venta;
END;
$$;

CREATE OR REPLACE PROCEDURE sp_finalizar_servicio(
    p_id_servicio_realizado VARCHAR,
    p_id_usuario            VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_estado VARCHAR(20);
    r RECORD;
    v_stock NUMERIC(10,2);
BEGIN
    SELECT estado
      INTO v_estado
      FROM servicio_realizado
     WHERE id_servicio_realizado = p_id_servicio_realizado
     FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Servicio realizado % no existe', p_id_servicio_realizado;
    END IF;

    IF v_estado IN ('FINALIZADO','ANULADO') THEN
        RAISE EXCEPTION 'El servicio no puede finalizarse desde estado %', v_estado;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM usuario WHERE id_usuario = p_id_usuario AND activo = TRUE) THEN
        RAISE EXCEPTION 'Usuario % inexistente o inactivo', p_id_usuario;
    END IF;

    FOR r IN
        SELECT id_producto, SUM(cantidad)::NUMERIC(10,2) AS cantidad
          FROM consumo_servicio
         WHERE id_servicio_realizado = p_id_servicio_realizado
         GROUP BY id_producto
         ORDER BY id_producto
    LOOP
        PERFORM 1 FROM producto WHERE id_producto = r.id_producto FOR UPDATE;
    END LOOP;

    FOR r IN
        SELECT id_producto, SUM(cantidad)::NUMERIC(10,2) AS cantidad
          FROM consumo_servicio
         WHERE id_servicio_realizado = p_id_servicio_realizado
         GROUP BY id_producto
         ORDER BY id_producto
    LOOP
        v_stock := fn_stock_producto(r.id_producto);
        IF v_stock < r.cantidad THEN
            RAISE EXCEPTION
                'Stock insuficiente. Producto %, disponible %, requerido %',
                r.id_producto, v_stock, r.cantidad;
        END IF;
    END LOOP;

    FOR r IN
        SELECT id_producto, SUM(cantidad)::NUMERIC(10,2) AS cantidad
          FROM consumo_servicio
         WHERE id_servicio_realizado = p_id_servicio_realizado
         GROUP BY id_producto
         ORDER BY id_producto
    LOOP
        INSERT INTO movimiento_inventario (
            id_movimiento, id_producto, id_usuario, tipo_movimiento,
            cantidad, fecha_hora, origen_tipo, origen_id, motivo
        ) VALUES (
            fn_generar_id20(), r.id_producto, p_id_usuario, 'SALIDA',
            r.cantidad, CURRENT_TIMESTAMP, 'SERVICIO', p_id_servicio_realizado,
            'Consumo de producto por finalizacion de servicio'
        );
    END LOOP;

    UPDATE servicio_realizado
       SET estado = 'FINALIZADO'
     WHERE id_servicio_realizado = p_id_servicio_realizado;
END;
$$;

-- ==========================================================================
-- 5. VISTAS
-- ==========================================================================

CREATE OR REPLACE VIEW vw_stock_actual AS
SELECT
    p.id_producto,
    p.sku,
    p.nombre,
    p.stock_minimo,
    fn_stock_producto(p.id_producto) AS stock_actual,
    CASE
        WHEN p.stock_minimo IS NOT NULL
         AND fn_stock_producto(p.id_producto) <= p.stock_minimo
        THEN TRUE ELSE FALSE
    END AS bajo_minimo,
    p.activo
FROM producto p;

CREATE OR REPLACE VIEW vw_productos_bajo_minimo AS
SELECT *
FROM vw_stock_actual
WHERE bajo_minimo = TRUE AND activo = TRUE;

CREATE OR REPLACE VIEW vw_ventas_resumen AS
SELECT
    v.id_venta,
    v.fecha_hora,
    v.estado,
    v.subtotal,
    v.descuento,
    v.total,
    COALESCE(p.nombres || ' ' || p.apellidos, 'Consumidor no identificado') AS paciente,
    u.nombre_completo AS usuario_responsable,
    mp.nombre AS metodo_pago
FROM venta v
LEFT JOIN paciente p ON p.id_paciente = v.id_paciente
JOIN usuario u ON u.id_usuario = v.id_usuario
JOIN metodo_pago mp ON mp.id_metodo_pago = v.id_metodo_pago;

CREATE OR REPLACE VIEW vw_movimientos_inventario_auditoria AS
SELECT
    m.id_movimiento,
    m.fecha_hora,
    p.id_producto,
    p.nombre AS producto,
    m.tipo_movimiento,
    m.cantidad,
    m.stock_resultante,
    m.origen_tipo,
    m.origen_id,
    m.motivo,
    u.id_usuario,
    u.nombre_completo AS usuario_responsable
FROM movimiento_inventario m
JOIN producto p ON p.id_producto = m.id_producto
JOIN usuario u ON u.id_usuario = m.id_usuario;

CREATE OR REPLACE VIEW vw_historial_paciente AS
SELECT
    p.id_paciente,
    p.nombres,
    p.apellidos,
    'SERVICIO'::VARCHAR(20) AS tipo_evento,
    sr.id_servicio_realizado AS id_evento,
    sr.fecha_hora,
    s.nombre AS detalle,
    sr.estado,
    sr.precio_aplicado AS importe
FROM paciente p
JOIN servicio_realizado sr ON sr.id_paciente = p.id_paciente
JOIN servicio s ON s.id_servicio = sr.id_servicio
UNION ALL
SELECT
    p.id_paciente,
    p.nombres,
    p.apellidos,
    'VENTA'::VARCHAR(20) AS tipo_evento,
    v.id_venta AS id_evento,
    v.fecha_hora,
    'Venta de productos'::VARCHAR(120) AS detalle,
    v.estado,
    v.total AS importe
FROM paciente p
JOIN venta v ON v.id_paciente = p.id_paciente;

-- ==========================================================================
-- 6. DATOS CATALOGO INICIALES
-- ==========================================================================

INSERT INTO rol (id_rol, nombre, descripcion, activo) VALUES
('ROL_ADMIN', 'Administrador', 'Administracion general de la solucion.', TRUE),
('ROL_OPER', 'Operativo', 'Registro de operaciones autorizadas.', TRUE),
('ROL_CONS', 'Consulta', 'Acceso de solo consulta a informacion permitida.', TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO metodo_pago (id_metodo_pago, nombre, activo) VALUES
('MP_EFECTIVO', 'Efectivo', TRUE),
('MP_TARJETA', 'Tarjeta', TRUE),
('MP_TRANSF', 'Transferencia', TRUE)
ON CONFLICT DO NOTHING;

-- ==========================================================================
-- 7. SEGURIDAD BASICA DEL ESQUEMA
-- ==========================================================================
-- Se elimina acceso implicito de PUBLIC. Los permisos a la cuenta tecnica de
-- la aplicacion deben otorgarse desde el ambiente de despliegue usando una
-- cuenta/rol dedicado y secretos fuera del codigo fuente.
REVOKE ALL ON SCHEMA duality FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA duality FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA duality FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA duality FROM PUBLIC;

COMMIT;

-- ==========================================================================
-- 8. CONSULTAS DE VERIFICACION (ejecutar despues del script)
-- ==========================================================================
-- SELECT table_name FROM information_schema.tables
--  WHERE table_schema = 'duality' ORDER BY table_name;
-- SELECT routine_name, routine_type FROM information_schema.routines
--  WHERE routine_schema = 'duality' ORDER BY routine_type, routine_name;
-- SELECT * FROM duality.vw_stock_actual;
-- SELECT * FROM duality.vw_ventas_resumen ORDER BY fecha_hora DESC;
-- SELECT * FROM duality.vw_movimientos_inventario_auditoria ORDER BY fecha_hora DESC;
--
-- Ejemplo de entrada manual de inventario:
-- CALL duality.sp_registrar_movimiento_inventario(
--   'PROD001','USR001','ENTRADA',10,'COMPRA','COMP001','Ingreso inicial'
-- );
--
-- Ejemplo de confirmacion de venta:
-- CALL duality.sp_confirmar_venta('VTA001','USR001');
--
-- Ejemplo de finalizacion de servicio:
-- CALL duality.sp_finalizar_servicio('SRVREAL001','USR001');

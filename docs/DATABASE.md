# Base de datos PostgreSQL

La implementación parte del Modelo Relacional del Entregable 7 corregido. Las tablas principales son:

`rol`, `usuario`, `paciente`, `servicio`, `producto`, `metodo_pago`, `venta`, `detalle_venta`, `servicio_realizado`, `consumo_servicio`, `movimiento_inventario` y la extensión operativa `pago`.

La relación **USUARIO 1:N MOVIMIENTO_INVENTARIO** está implementada con `movimiento_inventario.id_usuario` como FK obligatoria.

## Objetos SQL

### Funciones
- `fn_generar_id20`
- `fn_stock_producto`
- `fn_total_venta`
- funciones internas de triggers

### Procedimientos
- `sp_registrar_movimiento_inventario`
- `sp_confirmar_venta`
- `sp_finalizar_servicio`
- `sp_registrar_pago`

### Triggers
- cálculo de subtotal de detalle
- recálculo de totales de venta
- validación concurrente del stock
- inmutabilidad de movimientos

### Vistas
- `vw_stock_actual`
- `vw_productos_bajo_minimo`
- `vw_ventas_resumen`
- `vw_movimientos_inventario_auditoria`
- `vw_historial_paciente`
- `vw_pagos_resumen`
- `vw_estado_cuenta_venta`
- `vw_dashboard`

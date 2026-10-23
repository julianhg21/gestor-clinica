# Gestión de incidentes — procedimiento propuesto

Estado: Propuesto (C28). La clínica debe designar coordinador, suplente, canal de reporte y autoridad para detener operaciones/notificar; no existen contactos ni aprobaciones confirmados. No se han ejecutado simulacros con personal real.

1. Reportar: usuario comunica hora, servicio, síntoma y efecto por canal por aprobar; no enviar pacientes/contraseñas ni tokens.
2. Registrar: ID INC, fecha/hora con zona, informante autorizado, activo A, riesgo R, alcance, severidad preliminar y custodio.
3. Clasificar: alta si compromete pacientes, integridad de pagos/inventario o continuidad; media si es localizada recuperable; baja si carece de impacto confirmado. Escalar a autoridad de negocio.
4. Preservar: recolectar logs sanitizados, commit, configuración pertinente y hashes; registrar quién obtiene/transfiere evidencia, hora y acceso. No borrar ni reiniciar a ciegas.
5. Contener/erradicar según escenarios; cambios de credenciales o infraestructura real necesitan autoridad designada.
6. Recuperar en aislamiento, probar identidad/integridad y obtener aprobación para retorno del servicio.
7. Cerrar: causa, impacto real, acciones, tiempos, evidencia, residual y revisión de política; responsables de comunicación externa/legal por confirmar.

| Escenario | Activo/riesgo/control | Respuesta concreta propuesta | Criterio de recuperación |
|---|---|---|---|
| Cuenta o JWT comprometido | A03/R01-R03/C02-C05 | Desactivar cuenta; revocar jti si Redis disponible; evaluar rotación con impacto en todas las sesiones; investigar accesos | Token anterior rechazado, usuario vigente autorizado y evidencia protegida |
| Redis no disponible | A03/R01/C03 | 503 impide verificar sesión; alertar; restaurar servicio y persistencia; no cambiar a fallo abierto | Verificación y logout funcionan con Redis; probar jti previamente revocado |
| Stock/pagos inconsistentes | A02/R05/C09-C10 | Suspender operaciones afectadas, preservar movimientos/transacciones, conciliar; ajustes compensatorios autorizados | Totales, saldo, kardex e historial conciliados |
| Dependencia o despliegue defectuoso | A07-A08/R08-R09/C22-C26 | Bloquear promoción, identificar versión y exposición, probar corrección; rollback compatible sin borrar datos | Regresión aprobada, artefacto conocido y validación autorizada |
| Pérdida BD/proveedor | A02-A09/R10-R12/C11,C27,C31 | Evaluar alcance con proveedor, proteger copia, restaurar en destino distinto y verificar | Recuperación validada y aprobación de retorno; RTO/RPO medidos contra objetivos acordados |

Plantilla de registro: INC-ID; hora inicio/detección/contención/recuperación; activo y control; evidencia SHA256; acciones y autorización; responsables; impacto confirmado; datos potencialmente afectados; comunicación; causa y lecciones; cierre/aceptación residual. Hacer ejercicio de mesa con casos sintéticos antes de acreditar operación.

# Controles implementados y límites de validación

La matriz de cumplimiento y controles.json son la fuente única del estado detallado. Se conservaron consultas/contratos y modelo de pacientes, inventario, servicios, ventas, pagos y reportes. La regresión existente es principalmente de contratos; su aprobación no equivale a aceptación completa de todos los flujos en UI.

Cambios de seguridad: claims obligatorios y tipos de JWT; Redis con límites de conexión/lectura y 503 ante fallo de verificación/revocación; consulta de usuario activo y rol vigente por petición; codificación de salida en tablas/selects/perfil/errores e identificadores en handlers; retirada de credenciales del formulario; pipelines con fallo explícito y análisis de dependencias/estático; evidencia reproducible con hashes.

Validación técnica suficiente en alcance local: PBKDF2, validación JWT, parametrización del login, restricciones e inmutabilidad del inventario, carreras de stock/pagos probadas y restauración sintética, formulario sin prefill y metadatos de ejecución. Revocación, identidad/roles, XSS y pipelines conservan estado parcial por integración/cobertura/ejecución externa pendientes.

Controles existentes utilizados: transacciones psycopg, procedimientos y bloqueos FOR UPDATE, PK/FK/CHECK, trazabilidad de usuario, salt aleatorio, roles backend, usuario de contenedor Python 65532. No se modificaron modelos ni se ejecutaron scripts SQL en datos persistentes de usuario.

No se atribuyen como implementados: HTTPS público, rol mínimo de BD, rotación de secretos reales, MFA, auditoría central, protección de ramas, backups automáticos, objetivos RTO/RPO, firewall/VLAN/EDR o recursos cloud. El ensayo read-only/cap-drop de la imagen auth no modifica Compose. Las dependencias no se actualizaron automáticamente porque la familia Starlette requerida por FastAPI 0.115.6 limita la corrección y PyJWT forma parte de autenticación; preparar migración compatible y autorización correspondiente.

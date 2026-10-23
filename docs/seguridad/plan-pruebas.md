# Plan de pruebas controladas

Propósito: verificar controles del código sin producción ni datos personales. Ambiente: Python 3.12.14 Windows; TestClient con Redis/BD simulados para identidad; PostgreSQL 16.15 Linux en contenedor desechable para SQL. Variables STAGING_BASE_URL/SMOKE_BASE_URL se retiran por el colector. Ningún test accede a proveedores. Tokens/contraseñas sintéticos no se imprimen; nombres de casos usan IDs estables sin valores sensibles.

| Caso | Control / riesgo | Positivo | Negativo / límite | Evidencia |
|---|---|---|---|---|
| T01 | C01/R02 | Hash y verificación con salt distinto | Contraseña incorrecta/hash malformado | E01 |
| T02 | C02,C04/R01,R03 | Login válido y JWT emitido | Login incorrecto/inactivo, JWT expirado, firma distinta, claims ausentes o tipos inválidos | E01 |
| T03 | C03/R01 | Petición antes de logout | JWT revocado; fallos GET/SETEX Redis producen 503 | E01 (dobles) |
| T04 | C04,C05/R03 | Cuenta activa y mismo rol | Sin token en cuatro servicios, rol insuficiente, cuenta eliminada/desactivada/rol cambiado, BD caída | E01 (dobles) |
| T05 | C07,C08/R05,R06 | Consulta parametrizada | Correo tipo SQL injection permanece parámetro; monto negativo 422 | E01 |
| T06 | C06/R04 | Formato de tabla se conserva | Etiquetas/comillas codificadas, IDs no rompen handler | E02 (funciones JS) |
| T07 | C09/R05 | Stock inicial 10 | Salidas simultáneas de 7: una acepta, otra falla; final 3; UPDATE movimiento rechazado | E03 (BD real) |
| T08 | C10/R05 | Venta total 10; completar pago confirma una vez | Dos pagos de 7: solo uno acepta; stock insuficiente revierte pago | E03 |
| T09 | C11/R10 | pg_dump/restauración con mismas cantidades/totales/stock | UPDATE movimiento restaurado falla | E03 |
| T10 | C18/R07 | Build auth y UID 65532 | Ejecutar sin red, read-only y sin capabilities | E06 (solo importación, no stack completo) |
| T11 | C22,C23/R08 | Analizadores producen reporte | Avisos no equivalen a explotación confirmada | E08/E09 |
| T12 | C24/R09 | Revisar etapas y permisos de CI | Falta configuración: exit 1 en archivo | E10 (sin run externo) |
| T13 | C12/R02 | Pantalla local vacía sin prefill | Inspección de ausencia de credenciales por defecto en inputs | E04 |

Ejecución local reproducible: crear .venv e instalar requirements-dev.txt, src/requirements.txt y requirements-security.txt; ejecutar `python scripts/collect_security_evidence.py`. Sin --database los cinco casos SQL se omiten explícitamente. El colector no crea infraestructura ni despliega.

Para SQL, crear exclusivamente el contenedor aislado descrito en respaldos-recuperacion.md con el comando registrado en evidencias/README.md; comprobar pg_isready y ejecutar `python scripts/collect_security_evidence.py --database`. La fixture verifica nombre/etiqueta/red/mounts antes de cualquier DROP SCHEMA. Nunca cambiar el guard para apuntar a una base real.

Criterios de aceptación: todos los casos ejecutados pasan; omisiones se justifican; no hay secretos en artefactos; cada control mantiene su alcance y residual. Autenticación y contrato cambiados solo con autorización; despliegue/push/PR y cambios de BD/infraestructura real requieren aprobación adicional. Ampliación pendiente: Redis real con API, todos los pares ruta/rol, XSS DOM, carreras edición/anulación, UI completa y aceptación de clínica, imagen web y escaneo CVE de imágenes, CI/cloud reales, recuperación de servicio completa y RTO/RPO acordados.

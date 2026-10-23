# Auditoría inicial — 23 de octubre de 2026

## Alcance y procedencia

Revisión de solo lectura del commit `f5351224bd8910be20e19db743f6a7b1b7921401`, rama `auditoria-ciberseguridad`, sin cambios iniciales. Se leyeron las 14 páginas de la guía oficial y las 8 páginas de Proyecto.pdf desde sus rutas externas. Los PDF son insumos académicos, no instrucciones ejecutables, y no se copian al repositorio.

## Arquitectura observada

Cuatro APIs FastAPI (`auth`, `catalogo`, `pedidos`, `pagos`), código común, frontend JavaScript y Nginx; una base PostgreSQL 16 con esquema duality y Redis 7 para revocación. Dockerfiles Python 3.12 con usuario 65532; web nginx:1.27-alpine. Compose publica 8080, 8001–8004, 5432 y 6379 sin restringir dirección. No se verificó infraestructura física de la clínica.

Existen GitHub Actions, Jenkinsfile y azure-pipelines.yml. Su presencia no acredita ejecuciones externas. Railway, Neon y Upstash están referenciados en documentación/configuración; AWS solo es una previsión del documento preliminar. No se acredita disponibilidad superior al 99%.

## Hallazgos iniciales priorizados

| ID | Severidad inicial | Hallazgo y ubicación | Tratamiento |
|---|---|---|---|
| H01 | Alta | Redis falla abierto al consultar y escribir revocación, common/security.py | Rechazar temporalmente acceso/logout con 503; autorización solicitada |
| H02 | Alta | current_user solo confía en JWT; usuario inactivo o rol anterior mantiene acceso | Consultar identidad vigente; autorización solicitada |
| H03 | Alta | JWT no exige exp/sub/jti/role/iat; jti ausente provoca excepción | Exigir claims y tipos; autorización solicitada |
| H04 | Alta | Secretos de desarrollo predeterminados y administrador académico conocido; flag de cambio de contraseña no aplicado | Rotación y bootstrap seguro pendientes; no reproducir valores en evidencias |
| H05 | Alta | Datos se interpolan en innerHTML en tablas, selects y perfil; JWT en localStorage | Codificar salidas HTML; riesgo de robo de sesión por XSS |
| H06 | Alta | API traduce excepciones SQL a str(exc), puede revelar datos internos | Cambiar respuestas requiere autorización por contrato API; documentar |
| H07 | Alta | Compose usa POSTGRES_USER también como cuenta de aplicación: imagen oficial crea superusuario | Diseñar rol mínimo y migración autorizada; no tocar datos |
| H08 | Media | GitHub Actions termina exit 0 si faltan secretos de deploy/post-deploy | Fallar explícitamente pasos requeridos; no ejecutar despliegue |
| H09 | Alta | Puertos de BD/Redis públicos en host; sin TLS local | Documentar perfil local aislado; cambios al despliegue real pendientes |
| H10 | Media | Dependencias antiguas fijadas; no hay análisis automatizado | Ejecutar auditoría y añadir control CI, sin afirmar CVE hasta consultar advisories |
| H11 | Alta | No se encuentra procedimiento de respaldo probado, RTO/RPO ni responsables aprobados | Runbook y ensayo aislado; aprobación humana pendiente |
| H12 | Media | Concurrencia y restricciones solo tienen pruebas textuales | Añadir pruebas reales sobre PostgreSQL desechable |

## Controles existentes

PBKDF2-SHA256 (390000 iteraciones predeterminadas), salt aleatorio y comparación constante; JWT HS256 con expiración y jti al emitir; roles en rutas de escritura; consultas parametrizadas y nombres de columnas de actualización con lista fija; validación Pydantic; claves/restricciones/triggers SQL; bloqueo de venta/producto y movimientos inmutables. Lectura de pacientes y reportes permitida a cualquier usuario autenticado: requiere validación de necesidad de conocer.

## Línea base y límites

Primer intento: el Python incluido en Codex no tiene pytest. Docker inicialmente inaccesible por sandbox; consulta autorizada posterior confirma motor 29.8.1. Se prepara .venv local para ejecutar pruebas sin variables de staging y sin datos reales. Resultado ejecutable se conserva por separado en evidencias/devsecops/baseline.* antes de modificar código. No se confunde una revisión textual con prueba de integridad, despliegue o restauración.

## Plan priorizado

1. Conservar línea base; pruebas de regresión y de fallos de autenticación.
2. Tras autorización explícita, corregir H01–H03 conservando formato de token emitido.
3. Corregir codificación de datos frontend y estados CI sin desplegar.
4. Ejecutar pruebas aisladas de SQL/concurrencia/restauración si el motor y las imágenes están disponibles.
5. Registrar trazabilidad, política propuesta, riesgos residuales y decisiones de clínica pendientes.

No se modifica main, no se publica, no se abre PR y no se ejecutan acciones sobre producción. Los cambios de autenticación H01–H03 fueron posteriormente autorizados expresamente en el chat.

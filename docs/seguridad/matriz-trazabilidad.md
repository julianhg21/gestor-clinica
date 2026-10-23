# Matriz de trazabilidad

Se conservan los RS-01–RS-10 de Proyecto.pdf página 4; no se cambia su significado. C01–C40 detallan requisitos oficiales y criterios de cierre en matriz-cumplimiento.md y controles.json.

| Requisito preliminar | Controles vinculados | Documento académico afectado |
|---|---|---|
| RS-01 | C02,C03,C04,C05,C13 | Requisitos trazables / controles / pruebas (p. 4–5) |
| RS-02 | C04,C13 | Requisitos trazables / controles / pruebas (p. 4–5) |
| RS-03 | C01 | Requisitos trazables / controles / pruebas (p. 4–5) |
| RS-04 | C07,C08,C15 | Requisitos trazables / controles / pruebas (p. 4–5) |
| RS-05 | C09,C14 | Requisitos trazables / controles / pruebas (p. 4–5) |
| RS-06 | C10 | Requisitos trazables / controles / pruebas (p. 4–5) |
| RS-07 | C12,C21 | Requisitos trazables / controles / pruebas (p. 4–5) |
| RS-08 | C11,C27 | Requisitos trazables / controles / pruebas (p. 4–5) |
| RS-09 | C24 | Requisitos trazables / controles / pruebas (p. 4–5) |
| RS-10 | C29,C40 | Requisitos trazables / controles / pruebas (p. 4–5) |

| Activo/riesgo | Requisito/control | Implementación | Prueba y evidencia | Decisión residual |
|---|---|---|---|---|
| A03/R02 | C01 | `src/common/security.py` | test_password_salts_and_malformed_hashes; test_password_roundtrip; E01 | Implementado y validado: Validación local de funciones; rotación y política de longitud requieren revisión adicional |
| A03/R01 | C02 | `src/common/security.py` | test_invalid_tokens; test_required_claims; test_tampered_signature; E01 | Implementado y validado: No se prueba rotación de claves ni MFA; mantener secreto fuerte |
| A03/R01 | C03 | `src/common/security.py` | test_logout_revokes_token; test_redis_failure_is_not_success; E01 | Parcialmente implementado: Probar API con Redis real, reinicio, persistencia y alertas; denegación temporal reduce disponibilidad |
| A03/R03 | C04 | `src/common/security.py` | test_user_removed_disabled_or_role_changed; test_database_unavailable; E01 | Parcialmente implementado: Identidad simulada en estas pruebas; integrar con BD real y medir latencia del nuevo SELECT |
| A04/R03 | C05 | `src/*/main.py; matriz-accesos.md` | test_missing_token_all_services; test_role_denied; E01 | Parcialmente implementado: Ampliar pruebas positivas/negativas a cada ruta y aprobar permisos de consulta con clínica |
| A05/R04 | C06 | `src/web/app.js; src/web/edit-modal.js` | node tests/security_frontend.cjs; E02 | Parcialmente implementado: Prueba de funciones y revisión de sinks; falta flujo XSS completo en navegador; JWT sigue en localStorage |
| A04/R05 | C07 | `src/*/main.py` | test_invalid_payment_input; test_login; E01 | Parcialmente implementado: Añadir límites a listas/textos sin límite requiere autorización de contrato API |
| A04/R06 | C08 | `src/auth/main.py; src/common/db.py` | test_parameterized_login_injection; E01 | Implementado y validado: Prueba limitada al login; actualizaciones dinámicas usan nombres de una lista fija, revisar cada cambio |
| A02/R05 | C09 | `docker/postgres/init/001_schema.sql` | test_database_constraints_and_immutable_inventory; test_concurrent_inventory_no_negative_stock; E03 | Implementado y validado: Ensayo sintético de dos clientes, no prueba de carga sostenida ni de privilegios DBA |
| A02/R05 | C10 | `docker/postgres/init/002_app_extensions.sql` | test_concurrent_payments_and_rollback; test_payment_failed_confirmation_rolls_back; E03 | Implementado y validado: Faltan combinaciones de editar/anular/descontar y todos los flujos de servicios realizados |
| A02/R10 | C11 | `tests/test_audit_database.py` | test_backup_restore_in_separate_database; E03 | Implementado y validado: Dump en memoria dentro del laboratorio; no acredita backup operativo cifrado, offsite ni recuperación completa del servicio |
| A05/R02 | C12 | `src/web/index.html` | Inspección HTML y captura del formulario vacío; E04 | Implementado y validado: La cuenta académica sigue en SQL/README y debe rotarse antes de uso real |
| A01/R03 | C13 | `matriz-accesos.md; politica-seguridad.md` | Entrevista y revisión firmada de matriz; Sin evidencia operativa | Propuesto: Faltan nombres, suplencias, lugar de acceso, aprobación y periodicidad aceptada |
| A02/R06 | C14 | `SQL usuario/movimientos/pagos; gestion-incidentes.md` | Revisión de columnas de trazabilidad; ensayo de inventario; E03 | Parcialmente implementado: No hay auditoría central completa de login/cambios de privilegio ni retención aprobada |
| A04/R06 | C15 | `src/common/security.py; src/catalogo/main.py; src/pedidos/main.py; src/pagos/main.py` | 503 genérico en test_database_unavailable; E01 | Parcialmente implementado: Varios 409 aún muestran str(exc); sanear cambia contrato API y requiere autorización |
| A02/R03 | C16 | `docker-compose.yml (configuración actual); plan-pruebas.md` | Comprobar privilegios efectivos y rechazo de DDL; Sin evidencia operativa | Propuesto: Cuenta POSTGRES_USER compartida; diseñar migración/rol sin tocar persistencia existente |
| A06/R07 | C17 | `docker-compose.yml; diagramas/despliegue.puml` | docker compose config --quiet e inspección; E05 | Parcialmente implementado: Compose publica APIs/BD/Redis en todas las interfaces; restringir exposición requiere validar entorno |
| A06/R07 | C18 | `docker/*/Dockerfile` | Build auth y ejecución UID 65532 con red none/read-only/cap-drop; E06 | Parcialmente implementado: Solo imagen auth ejecutada; flags endurecidos son ensayo, no configuración de Compose; web sigue con privilegios iniciales de nginx |
| A06/R08 | C19 | `politica-seguridad.md` | Inventario de host, parches y escaneo de imágenes; Sin evidencia operativa | Propuesto: Faltan acceso e inventario de dispositivos de clínica; no se instala EDR/IDS sin contexto |
| A01/R07 | C20 | `proveedores-cloud.md` | Validar TLS público, certificados y cifrado de backup/BD; Sin evidencia operativa | Propuesto: Solo HTTP local observado; no se acredita HTTPS público ni cifrado en reposo |
| A03/R02 | C21 | `.gitignore; .dockerignore; common/config.py` | Inspección de salidas y escaneo local de patrones; E07 | Parcialmente implementado: Persisten fallbacks conocidos y bootstrap; no equivale a inspección del historial ni rotación externa |
| A08/R08 | C22 | `requirements-security.txt; .github/workflows/security.yml` | pip-audit; análisis de duplicados/aplicabilidad; E08 | Parcialmente implementado: Avisos abiertos; workflow no ejecutado en GitHub; actualizar FastAPI/PyJWT requiere validación de compatibilidad |
| A04/R06 | C23 | `.github/workflows/security.yml; requisitos actuales` | bandit -r src -f json; E09 | Parcialmente implementado: B105 literal bearer no es credencial; B608 nombres de lista fija, revisar parámetros; no prueba ausencia de vulnerabilidades |
| A07/R09 | C24 | `.github/workflows/ci.yml; Jenkinsfile` | Revisión YAML: exit 1 ante secretos ausentes; E10/E11 | Parcialmente implementado: Corrida histórica #55 éxito con deploy/post-deploy omitidos según logs; falta ejecutar cambios nuevos en GitHub/Jenkins |
| A07/R09 | C25 | `gestion-cambios.md` | Revisar branch rules, colaboradores y MFA; E11 | Propuesto: GitHub GET confirma main sin protección y rulesets vacíos; habilitar requiere autorización externa; MFA/colaboradores no revisados |
| A07/R09 | C26 | `scripts/collect_security_evidence.py; tests/test_audit_database.py` | Verificar etiqueta, nombre, red none, ausencia de bind mounts; E03 | Parcialmente implementado: Aislamiento local validado por fixture; separación cloud/staging por verificar |
| A02/R10 | C27 | `respaldos-recuperacion.md` | Aprobación de BIA y simulacro de recuperación de servicio; Sin evidencia operativa | Propuesto: Ensayo C11 no sustituye decisiones ni copias periódicas; sin RTO/RPO inventados |
| A01/R11 | C28 | `gestion-incidentes.md` | Ejercicio de mesa y registro firmado; Sin evidencia operativa | Propuesto: Falta responsables/canal y simulacro con clínica |
| A07/R09 | C29 | `gestion-cambios.md; evidencias/ejecuciones.json` | Revisión de diff, hashes y resultados locales; E01 | Parcialmente implementado: Cambios sin commit y sin revisión independiente; no simular aprobación |
| A09/R12 | C30 | `proveedores-cloud.md` | Confirmar contratos/cuentas y propietario por proveedor; Sin evidencia operativa | Propuesto: Railway/Neon/Upstash referenciados; AWS previsto; ninguno acreditado operativo en esta auditoría |
| A09/R12 | C31 | `proveedores-cloud.md` | Inspección autorizada de recursos y permisos efectivos; Sin evidencia operativa | Propuesto: Falta acceso a consolas y confirmación de servicios usados |
| A01/R11 | C32 | `politica-seguridad.md` | Revisión y aprobación formal de documento; Sin evidencia operativa | Propuesto: Borrador NIST CSF 2.0, sin adopción aprobada ni certificación |
| A01/R11 | C33 | `politica-seguridad.md` | Acta de designaciones y aceptación de riesgos; Sin evidencia operativa | Propuesto: Roles propuestos; no nombres ni aprobaciones ficticias |
| A01/R11 | C34 | `inventario-activos.md` | Contraste técnico con repositorio y entrevista; E10 | Parcialmente implementado: Inventario lógico del código; falta levantamiento físico y dueños de clínica |
| A01/R11 | C35 | `politica-seguridad.md` | Aprobar tabla de tratamiento y plazos; Sin evidencia operativa | Propuesto: No inferir obligaciones legales ni plazos de conservación médica |
| A01/R11 | C36 | `matriz-riesgos.md` | Revisión técnica y validación por propietario; E10 | Parcialmente implementado: Puntuaciones preliminares del equipo, no decisiones aceptadas por la clínica |
| A04/R11 | C37 | `diagramas/*.puml; docs/ARCHITECTURE.md` | Contraste con rutas, Compose y common.security; E10 | Parcialmente implementado: Fuentes UML sin render PlantUML ni validación docente; no sustituyen implementación |
| A06/R07 | C38 | `politica-seguridad.md; proveedores-cloud.md` | Entrevista y revisión de topología/reglas reales; Sin evidencia operativa | Propuesto: Sin inventario real no se inventan VLAN, VPN, IDS/IPS ni firewall instalado |
| A01/R11 | C39 | `politica-seguridad.md` | Revisión periódica y registro de excepción con vencimiento; Sin evidencia operativa | Propuesto: Falta aceptación formal y evaluación legal específica |
| A07/R09 | C40 | `evidencias/README.md; evidencias/ejecuciones.json` | Hashes y revisión de artefactos; E07 | Implementado y validado: Commit base más hashes de fuentes modificadas; evidencia local no equivale a validación en clínica |

Actualización de evidencia remota: C24 y C25 se contrastan con E11, github-historico.json; main sin protección y rulesets vacíos. C24 solo tiene corrida histórica del código anterior; cambios nuevos sin ejecutar en GitHub.

# Informe final técnico — Gestor Clínica Duality

Auditoría local del 23/10/2026 en auditoria-ciberseguridad. Base `f5351224bd8910be20e19db743f6a7b1b7921401`, cambios sin commit. No se modificó main, no hubo push/PR ni despliegue. Los PDF de entrada permanecen externos al repositorio. No se declara cumplimiento total: 8 controles validados localmente, 18 parcialmente implementados y 14 propuestos de 40.

## Diagnóstico y correcciones

Hallazgos completos H01–H12: auditoria-inicial.md. Se corrigió fallo abierto de Redis, ausencia de claims obligatorios y permanencia de sesiones tras desactivar/cambiar rol, con autorización explícita del usuario. Se codificaron salidas de API en frontend para reducir XSS, se retiraron credenciales precargadas del formulario, se hizo explícito el fallo de etapas de CI sin configuración y se añadió auditoría separada de dependencias/código. Se preservó el modelo relacional y no se tocó persistencia de usuario.

Se añadieron pruebas locales y de SQL aislado, colector reproducible, índices de evidencia, hashes y UML con controles. Se construyó auth y se verificó UID no root. La aplicación ya tenía PBKDF2, roles, SQL parametrizado, restricciones, triggers y bloqueo transaccional; se probaron técnicamente escenarios de stock/pagos y restauración.

## Resultados

Línea base: 33 aprobadas. Final: **69 aprobadas, 6 omitidas, 0 fallos**; JavaScript PASS adicional. Las 5 SQL reales están incluidas en el total. Se verificó restauración sintética a base distinta y comparación de datos/control de inmutabilidad. Resultados y límites en resultados-pruebas.md. E01–E11 se resuelven en evidencias/README.md, con fecha/entorno/commit/procedimiento/esperado/real/limitaciones y hashes.

## Riesgos y pendientes

Persisten avisos conocidos (50 registros/31 IDs distintos/4 paquetes, sin concluir explotabilidad), credenciales de bootstrap/fallbacks, superusuario compartido en Compose, puertos abiertos a interfaces del host, HTTP local y errores con texto SQL. El cambio de autenticación depende de Redis/BD y añade SELECT por petición. JWT sigue en localStorage. Falta integración Redis real, cobertura completa de roles/DOM, UAT, escaneo de imágenes, monitorización y revisión remota de pipelines/ramas/cloud.

La clínica debe confirmar contexto real, inventario físico, propietarios, política, permisos, clasificación/retención, proveedores, responsables de incidentes y objetivos RTO/RPO. Los procedimientos son borradores; ensayo de restauración no equivale a backup operativo. Prioridad: resolver defaults/privilegios/red antes de datos reales; planificar actualización compatible de dependencias; aprobar errores API seguros; probar stack y continuidad; formalizar gobierno y protección de repositorio.

## Entregables y revisión

matriz-cumplimiento.md y controles.json: 40 controles con activo/riesgo/control/ubicación/prueba/evidencia/residual/pendiente. Inventario, matriz-riesgos, matriz-accesos (49 rutas) y matriz-trazabilidad conservan contexto verificable. politica-seguridad, incidentes, cambios, respaldos y proveedores-cloud separan propuesta de operación real. Fuentes UML: diagramas/*.puml, sin render ni aprobación docente.

Archivos modificados exactos: evidencias/archivos-cambiados.txt (cierre local). Bitácora de motivo/actor/impacto/prueba/resultado: gestion-cambios.md. El informe académico con secciones de Proyecto.pdf a corregir y referencias exactas es INFORME-PARA-DOCUMENTO-UNIVERSITARIO.md. Ningún resultado externo histórico se usa como evidencia del código local nuevo.

## Verificación remota posterior de solo lectura (E11)

El conector GitHub confirmó `main.protected=false`, protección deshabilitada y lista de rulesets vacía. No se cambió configuración. La corrida histórica [#55](https://github.com/julianhg21/gestor-clinica/actions/runs/38074840230), del commit base y fecha 10/10/2026, figura exitosa. Sus logs auténticos muestran 33 passed, 1 skipped y 5 deselected, ausencia de RAILWAY_STAGING_DEPLOY_HOOKS y omisión de pruebas post-deploy por STAGING_BASE_URL ausente. No demuestra despliegue efectivo ni valida el código nuevo local. Extractos sanitizados y pasos: `evidencias/devsecops/github-historico.json` (sin correos, firmas, tokens ni logs completos). C24 permanece parcial; C25 permanece propuesto porque el control de protección no está implementado. MFA y colaboradores no se verificaron.

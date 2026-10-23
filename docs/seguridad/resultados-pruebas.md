# Resultados comprobados

Fecha: 2026-10-23T12:30:01.793788-06:00. Commit base `f5351224bd8910be20e19db743f6a7b1b7921401` con modificaciones locales, hashes en evidencias/ejecuciones.json.

| Ejecución | Resultado | Evidencia | Alcance |
|---|---|---|---|
| Línea base antes de modificar código | 33 aprobadas, 1 omitida, 5 no seleccionadas | evidencias/devsecops/baseline.xml y baseline.txt | Pruebas existentes, sin staging |
| Validación final completa | 69 aprobadas, 6 omitidas, 0 fallos, 1 warning | evidencias/devsecops/final.xml, final.html, final.txt, pytest-local.png | Suite existente + seguridad + PostgreSQL real |
| SQL aislado (corrida suplementaria) | 5 aprobadas | evidencias/bases-datos/postgres.xml, postgres.html, postgres.txt y postgres.png | Constraints, concurrencia, rollback y restauración |
| Funciones JavaScript con entradas XSS | PASS | evidencias/autenticacion/frontend.txt | Codificación y handlers en Node, sin DOM real |
| Construcción e importación de auth | Build correcto, UID 65532, importación OK | evidencias/contenedores/build-auth.txt y runtime-auth.txt | Imagen local sin red/read-only/cap-drop |
| Compose | Exit 0 | evidencias/infraestructura/compose.txt | Sintaxis, sin desplegar |
| Dependencias | Exit 1; 50 registros, 4 paquetes, 31 IDs distintos | evidencias/vulnerabilidades/dependencias-runtime-dev.json | Runtime + desarrollo + herramientas instalados |
| Bandit | 2 alertas revisadas (baja/media) | evidencias/vulnerabilidades/bandit.json y analisis.md | No prueba ausencia de fallos |

Las 5 pruebas SQL están incluidas en las 69 finales: no sumar 5 otra vez. La prueba JavaScript es adicional y no aumenta el conteo pytest. Las 6 omisiones son 3 integración, 1 rendimiento y 1 Selenium por STAGING_BASE_URL ausente, y 1 smoke por SMOKE_BASE_URL ausente. No se usó una URL pública. El warning final es de deprecación de anyio/Starlette TestClient; no es fallo de control.

Las pruebas con dobles verifican decisiones de autenticación, no disponibilidad real de Redis ni integración completa entre API y BD. SQL usa datos sintéticos y dos clientes simultáneos; no mide carga sostenida. Captura login-local.png demuestra formulario vacío en servidor estático, no autenticación de producción. No se reejecutaron GitHub Actions, Jenkins ni Azure DevOps; sus cambios tienen validación estática local.

La suite existente conserva contratos de pacientes, productos, servicios, ventas, pagos, usuarios y modal de edición. Esto reduce riesgo de regresión, pero no acredita aceptación de todos los flujos principales con usuarios reales. Falta UAT, stack completo, errores SQL saneados, Redis real, protección de ramas/cloud y recuperación del servicio con RTO/RPO aprobados.

## Verificación remota posterior de solo lectura (E11)

El conector GitHub confirmó `main.protected=false`, protección deshabilitada y lista de rulesets vacía. No se cambió configuración. La corrida histórica [#55](https://github.com/julianhg21/gestor-clinica/actions/runs/38074840230), del commit base y fecha 10/10/2026, figura exitosa. Sus logs auténticos muestran 33 passed, 1 skipped y 5 deselected, ausencia de RAILWAY_STAGING_DEPLOY_HOOKS y omisión de pruebas post-deploy por STAGING_BASE_URL ausente. No demuestra despliegue efectivo ni valida el código nuevo local. Extractos sanitizados y pasos: `evidencias/devsecops/github-historico.json` (sin correos, firmas, tokens ni logs completos). C24 permanece parcial; C25 permanece propuesto porque el control de protección no está implementado. MFA y colaboradores no se verificaron.

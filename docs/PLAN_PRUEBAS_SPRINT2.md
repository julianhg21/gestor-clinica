# Plan de Pruebas — Sprint 2

**Proyecto:** Gestor Clínica Duality  
**Sprint:** 2 — Integración Continua y Entrega Continua  
**Fecha de referencia:** 26–29 de septiembre de 2026  
**Stack:** Python 3.12, FastAPI, PostgreSQL 16, Redis 7, Nginx, HTML/CSS/JavaScript, Docker.

## 1. Objetivos

Validar que los componentes principales del sistema funcionen de manera consistente después de cada cambio, detectar regresiones antes del despliegue y dejar evidencia repetible mediante pruebas automatizadas y manuales.

Objetivos específicos:

- comprobar autenticación, autorización y controles básicos de seguridad;
- verificar operaciones CRUD y anulaciones auditables;
- validar contratos de base de datos, Docker y microservicios;
- verificar integración entre frontend, reverse proxy y APIs;
- revisar experiencia de usuario en navegador;
- medir un umbral básico de tiempo de respuesta en staging;
- generar un reporte HTML de pytest como evidencia del Sprint 2.

## 2. Propósito

El plan sirve como criterio de aceptación técnico del pipeline CI/CD. Una modificación no debe llegar a staging si falla la fase de build o las pruebas automatizadas obligatorias.

## 3. Alcance

Incluye:

- Auth: login, JWT, roles y usuarios.
- Catálogo: pacientes, productos, servicios, inventario y servicios realizados.
- Pedidos: creación, edición y anulación de ventas.
- Pagos: registro, edición y anulación controlada.
- Interfaz web responsive.
- Contratos Docker/PostgreSQL.
- Pipeline Jenkins y GitHub Actions.
- Staging desplegado mediante Railway Deploy Hooks.

Fuera de alcance del Sprint 2: diagnóstico médico automático, facturación fiscal, integraciones hospitalarias, pruebas de carga masiva y pruebas de penetración especializadas.

## 4. Tipos de prueba

| Tipo | Propósito | Herramienta / enfoque |
|---|---|---|
| Unitarias | Validar funciones aisladas y reglas simples | pytest |
| Contrato | Verificar rutas, scripts SQL, Docker y pipeline | pytest |
| Integración | Comprobar comunicación web/API en staging | pytest + httpx |
| Sistema | Validar flujo completo desde navegador | Selenium |
| Aceptación | Confirmar requisitos funcionales con el usuario | Manual guiada |
| Seguridad | Comprobar autenticación, roles y restricciones | pytest + revisión manual |
| Rendimiento | Medir respuesta de endpoint de salud | pytest + httpx |
| UX | Revisar claridad visual, responsive y mensajes | Manual |

## 5. Estrategia

La estrategia es híbrida:

1. **Automatizada con pytest:** se ejecutan pruebas unitarias, de seguridad y de contrato en cada push o pull request.
2. **Automatizada con Selenium:** se valida la pantalla de acceso en un navegador Chrome contra staging cuando se define `STAGING_BASE_URL`.
3. **Integración:** se consulta la aplicación desplegada con httpx.
4. **Rendimiento básico:** cinco solicitudes al endpoint de salud y promedio menor a 2 segundos.
5. **Manual para UX:** revisión de escritorio y móvil, formularios, mensajes de confirmación, edición y anulaciones.
6. **Evidencia:** pytest genera `reports/pytest-report.html` y `reports/junit.xml`.

## 6. Criterios de entrada y salida

**Entrada:** código compilable, dependencias instalables, Docker Compose válido y variables del entorno de staging configuradas.

**Salida:** build exitoso, pruebas obligatorias sin fallos bloqueantes, reporte HTML generado y staging accesible. Las pruebas manuales deben quedar documentadas con PASS/FAIL y captura cuando corresponda.

## 7. Casos de prueba

> La columna **Resultado obtenido** no se prellena con resultados inventados. Después de ejecutar el pipeline o la prueba manual debe registrarse PASS/FAIL y anexarse evidencia.

| ID | Tipo | Caso | Precondiciones | Pasos | Resultado esperado | Resultado obtenido |
|---|---|---|---|---|---|---|
| CP-01 | Sistema | Login válido | Usuario activo | Abrir web, ingresar credenciales válidas, enviar | Acceso al dashboard y JWT creado | Por ejecutar |
| CP-02 | Seguridad | Login inválido | Usuario existente | Ingresar contraseña incorrecta | HTTP 401 y mensaje de credenciales inválidas | Por ejecutar |
| CP-03 | Seguridad | Recurso sin token | Ninguna | GET a `/api/catalogo/patients` sin Authorization | HTTP 401 | Por ejecutar |
| CP-04 | Funcional | Crear paciente | Sesión Admin/Oper | Abrir Pacientes, completar formulario, guardar | Paciente aparece en listado | Por ejecutar |
| CP-05 | Funcional | Editar paciente | Paciente activo | Editar nombres/teléfono/correo | Datos actualizados | Por ejecutar |
| CP-06 | Funcional | Eliminar lógicamente paciente | Admin | Seleccionar Eliminar | Registro queda inactivo y desaparece del listado activo | Por ejecutar |
| CP-07 | Funcional | Crear producto | Admin/Oper | Completar SKU, nombre, precio, mínimo | Producto creado | Por ejecutar |
| CP-08 | Funcional | Editar producto | Producto activo | Cambiar nombre/precio/mínimo | Producto actualizado | Por ejecutar |
| CP-09 | Funcional | Desactivar producto | Admin | Seleccionar Eliminar | Producto queda inactivo sin borrar historial | Por ejecutar |
| CP-10 | Inventario | Registrar entrada | Producto activo | Inventario → ENTRADA → cantidad | Stock aumenta y queda movimiento auditable | Por ejecutar |
| CP-11 | Inventario | Evitar stock negativo | Stock insuficiente | Registrar SALIDA mayor al stock | Operación rechazada con error de negocio | Por ejecutar |
| CP-12 | Funcional | Crear servicio | Admin/Oper | Completar servicio y precio | Servicio aparece en catálogo | Por ejecutar |
| CP-13 | Funcional | Editar servicio | Servicio activo | Modificar precio/duración | Servicio actualizado | Por ejecutar |
| CP-14 | Clínico | Editar servicio realizado | Registro no finalizado | Cambiar precio/observaciones | Actualización permitida | Por ejecutar |
| CP-15 | Clínico | Anular servicio realizado | Registro no finalizado | Seleccionar Anular | Estado ANULADO; no se elimina evidencia | Por ejecutar |
| CP-16 | Ventas | Crear venta pendiente | Paciente/producto disponibles | Crear venta con cantidad válida | Venta PENDIENTE creada | Por ejecutar |
| CP-17 | Ventas | Editar venta pendiente | Venta PENDIENTE | Cambiar descuento/observaciones | Venta actualizada | Por ejecutar |
| CP-18 | Ventas | Anular venta pendiente | Admin, venta pendiente | Seleccionar Anular | Venta pasa a ANULADA y pagos registrados se anulan | Por ejecutar |
| CP-19 | Pagos | Registrar pago | Venta pendiente | Registrar monto válido | Pago registrado y saldo actualizado | Por ejecutar |
| CP-20 | Pagos | Editar pago pendiente | Pago REGISTRADO de venta PENDIENTE | Cambiar monto/referencia | Pago actualizado sin exceder total | Por ejecutar |
| CP-21 | Pagos | Impedir edición de pago cerrado | Venta no pendiente | Intentar editar pago | HTTP 409 | Por ejecutar |
| CP-22 | Usuarios | Desactivar usuario | Admin y usuario distinto al actual | Seleccionar Desactivar | Usuario queda inactivo | Por ejecutar |
| CP-23 | Seguridad | Impedir auto-desactivación | Admin autenticado | Intentar desactivar su propio usuario | HTTP 409 | Por ejecutar |
| CP-24 | Sistema | Dashboard | Sesión válida | Abrir Resumen | Indicadores cargan sin error | Por ejecutar |
| CP-25 | UX | Responsive | Navegador desktop/móvil | Revisar login, menú, tablas y formularios | Contenido legible y usable | Por ejecutar |
| CP-26 | Rendimiento | Health < 2 s promedio | Staging disponible | Ejecutar 5 GET a `/api/auth/health` | Promedio menor a 2 s | Por ejecutar |

## 8. Automatización disponible

Archivos principales:

- `tests/test_security.py`
- `tests/test_sprint2_contract.py`
- `tests/test_integration_sprint2.py`
- `tests/test_performance_sprint2.py`
- `tests/test_selenium_sprint2.py`

Ejecución local obligatoria:

```bash
pip install -r requirements-dev.txt
mkdir -p reports
pytest -m "not integration and not selenium and not performance" \
  --html=reports/pytest-report.html --self-contained-html \
  --junitxml=reports/junit.xml
```

Pruebas contra staging:

```bash
export STAGING_BASE_URL="https://TU-STAGING.example"
pytest -m "integration or performance" -q
pytest -m selenium -q
```

## 9. Ejecución y reporte

El pipeline genera un artefacto denominado **sprint2-test-report** con:

- `pytest-report.html`
- `junit.xml`

Para la entrega deben conservarse capturas de:

1. ejecución exitosa;
2. una ejecución fallida provocada de forma controlada y luego corregida;
3. reporte HTML abierto;
4. prueba Selenium / staging;
5. historial del pipeline mostrando ambas ejecuciones.

## 10. Parámetros del sistema

| Parámetro | Valor de referencia |
|---|---|
| Aplicación | Gestor Clínica Duality — Sprint 2 |
| Python | 3.12 |
| FastAPI | 0.115.6 |
| PostgreSQL | 16 |
| Redis | 7 |
| Nginx | 1.27 Alpine |
| Contenedores | Docker + Docker Compose |
| CI/CD | Jenkinsfile + GitHub Actions |
| Navegador objetivo | Google Chrome actual |
| SO de CI | Ubuntu Latest / agente Jenkins Linux |
| Resolución UX desktop | 1366×768 o superior |
| Resolución UX móvil | 390×844 de referencia |
| Hardware CI | Runner/agent con al menos 2 CPU y 4 GB RAM recomendados |

# Implementación DEVOPS 2 — Sprint 2

**Proyecto:** Gestor Clínica Duality  
**Tema:** Integración Continua y Entrega Continua (CI/CD)  
**Periodo:** 26–29 de septiembre de 2026

## 1. Objetivo del Sprint 2

Implementar un flujo CI/CD reproducible que compile, pruebe y prepare el despliegue a staging del Gestor Clínica Duality, acompañado de un plan de pruebas formal y mejoras funcionales/visuales de la aplicación.

## 2. Cambios implementados

### CI/CD

Se agregó un `Jenkinsfile` con las etapas solicitadas:

1. **Checkout**
2. **Build**
3. **Test**
4. **Deploy staging**

La fase Build compila Python, valida Docker Compose y construye los contenedores. La fase Test instala dependencias y genera reporte HTML/JUnit. Deploy staging usa uno o más Railway Deploy Hooks proporcionados por una variable secreta `STAGING_DEPLOY_HOOKS`.

También se amplió `.github/workflows/ci.yml` para disponer de evidencia automática dentro del repositorio: build, pruebas, artefacto HTML y etapa de staging.

### Plan de pruebas

El plan completo está en [PLAN_PRUEBAS_SPRINT2.md](PLAN_PRUEBAS_SPRINT2.md). Incluye objetivos, propósito, alcance, tipos de prueba, estrategia, parámetros del sistema y más de 15 casos de prueba.

### Automatización

- pytest para unitarias, seguridad y contratos;
- httpx para integración y rendimiento;
- Selenium para sistema/interfaz;
- pytest-html para el reporte de ejecución.

### Mejoras de la aplicación

Se incorporaron acciones que faltaban en la interfaz:

- editar y desactivar pacientes;
- editar y desactivar productos;
- editar y desactivar servicios;
- editar y anular servicios realizados que aún no estén cerrados;
- editar y anular ventas pendientes;
- editar y anular pagos mientras la venta permanezca pendiente;
- editar y desactivar usuarios;
- protección para evitar que un administrador se desactive a sí mismo.

La eliminación es **lógica/auditable** cuando el dominio lo requiere. Los movimientos de inventario permanecen inmutables; una corrección se realiza mediante `AJUSTE_POSITIVO` o `AJUSTE_NEGATIVO` para no perder trazabilidad.

### Rediseño visual

La interfaz se actualizó con:

- pantalla de login renovada;
- navegación lateral más clara;
- tarjetas, sombras y jerarquía visual;
- tablas con acciones;
- mensajes tipo toast;
- responsive para escritorio y móvil;
- avisos de auditoría en inventario, ventas y pagos.

## 3. Arquitectura del pipeline

```text
GitHub
  │
  ├── checkout
  │
  ├── build
  │    ├── compileall
  │    ├── docker compose config
  │    └── docker compose build
  │
  ├── test
  │    ├── pytest
  │    ├── seguridad/contratos
  │    └── pytest-report.html + junit.xml
  │
  └── deploy staging
       └── Railway Deploy Hooks
             │
             └── pruebas post-deploy
                  ├── integración
                  ├── rendimiento
                  └── Selenium (manual/ejecución dedicada)
```

## 4. Configuración Jenkins

El agente Jenkins debe disponer de:

- Git;
- Docker + Docker Compose;
- Python 3;
- acceso a Internet para instalar dependencias;
- `curl`.

Crear una credencial/variable secreta en Jenkins llamada:

```text
STAGING_DEPLOY_HOOKS
```

Puede contener uno o varios hooks separados por espacios, comas o saltos de línea. Se recomienda un hook por cada servicio que deba desplegarse en el ambiente **staging**.

No se deben guardar tokens, URLs privadas de deploy ni contraseñas en el repositorio.

## 5. Configuración GitHub Actions

Para activar el deploy de staging desde GitHub Actions configurar:

- Secret: `RAILWAY_STAGING_DEPLOY_HOOKS`
- Secret: `STAGING_BASE_URL`

Sin estos secretos la fase queda preparada y muestra una advertencia, pero no publica staging.

## 6. Reporte HTML

Comando de referencia:

```bash
pytest -m "not integration and not selenium and not performance" \
  --html=reports/pytest-report.html --self-contained-html \
  --junitxml=reports/junit.xml
```

En GitHub Actions, la carpeta `reports/` se publica como artefacto **sprint2-test-report**.

## 7. Evidencia requerida para el documento PDF

Capturas recomendadas y ubicación:

| Evidencia | Captura |
|---|---|
| E1 | Repositorio mostrando `Jenkinsfile` |
| E2 | Jenkins Pipeline con Checkout → Build → Test → Deploy staging |
| E3 | Ejecución exitosa en Jenkins |
| E4 | Ejecución fallida controlada en Jenkins |
| E5 | Consola del fallo mostrando la prueba/etapa que bloqueó |
| E6 | Corrección posterior y pipeline verde |
| E7 | GitHub Actions CI-CD Sprint 2 |
| E8 | Artefacto `sprint2-test-report` |
| E9 | `pytest-report.html` abierto |
| E10 | Railway ambiente staging / deploy exitoso |
| E11 | Aplicación renovada: pantalla de login |
| E12 | Aplicación: tabla con botones Editar/Eliminar o Anular |
| E13 | Aplicación: inventario con mensaje de trazabilidad |
| E14 | Selenium/Chrome ejecutando prueba |
| E15 | Sprint Backlog Sprint 2 |
| E16 | Burn down Sprint 2 |
| E17 | Daily Scrum documentado |
| E18 | Sprint Review y Retrospectiva |

## 8. Evidencia de ejecución exitosa y fallida

No se debe inventar una ejecución fallida. Para obtener evidencia válida:

1. crear temporalmente una rama de prueba;
2. introducir un cambio controlado que haga fallar una aserción;
3. ejecutar el pipeline y capturar el estado rojo;
4. corregir la aserción/código;
5. ejecutar nuevamente y capturar el estado verde.

La rama o commit defectuoso no debe permanecer en `main`.

## 9. Criterios de aceptación del Sprint 2

- `Jenkinsfile` presente y legible;
- etapas solicitadas presentes;
- Docker build válido;
- pytest ejecutado;
- reporte HTML generado;
- staging configurado;
- plan con 15+ casos;
- Selenium incluido;
- operaciones de edición/anulación disponibles;
- interfaz visual mejorada;
- evidencia Scrum preparada con datos reales.

## 10. Archivos de soporte

```text
Jenkinsfile
.github/workflows/ci.yml
scripts/deploy_staging.sh
docs/PLAN_PRUEBAS_SPRINT2.md
docs/DEVOPS_2_IMPLEMENTACION.md
docs/scrum/SPRINT_2.md
tests/test_sprint2_contract.py
tests/test_integration_sprint2.py
tests/test_performance_sprint2.py
tests/test_selenium_sprint2.py
```

# Gestor Clínica — Duality

Aplicación web para la gestión administrativa de **Duality - Clínica de Medicina Estética**, construida a partir de los requerimientos, UML, modelo relacional y arquitectura desarrollados en el Proyecto de Seminario.

La solución cubre los módulos de **usuarios y seguridad, pacientes, productos, servicios, inventario, servicios realizados, ventas/pedidos, pagos, reportes e indicadores**.

## Stack

- **Python 3.12 + FastAPI** para APIs REST.
- **PostgreSQL 16** como base de datos relacional.
- **Redis 7** para revocación de JWT y soporte de caché.
- **Nginx + HTML/CSS/JavaScript** para la interfaz administrativa.
- **Docker / Docker Compose** para ejecutar toda la solución de forma reproducible.

## Servicios

| Servicio | Responsabilidad | Puerto local |
|---|---|---:|
| `auth` | Login, JWT, roles, usuarios, pacientes, productos, servicios e inventario | 8001 |
| `pedidos` | Ventas, pedidos, reportes, pagos y métodos de pago | 8003 |
| `web` | Interfaz administrativa y reverse proxy | 8080 |
| `postgres` | PostgreSQL 16 | 5432 |
| `redis` | Redis 7 | 6379 |

Los despliegues usan tres servicios de aplicación (`auth`, `pedidos` y `web`). PostgreSQL y Redis permanecen como dependencias del entorno local de Docker Compose.

## Estructura del repositorio

```text
/src
  /api
  /auth
  /catalogo
  /pedidos
  /pagos
  /common
  /web
/docs
/docker
  /auth
  /catalogo
  /pedidos
  /pagos
  /web
  /postgres/init
/tests
.env.example
.gitignore
docker-compose.yml
```

## Inicio rápido

1. Crear el archivo local de variables de entorno:

   ```bash
   cp .env.example .env
   ```

2. Cambiar como mínimo `POSTGRES_PASSWORD` y `JWT_SECRET` en `.env`.
3. Levantar la plataforma completa:

   ```bash
   docker compose up --build -d
   ```

4. Abrir **http://localhost:8080**.

La cuenta administrativa inicial queda bloqueada para acceso interactivo hasta que se establezca una contraseña propia. Después, el primer ingreso exige registrar un autenticador TOTP; ningún JWT administrativo se emite solo con la contraseña. No se distribuyen credenciales de demostración en la interfaz.

## Base de datos

Los scripts SQL se ejecutan automáticamente al inicializar PostgreSQL:

- `docker/postgres/init/001_schema.sql`: esquema Duality, tablas, claves, restricciones, índices, funciones, triggers, procedimientos, vistas y catálogos base.
- `docker/postgres/init/002_app_extensions.sql`: autenticación, pagos, procedimientos de confirmación/pago, vistas del dashboard y usuario administrador inicial.
- `docker/postgres/init/003_fix_routine_search_path.sql`: corrección idempotente del `search_path` para bases ya creadas.
- `docker/postgres/init/004_mfa.sql`: estado de MFA para cuentas administrativas. En Neon existente se aplica como migración antes de desplegar la versión con MFA; no se debe repetir `001_schema.sql` allí.

Se conserva la corrección técnica del modelo: **USUARIO 1:N MOVIMIENTO_INVENTARIO**. El stock se deriva de movimientos inmutables y las operaciones de confirmación utilizan transacciones y `FOR UPDATE` para proteger la consistencia concurrente.

Si cambia los scripts de inicialización y necesita reconstruir la BD desde cero:

```bash
docker compose down -v
docker compose up --build -d
```

## API y documentación OpenAPI

Con Docker Compose activo:

- Auth y catálogo: http://localhost:8001/docs
- Pedidos y pagos: http://localhost:8003/docs

## Pruebas

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

El workflow `.github/workflows/ci.yml` ejecuta build, pruebas, generación de reporte HTML y prepara el despliegue de staging.

## Sprint 2 — CI/CD y calidad

El repositorio incluye:

- `Jenkinsfile` con **Checkout → Build → Test → Deploy staging**.
- GitHub Actions como evidencia adicional de CI/CD.
- `pytest-html` para generar el reporte `reports/pytest-report.html`.
- Selenium para pruebas de sistema en navegador.
- Pruebas de integración y rendimiento contra staging.
- Deploy de staging mediante Railway Deploy Hooks sin guardar secretos en el código.
- Edición y anulación/desactivación de registros respetando trazabilidad.
- Rediseño responsive de la interfaz administrativa.

Para Jenkins, inyecte la variable secreta `STAGING_DEPLOY_HOOKS`. Para GitHub Actions, configure `RAILWAY_STAGING_DEPLOY_HOOKS` y `STAGING_BASE_URL` como Secrets.

Ejecución de pruebas obligatorias:

```bash
mkdir -p reports
pytest -m "not integration and not selenium and not performance" \
  --html=reports/pytest-report.html --self-contained-html \
  --junitxml=reports/junit.xml
```

Las pruebas de staging se habilitan con `STAGING_BASE_URL`.

## Seguridad implementada

- Contraseñas PBKDF2-SHA256 con salt aleatorio.
- JWT firmado, expiración y `jti`.
- Logout con revocación de token en Redis.
- Autorización por roles: `ROL_ADMIN`, `ROL_OPER`, `ROL_CONS`.
- Consultas SQL parametrizadas.
- Restricciones de integridad en PostgreSQL.
- Transacciones y bloqueo pesimista para operaciones sensibles de inventario.

Para producción deben añadirse HTTPS, secretos administrados, backups automáticos, observabilidad y credenciales PostgreSQL de mínimo privilegio.

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md)
- [API](docs/API.md)
- [Base de datos](docs/DATABASE.md)
- [Implementación DEVOPS 2](docs/DEVOPS_2_IMPLEMENTACION.md)
- [Plan de pruebas Sprint 2](docs/PLAN_PRUEBAS_SPRINT2.md)
- [Scrum Sprint 2](docs/scrum/SPRINT_2.md)

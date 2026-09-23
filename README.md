# Gestor Clínica — Duality

Aplicación web para la gestión administrativa de **Duality - Clínica de Medicina Estética**, construida a partir de los requerimientos, UML, modelo relacional y arquitectura desarrollados en el Proyecto de Seminario.

La solución cubre los módulos de **usuarios y seguridad, pacientes, productos, servicios, inventario, servicios realizados, ventas/pedidos, pagos, reportes e indicadores**.

## Stack

- **Python 3.12 + FastAPI** para APIs REST.
- **PostgreSQL 16** como base de datos relacional.
- **Redis 7** para revocación de JWT y soporte de caché.
- **Nginx + HTML/CSS/JavaScript** para la interfaz administrativa.
- **Docker / Docker Compose** para ejecutar toda la solución de forma reproducible.

## Microservicios

| Servicio | Responsabilidad | Puerto local |
|---|---|---:|
| `auth` | Login, JWT, roles y usuarios | 8001 |
| `catalogo` | Pacientes, productos, servicios, inventario y servicios realizados | 8002 |
| `pedidos` | Ventas/pedidos, detalle, confirmación y reportes | 8003 |
| `pagos` | Métodos de pago, pagos y estado de cuenta | 8004 |
| `web` | Interfaz administrativa y reverse proxy | 8080 |
| `postgres` | PostgreSQL 16 | 5432 |
| `redis` | Redis 7 | 6379 |

## Estructura del repositorio

```text
/src
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

Credenciales académicas iniciales:

- **Correo:** `admin@duality.local`
- **Contraseña:** `Admin123!`

> El usuario inicial existe únicamente para facilitar la demostración académica. Cambie la contraseña antes de utilizar información real.

## Base de datos

Los scripts SQL se ejecutan automáticamente al inicializar PostgreSQL:

- `docker/postgres/init/001_schema.sql`: esquema Duality, tablas, claves, restricciones, índices, funciones, triggers, procedimientos, vistas y catálogos base.
- `docker/postgres/init/002_app_extensions.sql`: autenticación, pagos, procedimientos de confirmación/pago, vistas del dashboard y usuario administrador inicial.

Se conserva la corrección técnica del modelo: **USUARIO 1:N MOVIMIENTO_INVENTARIO**. El stock se deriva de movimientos inmutables y las operaciones de confirmación utilizan transacciones y `FOR UPDATE` para proteger la consistencia concurrente.

Si cambia los scripts de inicialización y necesita reconstruir la BD desde cero:

```bash
docker compose down -v
docker compose up --build -d
```

## API y documentación OpenAPI

Con Docker Compose activo:

- Auth: http://localhost:8001/docs
- Catálogo: http://localhost:8002/docs
- Pedidos: http://localhost:8003/docs
- Pagos: http://localhost:8004/docs

## Pruebas

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

El workflow `.github/workflows/ci.yml` ejecuta las pruebas automáticamente en GitHub Actions.

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

# Gestor Clínica — Duality

Aplicación web de gestión administrativa para **Duality - Clínica de Medicina Estética**. El proyecto implementa los módulos definidos durante el seminario: usuarios y seguridad, pacientes, catálogo de productos y servicios, inventario, servicios realizados, ventas/pedidos, pagos, reportes e indicadores.

## Arquitectura

La solución usa **Python 3.12 + FastAPI**, **PostgreSQL 16**, **Redis 7** y una interfaz web estática detrás de **Nginx**. Se divide en cuatro microservicios requeridos:

- **auth**: autenticación JWT, cierre de sesión con revocación en Redis, roles y usuarios.
- **catalog**: pacientes, productos, servicios, inventario y servicios clínicos realizados.
- **orders**: ventas/pedidos, detalle de productos, confirmación y reportes.
- **payments**: métodos de pago y registro de pagos.

PostgreSQL mantiene el modelo relacional de Duality. Redis se utiliza para revocar tokens JWT y deja preparada una capa de caché compartida. La interfaz web consume los cuatro servicios mediante un reverse proxy Nginx.

## Estructura del repositorio

```text
/src          código de microservicios y frontend
/docs         arquitectura, API y modelo de datos
/docker       scripts reproducibles de PostgreSQL
/tests        pruebas automáticas
docker-compose.yml
.env.example
```

## Requisitos

- Docker Engine 24+
- Docker Compose v2

## Puesta en marcha

1. Copiar la configuración de ejemplo:

   ```bash
   cp .env.example .env
   ```

2. Cambiar como mínimo `POSTGRES_PASSWORD` y `JWT_SECRET` en `.env`.
3. Construir e iniciar toda la solución:

   ```bash
   docker compose up --build -d
   ```

4. Abrir **http://localhost:8080**.

Credenciales académicas iniciales:

- **Correo:** `admin@duality.local`
- **Contraseña:** `Admin123!`

Cambie esta contraseña antes de utilizar el sistema con información real.

## Puertos de desarrollo

| Componente | Puerto |
|---|---:|
| Web | 8080 |
| Auth API | 8001 |
| Catálogo API | 8002 |
| Pedidos API | 8003 |
| Pagos API | 8004 |
| PostgreSQL | 5432 |
| Redis | 6379 |

Cada API expone documentación OpenAPI en `/docs`, por ejemplo: `http://localhost:8001/docs`.

## Base de datos

Los scripts se ejecutan automáticamente al crear por primera vez el volumen de PostgreSQL:

1. `docker/postgres/init/001_schema.sql`: modelo relacional, índices, funciones, triggers, procedimientos, vistas y catálogos base.
2. `docker/postgres/init/002_app_extensions.sql`: autenticación, pagos, vistas operativas y usuario administrador inicial.

El control de inventario conserva la corrección técnica del proyecto: `USUARIO 1:N MOVIMIENTO_INVENTARIO`, movimientos inmutables y validación concurrente del stock mediante bloqueo de fila (`FOR UPDATE`) y transacciones ACID.

> Si modifica los scripts de inicialización y desea recrear la BD desde cero: `docker compose down -v && docker compose up --build`.

## Pruebas

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

Las pruebas de contrato verifican que el SQL contenga los objetos críticos y que la configuración de Docker incluya PostgreSQL, Redis y los cuatro microservicios.

## Seguridad

- Contraseñas almacenadas con PBKDF2-SHA256 y salt aleatorio.
- JWT con expiración y `jti`; logout revoca tokens en Redis.
- Autorización por roles (`ROL_ADMIN`, `ROL_OPER`, `ROL_CONS`).
- Parámetros SQL enlazados; no se concatena entrada de usuario en consultas.
- Validaciones y restricciones también existen en PostgreSQL.
- Para producción: HTTPS, secretos administrados, usuario PostgreSQL de mínimo privilegio, backups y rotación de credenciales.

## Documentación adicional

- [Arquitectura](docs/ARCHITECTURE.md)
- [API](docs/API.md)
- [Base de datos](docs/DATABASE.md)

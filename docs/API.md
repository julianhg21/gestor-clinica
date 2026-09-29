# API

## Auth (8001)
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET/POST /api/users`
- `PUT/DELETE /api/users/{id}`
- `GET /api/roles`

## Catálogo (8002)
- `GET/POST /api/catalogo/patients`
- `GET/PUT/DELETE /api/catalogo/patients/{id}`
- `GET/POST /api/catalogo/products`
- `PUT/DELETE /api/catalogo/products/{id}`
- `GET/POST /api/catalogo/services`
- `PUT/DELETE /api/catalogo/services/{id}`
- `GET /api/catalogo/inventory`
- `GET/POST /api/catalogo/inventory/movements`
- `GET/POST /api/catalogo/clinical-services`
- `PUT/DELETE /api/catalogo/clinical-services/{id}`
- `POST /api/catalogo/clinical-services/{id}/consumptions`
- `POST /api/catalogo/clinical-services/{id}/finalize`
- `GET /api/catalogo/dashboard`

## Pedidos (8003)
- `GET/POST /api/pedidos`
- `GET/PUT/DELETE /api/pedidos/{id}`
- `POST /api/pedidos/{id}/confirm`
- `POST /api/pedidos/{id}/cancel`
- `GET /api/pedidos/reportes/diario`

## Pagos (8004)
- `GET/POST /api/metodos-pago`
- `GET/POST /api/pagos`
- `PUT/DELETE /api/pagos/{id}`

Todos los endpoints, salvo `login` y `health`, requieren `Authorization: Bearer <JWT>`.

Las operaciones DELETE de pacientes, productos, servicios, ventas, pagos, servicios realizados y usuarios se implementan como desactivación/anulación cuando la trazabilidad del dominio lo requiere.

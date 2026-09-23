# API

## Auth (8001)
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET/POST/PUT /api/users`
- `GET /api/roles`

## Catálogo (8002)
- `GET/POST/PUT/DELETE /api/catalogo/patients`
- `GET/POST/PUT/DELETE /api/catalogo/products`
- `GET/POST/PUT/DELETE /api/catalogo/services`
- `GET /api/catalogo/inventory`
- `GET/POST /api/catalogo/inventory/movements`
- `GET/POST /api/catalogo/clinical-services`
- `POST /api/catalogo/clinical-services/{id}/consumptions`
- `POST /api/catalogo/clinical-services/{id}/finalize`
- `GET /api/catalogo/dashboard`

## Pedidos (8003)
- `GET/POST /api/pedidos`
- `GET/PUT /api/pedidos/{id}`
- `POST /api/pedidos/{id}/confirm`
- `POST /api/pedidos/{id}/cancel`
- `GET /api/pedidos/reports/daily`

## Pagos (8004)
- `GET/POST /api/metodos-pago`
- `GET/POST /api/pagos`

Todos los endpoints, salvo `login` y `health`, requieren `Authorization: Bearer <JWT>`.

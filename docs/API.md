# API

## Auth (8001)
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET/POST/PUT /api/users`
- `GET /api/roles`

## Catálogo (8002)
- `GET/POST/PUT/DELETE /api/catalog/patients`
- `GET/POST/PUT/DELETE /api/catalog/products`
- `GET/POST/PUT/DELETE /api/catalog/services`
- `GET /api/catalog/inventory`
- `GET/POST /api/catalog/inventory/movements`
- `GET/POST /api/catalog/clinical-services`
- `POST /api/catalog/clinical-services/{id}/consumptions`
- `POST /api/catalog/clinical-services/{id}/finalize`
- `GET /api/catalog/dashboard`

## Pedidos (8003)
- `GET/POST /api/orders`
- `GET/PUT /api/orders/{id}`
- `POST /api/orders/{id}/confirm`
- `POST /api/orders/{id}/cancel`
- `GET /api/orders/reports/daily`

## Pagos (8004)
- `GET/POST /api/payment-methods`
- `GET/POST /api/payments`

Todos los endpoints, salvo `login` y `health`, requieren `Authorization: Bearer <JWT>`.

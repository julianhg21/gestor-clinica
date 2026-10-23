# Matriz de accesos observados

Extraída de dependencias FastAPI locales. No acredita aprobación de la clínica. Todos los roles tienen lectura administrativa por current_user salvo usuarios (solo administrador). OPER y ADMIN pueden crear/editar la mayoría de registros; bajas de pacientes/ventas/productos/servicios/pagos y gestión de usuarios dependen de la ruta. La tabla exacta evita atribuir privilegios por suposición.

Condiciones comunes: JWT válido, Redis disponible, cuenta activa y mismo rol en BD; 401 al faltar autenticación/identidad vigente, 403 ante rol insuficiente, 503 ante fallo de verificación. Acceso local por web 8080 o APIs 8001–8004; origen autorizado real y acceso remoto pendientes. ROL_CONS también accede a datos de pacientes: validar necesidad de conocer. Cuentas de servicio/DB requieren mínimo privilegio (C16). Cuentas cloud, Jenkins y administradores del host: propietarios/MFA por confirmar.

| Método | Recurso | Privilegio exigido en código | Fuente |
|---|---|---|---|
| GET | `/api/auth/health` | Público | `src/auth/main.py` |
| POST | `/api/auth/login` | Público | `src/auth/main.py` |
| GET | `/api/auth/me` | Cualquier cuenta activa con rol vigente | `src/auth/main.py` |
| POST | `/api/auth/logout` | Sin token: 204 sin acción; con token: JWT y revocación válidos | `src/auth/main.py` |
| GET | `/api/roles` | Cualquier cuenta activa con rol vigente | `src/auth/main.py` |
| GET | `/api/users` | ROL_ADMIN | `src/auth/main.py` |
| POST | `/api/users` | ROL_ADMIN | `src/auth/main.py` |
| PUT | `/api/users/{user_id}` | ROL_ADMIN | `src/auth/main.py` |
| DELETE | `/api/users/{user_id}` | ROL_ADMIN | `src/auth/main.py` |
| GET | `/api/catalogo/health` | Público | `src/catalogo/main.py` |
| GET | `/api/catalogo/dashboard` | Cualquier cuenta activa con rol vigente | `src/catalogo/main.py` |
| GET | `/api/catalogo/patients` | Cualquier cuenta activa con rol vigente | `src/catalogo/main.py` |
| GET | `/api/catalogo/patients/{patient_id}` | Cualquier cuenta activa con rol vigente | `src/catalogo/main.py` |
| POST | `/api/catalogo/patients` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| PUT | `/api/catalogo/patients/{patient_id}` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| DELETE | `/api/catalogo/patients/{patient_id}` | ROL_ADMIN | `src/catalogo/main.py` |
| GET | `/api/catalogo/products` | Cualquier cuenta activa con rol vigente | `src/catalogo/main.py` |
| POST | `/api/catalogo/products` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| PUT | `/api/catalogo/products/{product_id}` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| DELETE | `/api/catalogo/products/{product_id}` | ROL_ADMIN | `src/catalogo/main.py` |
| GET | `/api/catalogo/services` | Cualquier cuenta activa con rol vigente | `src/catalogo/main.py` |
| POST | `/api/catalogo/services` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| PUT | `/api/catalogo/services/{service_id}` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| DELETE | `/api/catalogo/services/{service_id}` | ROL_ADMIN | `src/catalogo/main.py` |
| GET | `/api/catalogo/inventory` | Cualquier cuenta activa con rol vigente | `src/catalogo/main.py` |
| GET | `/api/catalogo/inventory/movements` | Cualquier cuenta activa con rol vigente | `src/catalogo/main.py` |
| POST | `/api/catalogo/inventory/movements` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| GET | `/api/catalogo/clinical-services` | Cualquier cuenta activa con rol vigente | `src/catalogo/main.py` |
| POST | `/api/catalogo/clinical-services` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| PUT | `/api/catalogo/clinical-services/{record_id}` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| DELETE | `/api/catalogo/clinical-services/{record_id}` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| POST | `/api/catalogo/clinical-services/{record_id}/consumptions` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| POST | `/api/catalogo/clinical-services/{record_id}/finalize` | ROL_ADMIN, ROL_OPER | `src/catalogo/main.py` |
| GET | `/api/pedidos/health` | Público | `src/pedidos/main.py` |
| GET | `/api/pedidos` | Cualquier cuenta activa con rol vigente | `src/pedidos/main.py` |
| GET | `/api/pedidos/{order_id}` | Cualquier cuenta activa con rol vigente | `src/pedidos/main.py` |
| POST | `/api/pedidos` | ROL_ADMIN, ROL_OPER | `src/pedidos/main.py` |
| PUT | `/api/pedidos/{order_id}` | ROL_ADMIN, ROL_OPER | `src/pedidos/main.py` |
| POST | `/api/pedidos/{order_id}/confirm` | ROL_ADMIN, ROL_OPER | `src/pedidos/main.py` |
| POST | `/api/pedidos/{order_id}/cancel` | ROL_ADMIN | `src/pedidos/main.py` |
| DELETE | `/api/pedidos/{order_id}` | ROL_ADMIN | `src/pedidos/main.py` |
| GET | `/api/pedidos/reportes/diario` | Cualquier cuenta activa con rol vigente | `src/pedidos/main.py` |
| GET | `/api/pagos/health` | Público | `src/pagos/main.py` |
| GET | `/api/metodos-pago` | Cualquier cuenta activa con rol vigente | `src/pagos/main.py` |
| POST | `/api/metodos-pago` | ROL_ADMIN | `src/pagos/main.py` |
| GET | `/api/pagos` | Cualquier cuenta activa con rol vigente | `src/pagos/main.py` |
| POST | `/api/pagos` | ROL_ADMIN, ROL_OPER | `src/pagos/main.py` |
| PUT | `/api/pagos/{payment_id}` | ROL_ADMIN, ROL_OPER | `src/pagos/main.py` |
| DELETE | `/api/pagos/{payment_id}` | ROL_ADMIN | `src/pagos/main.py` |

Procedimiento propuesto de alta: solicitud con función/recursos, aprobación de propietaria, cuenta individual, privilegio mínimo y registro de entrega sin contraseña. Baja: desactivar, verificar rechazo de JWT existente, retirar accesos cloud y revisar sesiones. Cambio de rol: nueva autenticación requerida. Revisión propuesta trimestral y ante cambio de personal, sujeta a aprobación. No se afirma que este proceso esté operativo.

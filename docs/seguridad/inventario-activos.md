# Inventario de activos lógico

Este inventario se deriva del código, no de una visita a la clínica. Propietario de negocio, custodio nominal, ubicación real y criticidad final: por confirmar con la propietaria. Las clasificaciones son propuestas para su aprobación.

| ID | Activo y proceso | Ubicación observada / dependencia | Clasificación / criticidad preliminar | Propietario y custodio propuestos | Protección requerida |
|---|---|---|---|---|---|
| A01 | Información de pacientes, servicios realizados, ventas, pagos y usuarios | Tablas duality; APIs y frontend | Restringida (pacientes), confidencial (finanzas); alta | Propietaria / administrador técnico | Acceso por necesidad, TLS, minimización, retención aprobada |
| A02 | PostgreSQL y objetos de integridad | Imagen postgres:16-alpine; SQL 001–003; volumen postgres_data en Compose | Restringida; alta | Propietaria / DBA designado | Rol mínimo, respaldo cifrado y ensayo de restauración |
| A03 | Identidades, hashes, JWT, secreto de firma y revocaciones | common/security.py, auth/main.py, Redis | Restringida; alta | Propietaria / administrador técnico | Rotación, revocación fiable, MFA administrativo |
| A04 | APIs administrativas Python/FastAPI | auth, catalogo, pedidos, pagos, common; psycopg | Interna; alta | Responsable de producto por designar / equipo técnico | Validación, autorización, errores seguros y revisión |
| A05 | Frontend y proxy | src/web; Nginx; navegador | Código interno, datos mostrados restringidos; alta | Equipo técnico / administrador | Codificación de salidas, gestión de sesión y TLS |
| A06 | Contenedores, red y configuración de host | docker/, docker-compose.yml | Interna; alta | Administrador por designar | Reducir puertos, parches, cuentas, límites y monitoreo |
| A07 | Código, pipelines y evidencias | .git, .github/workflows, Jenkinsfile, azure-pipelines.yml | Interna; alta | Propietario repositorio por confirmar / mantenedor | Revisión, ramas protegidas, no exponer secretos |
| A08 | Bibliotecas de aplicación y herramientas de prueba | src/requirements.txt, requirements-dev.txt, requirements-security.txt | Pública (paquetes); dependencia alta | Equipo técnico | Auditoría de avisos y compatibilidad de versiones |
| A09 | Referencias a proveedores externos | GitHub confirmado por configuración; Railway/Neon/Upstash documentados; operación no verificada | Datos según uso, por confirmar | Titular de cuenta por confirmar | Inventario cloud y responsabilidad compartida |

Los respaldos operativos no se registran como activos existentes: su creación y custodia permanecen propuestas sobre A02. No se inventan laptops, routers, servidores físicos, VLAN ni contratos.

Para cerrar el levantamiento: entrevistar sobre procesos críticos, consecuencias de interrupción, creación/lectura/cambio/eliminación de datos, usuarios reales y permisos esperados, dispositivos/red, dependencias y requisitos de confidencialidad, integridad, disponibilidad y trazabilidad; conservar acta consentida sin datos de pacientes.

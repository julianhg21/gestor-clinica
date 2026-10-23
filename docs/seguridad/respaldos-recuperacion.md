# Respaldos y recuperación

C11: Implementado y validado exclusivamente el ensayo técnico sintético. C27: Propuesto para operación de clínica. No existe RTO/RPO aprobado, responsable nominal, frecuencia o retención confirmada.

Información crítica: pacientes/usuarios/servicios realizados, movimientos, ventas/detalles/pagos y catálogos; esquema, funciones, triggers y vistas. Dependencias de recuperación: imagen compatible PostgreSQL, configuración, secreto de firma, Redis y su persistencia, versiones de APIs/web, identidad de proveedor, acceso seguro y capacidad de destino. Un dump solo del esquema duality no recupera todo el servidor, IAM, secretos ni continuidad de la aplicación.

## Ensayo ejecutado

Contenedor `duality-audit-postgres-20261023`, etiqueta `duality.audit=20261023`, red `none`, sin bind mounts ni puertos públicos. El modo trust solo es válido en este laboratorio sin red. Fixture verifica aislamiento antes de inicializar esquema; nunca usa DATABASE_URL. Scripts 001–003 son destructivos para el esquema y solo se ejecutaron en este destino desechable.

`test_backup_restore_in_separate_database` ejecuta pg_dump del esquema duality en memoria, crea audit_restore y restaura mediante psql con ON_ERROR_STOP. Compara cantidades de productos/movimientos/pagos, suma de pagos y stock; verifica rechazo de UPDATE de movimientos en la base restaurada. El dump no se exporta porque contiene el bootstrap académico. Evidencias: E03; `evidencias/bases-datos/postgres.xml` y `evidencias/devsecops/final.xml`. Tiempo de prueba en XML incluye comandos de laboratorio; no es RTO de negocio. No se realizó recuperación de proveedor ni failover.

## Procedimiento operativo propuesto (requiere aprobación y ambiente)

1. Designar propietario, operador y suplente; acordar procesos críticos, tolerancia a pérdida y tiempo máximo de interrupción. RPO = pérdida temporal máxima tolerable; RTO = tiempo objetivo para recuperar servicio.
2. Aprobar frecuencia/retención según RPO, acceso y clasificación; seleccionar copia cifrada fuera del host y alertas de fallos. No fijar valores sin BIA.
3. Realizar copia consistente PostgreSQL con herramienta compatible y permisos mínimos; proteger credenciales fuera de argumentos/logs; incluir roles/configuración cuando sea necesario sin publicar secretos.
4. Registrar hora, destino protegido, tamaño, checksum, versión, operador y estado; verificar lectura y acceso mínimo. Redis revocado debe persistir hasta expiración o invalidar sesiones según plan autorizado.
5. Restaurar en una instancia distinta aislada, nunca sobre producción; comprobar tablas, FK, funciones, stock, pagos, identidad y flujo de negocio. Medir tiempos desde incidente hasta servicio verificado y pérdida efectiva de datos.
6. Comparar con RTO/RPO aprobados; corregir desviaciones, registrar revisión y autorizar retorno antes de cambiar endpoints o datos persistentes.

No usar `docker compose down -v` como procedimiento de recuperación: elimina volúmenes. No reejecutar 001_schema.sql en datos existentes. Limpieza del laboratorio solo tras identificar exactamente contenedor/etiqueta y volumen anónimo creados por este ensayo.

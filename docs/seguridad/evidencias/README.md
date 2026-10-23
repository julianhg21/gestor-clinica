# Índice de evidencias reales

Fecha de cierre del índice: 2026-10-23T12:41:18.928993-06:00. Zona: America/Guatemala (UTC-06:00). Commit base `f5351224bd8910be20e19db743f6a7b1b7921401`, rama `auditoria-ciberseguridad`, cambios **sin commit**. No se atribuyen estos resultados a un commit que aún no contiene los cambios. Hashes del código usado por el colector: ejecuciones.json; cierre de archivos: MANIFEST-SHA256.json.

Ambiente: Windows-10-10.0.19045-SP0, Python 3.12.14; PostgreSQL 16.15 en Linux, Docker 29.8.1. Pruebas de API con dobles controlados de Redis/BD; SQL y restauración con PostgreSQL real aislado. Fechas de inicio/fin y comandos del colector están en ejecuciones.json. Para otras evidencias se registra la hora de modificación del archivo como hora de conservación, no un inicio inferido. El PNG es captura de navegador de una página/reporte auténticos, no imagen generada ni prueba de producción.

Documentos de entrada no copiados ni publicados. Dumps, secretos, JWT y datos personales reales no se conservan. El escaneo es por patrones y revisión visual, con límites declarados.

## E01

- Control: C01–C05,C07–C10,C29. Riesgo: R01,R03,R05,R06.
- Archivos (rutas relativas a esta carpeta): devsecops/final.xml; devsecops/final.html; devsecops/final.txt; devsecops/pytest-local.png.
- Procedimiento: `python scripts/collect_security_evidence.py --database`.
- Esperado: Sin fallos; omisiones externas explícitas.
- Real: 69 aprobadas, 6 omitidas, 0 fallos; 1 warning de deprecación.
- Estado: Implementado y validado solo ejecución local.
- Límites: API con Redis/BD simulados; SQL con PostgreSQL real; no staging.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## E02

- Control: C06. Riesgo: R04.
- Archivos (rutas relativas a esta carpeta): autenticacion/frontend.txt.
- Procedimiento: `node tests/security_frontend.cjs`.
- Esperado: Etiquetas/comillas no inyectan HTML; formato conservado.
- Real: PASS: texto, columnas, formato e identificadores sintéticos.
- Estado: Parcialmente implementado.
- Límites: Prueba de funciones JS en Node; no ataque DOM completo en navegador.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## E03

- Control: C09–C11,C14,C26. Riesgo: R05,R10.
- Archivos (rutas relativas a esta carpeta): bases-datos/postgres.xml; bases-datos/postgres.html; bases-datos/postgres.txt; bases-datos/postgres.png; bases-datos/version.txt; devsecops/final.xml.
- Procedimiento: `pytest tests/test_audit_database.py (AUDIT_DB_CONTAINER validado); pg_dump/psql dentro del contenedor`.
- Esperado: Sin stock negativo/sobrepago; rollback; restauración íntegra.
- Real: 5 casos SQL aprobados en corrida separada y repetidos en final; PostgreSQL 16.15.
- Estado: Implementado y validado en laboratorio.
- Límites: Datos sintéticos; restauración de esquema, no servicio completo; no RTO/RPO de negocio.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## E04

- Control: C12. Riesgo: R02.
- Archivos (rutas relativas a esta carpeta): autenticacion/login-local.png; devsecops/configuracion.json.
- Procedimiento: `HTTP server 127.0.0.1:8766, abrir src/web/index.html con navegador y capturar`.
- Esperado: Correo/contraseña vacíos sin datos personales.
- Real: Formulario sin valores precargados confirmado por AX y PNG.
- Estado: Implementado y validado para formulario.
- Límites: Servidor estático local sin backend; no es prueba de login desplegado.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## E05

- Control: C17. Riesgo: R07.
- Archivos (rutas relativas a esta carpeta): infraestructura/compose.txt; devsecops/configuracion.json.
- Procedimiento: `docker compose config --quiet; python scripts/inspect_security_config.py`.
- Esperado: Compose válido; enumerar exposición sin imprimir secretos.
- Real: Salida válida; puertos 5432/6379/8001–8004/8080 expuestos en host.
- Estado: Parcialmente implementado.
- Límites: Valida sintaxis e inspección, no firewall/red productiva.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## E06

- Control: C18. Riesgo: R07.
- Archivos (rutas relativas a esta carpeta): contenedores/build-auth.txt; contenedores/runtime-auth.txt.
- Procedimiento: `docker build -f docker/auth/Dockerfile -t duality-audit-auth:20261023 .; docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges duality-audit-auth:20261023 python -c <importar auth e imprimir UID>`.
- Esperado: Build e importación como usuario no root.
- Real: Build exitoso; uid=65532; auth_import=ok.
- Estado: Parcialmente implementado.
- Límites: Solo imagen auth; flags de ensayo no aplicados a Compose; no escaneo CVE de imagen.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## E07

- Control: C21,C40. Riesgo: R02,R09.
- Archivos (rutas relativas a esta carpeta): revision-secretos.json; ejecuciones.json; MANIFEST-SHA256.json.
- Procedimiento: `Revisión de patrones sobre evidencias; hashes SHA256`.
- Esperado: Sin JWT, claves privadas ni contraseñas en evidencias.
- Real: Resultado exacto en revision-secretos.json.
- Estado: Implementado y validado para paquete local.
- Límites: Escaneo por patrones y revisión visual; no historial Git ni certificación de ausencia total de secretos.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## E08

- Control: C22. Riesgo: R08.
- Archivos (rutas relativas a esta carpeta): vulnerabilidades/dependencias.json; vulnerabilidades/dependencias-runtime-dev.json.
- Procedimiento: `python -m pip_audit --format json --output <reporte> --progress-spinner off`.
- Esperado: Generar avisos y retornar no-cero si existen.
- Real: Exit 1: 50 registros de avisos en 4 paquetes; 31 IDs distintos, algunos avisos tienen alias/duplicados.
- Estado: Parcialmente implementado.
- Límites: Paquetes instalados en .venv Windows; no acredita explotabilidad ni cubre SO/imagen Linux.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## E09

- Control: C23. Riesgo: R06.
- Archivos (rutas relativas a esta carpeta): vulnerabilidades/bandit.json.
- Procedimiento: `python -m bandit -r src -f json -o <reporte>`.
- Esperado: Análisis estático con hallazgos revisados.
- Real: B105 bajo: literal bearer; B608 medio: UPDATE con nombres de lista fija.
- Estado: Parcialmente implementado.
- Límites: Bandit no sustituye revisión de código ni pruebas; no se suprimieron hallazgos sin explicación.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## E10

- Control: C24,C34,C36,C37. Riesgo: R09,R11.
- Archivos (rutas relativas a esta carpeta): devsecops/configuracion.json.
- Procedimiento: `python scripts/inspect_security_config.py y contraste con fuentes versionadas`.
- Esperado: Guardas exit 1 y permisos mínimos; topología coherente.
- Real: Guardas locales de deploy/post-deploy devuelven exit 1 en configuración; inventario y UML contrastados.
- Estado: Parcialmente implementado.
- Límites: Sin ejecución nueva del cambio local; estado remoto/histórico verificado posteriormente en E11; UML fuente sin render.
- Commit/ambiente: los indicados al inicio; fecha/hora de conservación por archivo en MANIFEST-SHA256.json.

## Reproducción del laboratorio

1. Instalar requisitos en .venv local; no cargar .env ni variables de staging.
2. Crear únicamente el destino aislado del ensayo:

```powershell
docker run -d --name duality-audit-postgres-20261023 --label duality.audit=20261023 --network none -e POSTGRES_HOST_AUTH_METHOD=trust postgres:16-alpine
docker exec duality-audit-postgres-20261023 pg_isready -U postgres
.\.venv\Scripts\python.exe scripts/collect_security_evidence.py --database
```

El método trust es exclusivo de este contenedor sin red ni puertos, no es configuración aprobada de la aplicación. No usar el nombre/etiqueta en contenedores con datos reales. La fixture rechaza otro nombre, etiqueta, red o bind mount. Reejecuta SQL destructivo únicamente en este destino. El colector sin --database ejecuta la parte local sin usar Docker para SQL; las pruebas SQL se omiten de forma explícita.

3. Revisar resultados, secretos y hashes; renovar capturas si cambian los reportes. Retirar el contenedor y su volumen anónimo solo después de validar su identidad/etiqueta. Conservar fuentes y evidencias.

Las carpetas por categoría contienen índices hacia el reporte compartido, evitando copias que puedan divergir. Las evidencias de ejecución separada de PostgreSQL son suplementarias; la ejecución final es la referencia de hashes del código probado.

## E11

- Control: C24/C25; riesgos R09/R12; activo A07.
- Evidencia: devsecops/github-historico.json.
- Procedimiento: GitHub conector GET rama main, rulesets, runs del commit base, jobs y logs de tres jobs. Solo se conservan metadatos mínimos y líneas relevantes sin echo de comandos.
- Fecha de consulta: consulta_utc dentro del JSON. Fecha de corrida: 10/10/2026; ambiente: GitHub Actions histórico, no ejecución local nueva. Commit: f5351224bd8910be20e19db743f6a7b1b7921401.
- Esperado: determinar protección real y si éxito de job acredita deploy.
- Real: main sin protección/rulesets vacíos; corrida #55 exitosa pero logs confirman despliegue y pruebas posteriores omitidos; 33 pruebas históricas aprobadas.
- Estado: Parcialmente implementado (C24); Propuesto (C25).
- Limitaciones: extractos sanitizados, sin cambios remotos, sin ejecutar workflows nuevos; permisos/MFA de cuentas no auditados.

Los reportes de pip-audit están sanitizados: ejemplos JWT incluidos en descripciones públicas se sustituyeron por una marca; conteos e IDs no cambiaron. Registro y hashes originales: sanitizacion.json en la raíz de evidencias.

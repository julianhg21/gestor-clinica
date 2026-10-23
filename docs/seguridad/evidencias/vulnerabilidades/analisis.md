# Revisión de avisos y análisis estático

Origen: pip-audit 2.10.1 sobre .venv; metadatos públicos de avisos consultados el 23/10/2026. Se completó instalación de src/requirements.txt antes del segundo reporte. Ambos retornan exit 1. No se ejecutó explotación. Los paquetes de herramientas y aplicación están juntos; esto no es un SBOM del contenedor Linux.

| Paquete | Versión instalada | Registros devueltos | IDs de aviso distintos |
|---|---|---|---|
| pip | 25.0.1 | 12 | 6 |
| pyjwt | 2.10.1 | 22 | 17 |
| pytest | 8.3.4 | 2 | 1 |
| starlette | 0.41.3 | 14 | 7 |

Son 50 registros, 31 IDs distintos; no se deben presentar como 50 vulnerabilidades únicas ni 31 CVE distintas. Los alias también pueden referirse al mismo problema. Los reportes conservan fix_versions/aliases/descripción para revisión de aplicabilidad.

PyJWT: 17 IDs distintos, incluidos avisos de JWKS/algoritmos no usados por esta implementación HS256 de clave estática. PYSEC-2025-183 está disputado por el proveedor según su descripción. Esto no justifica ignorar la actualización: evaluar cada aviso y probar migración compatible. Starlette: 7 IDs distintos; algunas rutas de multipart/StaticFiles no son usadas, pero la biblioteca está instalada. FastAPI 0.115.6 exige Starlette <0.42, por lo que no basta forzar una versión corregida ignorando restricciones; preparar actualización coordinada y pruebas de contratos. Pytest y pip afectan herramientas de desarrollo/CI, no directamente las rutas de pacientes.

Propuesta: actualización planificada de FastAPI/Starlette y PyJWT con autorización de impacto de autenticación/API, herramientas de CI actualizadas, dependencia transitiva resuelta y nueva auditoría después de pruebas. No hay aceptación formal ni supresiones de CVE. Security workflow fallará mientras existan avisos; no se presenta el pipeline como verde.

Bandit 1.9.4: B105 (bajo) en auth/main.py se refiere al literal del tipo bearer, no una contraseña; B608 (medio) en update_user usa columnas seleccionadas de lista fija y valores separados, por lo que la alerta no demuestra inyección explotable. Mantener revisión de la lista y parametrización. Quedan riesgos fuera de estas alertas: fallback de secretos, XSS, errores SQL expuestos, privilegios/red y falta de auditoría central. No se hizo escaneo CVE de imágenes ni de hosts.

Los reportes de pip-audit están sanitizados: ejemplos JWT incluidos en descripciones públicas se sustituyeron por una marca; conteos e IDs no cambiaron. Registro y hashes originales: sanitizacion.json en la raíz de evidencias.

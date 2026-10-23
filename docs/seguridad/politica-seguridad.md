# Política integral general y adaptación a Duality — borrador 1.0

Estado: Propuesto. Autoría técnica: equipo del proyecto asistido por Codex; aprobación, vigencia y responsables nominales: sin asignar. No constituye una política adoptada por la clínica ni una opinión legal. Aplicación técnica parcial documentada por separado en la matriz.

## Marco general

Objetivo: proteger confidencialidad (acceso permitido), integridad (datos correctos), disponibilidad (servicio recuperable) y trazabilidad (actor/resultado) durante el ciclo de desarrollo y operación. Alcance general: personas con acceso, información, equipos, aplicaciones, bases, redes, proveedores y cambios que soportan procesos críticos. Aplicabilidad: seleccionar controles según activo, riesgo, capacidad de prueba y contexto; exclusiones requieren justificación y revisión.

Marco propuesto: NIST CSF 2.0, organizando gobierno, identificación, protección, detección, respuesta y recuperación. Referencia técnica complementaria: OWASP ASVS para requisitos verificables de aplicaciones, sin afirmar evaluación formal por nivel ni cobertura completa.

Fuentes primarias consultadas el 23/10/2026: [NIST CSF 2.0](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf) y [OWASP ASVS](https://asvs.owasp.org/). La guía del curso es la fuente de obligaciones del entregable.

Principios: mínimo privilegio, cuentas individuales, separación de funciones viable, defensa por capas, configuración explícita, minimización, evidencia auténtica y decisiones documentadas. Un riesgo es la combinación de amenaza, vulnerabilidad, probabilidad e impacto sobre un activo. Un control válido necesita implementación, prueba y límite declarado.

## Gobierno y autoridades (GOVERN)

La autoridad de negocio debe aprobar alcance, política, prioridades, excepciones y riesgo residual; designar dueño de cada activo/riesgo y suplente. El responsable operativo valida necesidad de acceso y reporta incidentes. Administración técnica conserva configuración, registros, parches, backups y recuperación. Desarrollo revisa código/dependencias, prueba en aislamiento y mantiene trazabilidad. Usuarios protegen credenciales y reportan anomalías. Los nombres y canales se completarán con entrevista; no se atribuyen aprobaciones a personas reales.

Revisión propuesta: trimestral y después de incidente/cambio relevante; registrar fecha, versión, decisiones, responsable y cierre de acciones. Excepciones: activo/control, motivo, riesgo, compensación, aprobador y vencimiento; nunca aceptación implícita por falta de presupuesto o acceso.

## Activos, riesgos y datos (IDENTIFY)

Inventariar solo activos confirmados, registrando dueño, custodio, finalidad, ubicación, dependencia y criticidad. Mantener P/I y tratamiento trazables. Priorizar riesgo alto antes de uso real. Aceptar/transferir/evitar requiere decisión explícita de negocio y soporte contractual cuando corresponda.

| Clase propuesta | Manejo general | Adaptación Duality |
|---|---|---|
| Pública | Difusión autorizada y revisión de contenido | Material comercial aprobado, sin pacientes |
| Interna | Acceso de equipo autorizado; integridad y versiones | Código, diagramas, procedimientos |
| Confidencial | Acceso por función, transferencia cifrada, retención aprobada | Ventas, pagos, reportes y referencias |
| Restringida | Acceso mínimo, cifrado cuando aplique, registro y eliminación controlada | Datos de pacientes, credenciales, hashes, JWT y backups |

La clínica debe fijar finalidad, conservación y eliminación por clase con asesoría pertinente. No se establecen años de retención ni obligaciones jurídicas no verificadas. Backups y exportaciones heredan sensibilidad; borrar registros relacionados exige proceso autorizado y conservación de trazabilidad.

## Protección (PROTECT)

Accesos: altas/cambios/bajas aprobados; revisar privilegios y cuentas administrativas; MFA propuesto para repositorio, cloud y administración remota. Acceso remoto solo por canales aprobados y con registro; no se presume VPN existente. Cuentas de servicio separadas y mínimo privilegio en BD.

Aplicaciones: validar autenticación/rol en servidor, no confiar en UI; expirar y revocar sesiones; denegar verificación si Redis falla; mantener identidad vigente; usar PBKDF2 y parámetros SQL; validar entradas; codificar salida; responder errores sin secretos. Registrar operaciones críticas con campos mínimos y sin cuerpos, tokens, contraseñas o datos de pacientes. Cambios de contrato/autenticación/modelo necesitan autorización del solicitante.

Infraestructura: inventariar hosts y dispositivos, actualizar parches e imágenes, desactivar servicios innecesarios, reducir cuentas/puertos y separar límites de confianza. Usar TLS en exposición pública, cifrado de copias y administración segura. Bloqueo de pantalla y antimalware/EDR se evaluarán en equipos reales. VLAN/Wi-Fi/VPN/IDS/IPS requieren necesidad y contexto; no se añaden tecnologías por lista.

DevSecOps: revisiones y ramas protegidas, permisos CI mínimos, secretos por ambiente, dependencias/imágenes auditadas y evidencia de etapas. Prohibir secretos y documentos de entrada privados en Git/artefactos. Revisar herramientas de IA: no introducir datos reales, secretos o documentos privados en servicios externos sin autorización de destino/finalidad; revisar todo código generado y conservar su autoría asistida.

Cloud y terceros: confirmar proveedor, titular, recurso, datos, accesos, responsabilidades, SLA contractual y recuperación; MFA y mínimos permisos cuando corresponda. La responsabilidad del proveedor no elimina la obligación del equipo de configurar accesos, respaldar y probar recuperación.

## Detección (DETECT)

Revisar fallos de login/rol, cambios privilegiados, revocación no disponible, errores BD, anomalías de stock/pagos, fallos de backup y avisos de dependencias. Centralización, alertas y retención siguen propuestas: definir responsable y canal antes de acreditar operación. Proteger acceso a logs y minimizar información.

## Respuesta y recuperación (RESPOND/RECOVER)

Aplicar gestion-incidentes.md: reportar, clasificar, preservar, contener, erradicar, recuperar y aprender. Aplicar respaldos-recuperacion.md: separar copias, proteger credenciales, restaurar a destino aislado, verificar integridad y autorizar retorno. RTO/RPO y frecuencia/retención se acuerdan según procesos y capacidad real; el ensayo de laboratorio no fija valores productivos.

## Adaptación específica y mejora

La solución administrativa Duality maneja pacientes, servicios realizados, productos, inventario, ventas, pagos, usuarios y reportes. El contexto de ubicación y organización del documento preliminar debe corroborarse mediante entrevistas. No se asume expediente clínico completo ni procesos diagnósticos.

Los controles C01–C40 vinculan cada regla con A01–A09 y R01–R12; matriz-cumplimiento.md distingue validación local, implementación parcial y propuestas. No se declara certificación NIST/OWASP ni cumplimiento legal total. Seguimiento: asignar propietario, fecha objetivo y evidencia de cierre a cada pendiente; revisar cambio/resultado y residual antes de aprobar promoción.

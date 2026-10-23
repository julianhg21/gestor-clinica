# Gestión de cambios y bitácora

Estado C29: Parcialmente implementado. Rama exclusiva auditoria-ciberseguridad; base f5351224bd8910be20e19db743f6a7b1b7921401. Cambios locales sin commit/push/PR. Responsable técnico de esta ejecución: Codex por solicitud del usuario; mantenedor/revisor humano y aprobación de clínica por designar. No se presenta la autorrevisión como aprobación independiente.

Autorización registrada en conversación: usuario autorizó los tres cambios de autenticación: 503 al fallar Redis, claims obligatorios y consulta de usuario activo/rol vigente. Efecto: nueva dependencia de PostgreSQL por petición protegida, latencia adicional y denegación temporal si Redis/BD no verifican. No se cambió el esquema ni se migraron datos existentes.

| Cambio | Motivo / riesgo | Elemento | Impacto y pruebas | Resultado / estado final |
|---|---|---|---|---|
| CH01 | H01–H03/R01/R03 | common/security.py | Claims, revocación fiable y cuenta vigente; E01 con dobles | Regresión local aprobada; integración de API/Redis/BD pendiente |
| CH02 | H05/R04 | app.js | Codificar datos al renderizar, preservar HTML de formato; E02 | Prueba JavaScript aprobada; DOM integral pendiente |
| CH03 | R02 | index.html | Quitar credenciales precargadas sin cambiar login ni bootstrap; E04 | Formulario vacío comprobado en navegador |
| CH04 | H08/R09 | ci.yml, security.yml, azure-pipelines.yml, requirements-security.txt | Fallo explícito en pasos requeridos, auditoría separada, Compose quiet; E10 | Revisión local, sin corrida remota; gate de dependencias detectará avisos abiertos |
| CH05 | R02/R09 | .gitignore, .dockerignore | Excluir insumos y evidencias del contexto Docker; E07 | Configuración local; documentos fuente permanecen fuera de repo |
| CH06 | H11/H12/R05/R10 | tests/test_audit_*.py, security_frontend.cjs y colector | Datos sintéticos; etiqueta/red/bind comprobados antes de SQL; E01/E03 | 69 pruebas aprobadas; 6 omitidas explícitamente |
| CH07 | R11 | docs/seguridad y ARCHITECTURE.md | Trazabilidad, política y UML; revisión documental | Borradores sujetos a aprobación organizacional |

Procedimiento de cambio propuesto: solicitud con motivo/activo/impacto; revisión de riesgo y contrato; autorización cuando afecte identidad/API/modelos/datos/infraestructura; implementación en rama; pruebas y evidencias con base+hashes; revisión independiente; decisión de promoción; observación y cierre del residual. Integrar ID CH y C/R en historia Scrum y PR cuando se autorice publicar.

Rollback propuesto: conservar diff antes de revertir archivos concretos; mantener evidencia; revertir código/configuración al commit conocido en rama revisada y volver a probar. No restaurar BD ni borrar volúmenes para revertir este cambio (no hay migraciones). Volver a la versión previa reintroduce fallo abierto Redis y sesiones de usuarios inactivos: requiere aceptación explícita del riesgo.

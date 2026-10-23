# Proveedores, cloud y responsabilidad compartida

Estados C30/C31: Propuesto para validación operativa. Esta auditoría no contacta producción, no verifica contratos, SLA, MFA ni consolas. No se puede afirmar disponibilidad >99% ni que AWS esté desplegado. Propietario, ambiente real, región, plan, titular de cuenta y residencia de datos: por confirmar.

| Proveedor/componente | Evidencia y estado de uso | Datos/acceso/dependencia | Riesgo/control propuesto | Recuperación propuesta |
|---|---|---|---|---|
| GitHub | Remoto del repositorio y workflows presentes | Código, CI y artefactos; acceso de mantenimiento/secretos por verificar | R09: MFA, revisiones, reglas de rama y contents:read | Copia Git controlada y reconstrucción de artefactos |
| Jenkins | Jenkinsfile presente, ejecución histórica mencionada en preliminar; no reejecutada | Checkout, agente Docker, credenciales de deploy | R09: aislar agente, limitar credenciales, revisar plugins y permisos | Reponer configuración segura desde copia, reconstruir y probar |
| Azure DevOps | azure-pipelines.yml y docs DEVOPS_1; sin corrida verificada | Código espejo/pipeline según configuración por confirmar | R09: revisar service connections, permisos y logs; no imprimir Compose con secretos | Reejecutar pipeline autorizado y conservar resultados auténticos |
| Railway | Hooks de staging y aliases documentados, operación no verificada | APIs/web y variables si está desplegado | R12: permisos, TLS, límites, alertas y secretos distintos | Redeploy de versión conocida tras autorización y pruebas |
| Neon | Documentación menciona PostgreSQL externo, cuenta no verificada | Potencial almacenamiento de A01/A02, acceso DB | R03/R10/R12: rol mínimo, cifrado y backup independiente | Restaurar a instancia nueva y verificar antes de redirigir |
| Upstash | Referencia documental a Redis, sin instancia verificada | Potenciales jti revocados y credencial de conexión | R01/R12: TLS, permisos, persistencia y disponibilidad | Recuperar revocaciones o invalidar sesiones según plan autorizado |
| AWS | Solo previsión del documento preliminar | Ningún recurso concreto confirmado | No agregar como activo desplegado ni inventar IAM/VPC/SLA | Definir solo al confirmar arquitectura necesaria |
| PyPI / imágenes oficiales Docker | Dependencias descargadas para laboratorio | Metadatos de paquetes/imágenes; cadena de suministro | R08: fijación, avisos, hashes/digests y escaneo de imágenes | Reconstruir entorno compatible y volver a probar |

Responsabilidad compartida propuesta: proveedor opera plataforma/servicio contratado; titular del proyecto gestiona identidades, permisos, clasificación, configuración, secretos, acceso de red, retención, backups y pruebas según capacidades del plan. Verificar contrato para precisar fronteras, cifrado, copias y soporte; no asumir que servicio gestionado equivale a respaldo probado. El equipo mantiene dependencias, código y validación; la clínica aprueba datos, responsables y residual.

Terceros de soporte deben tener alcance, mínimo acceso, duración y revocación documentados. No hay pasarela externa verificada: el módulo de pagos registra métodos/importes internamente, no se inventa integración bancaria. No se añadieron SaaS, VPN o servicios cloud solo para cumplir una lista.

## Verificación remota posterior de solo lectura (E11)

El conector GitHub confirmó `main.protected=false`, protección deshabilitada y lista de rulesets vacía. No se cambió configuración. La corrida histórica [#55](https://github.com/julianhg21/gestor-clinica/actions/runs/38074840230), del commit base y fecha 10/10/2026, figura exitosa. Sus logs auténticos muestran 33 passed, 1 skipped y 5 deselected, ausencia de RAILWAY_STAGING_DEPLOY_HOOKS y omisión de pruebas post-deploy por STAGING_BASE_URL ausente. No demuestra despliegue efectivo ni valida el código nuevo local. Extractos sanitizados y pasos: `evidencias/devsecops/github-historico.json` (sin correos, firmas, tokens ni logs completos). C24 permanece parcial; C25 permanece propuesto porque el control de protección no está implementado. MFA y colaboradores no se verificaron.

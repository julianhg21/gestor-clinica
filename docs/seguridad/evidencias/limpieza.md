# Cierre del laboratorio

Después de guardar y verificar las evidencias se inspeccionó el contenedor
`duality-audit-postgres-20261023`: etiqueta `duality.audit=20261023` y red `none`.
Solo al coincidir ambos valores se ejecutó `docker rm -fv` sobre ese nombre
exacto; el comando terminó correctamente y retiró su volumen anónimo.
No se retiraron contenedores ni volúmenes existentes de la aplicación.

Los servidores HTTP temporales de 127.0.0.1:8765 (reportes) y 8766 (frontend
estático) fueron detenidos después de las capturas. Las previsualizaciones
temporales de las páginas del PDF preliminar se retiraron de tmp ignorado.
Los PDF fuente no se copiaron al repositorio.

La imagen local `duality-audit-auth:20261023` se conserva como artefacto de
construcción; no se publicó en ningún registro ni se desplegó. Para repetir
las pruebas SQL debe recrearse el laboratorio como indica el índice.

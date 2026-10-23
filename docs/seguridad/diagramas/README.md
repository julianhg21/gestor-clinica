# Diagramas UML con controles

Fuentes PlantUML de casos de uso, componentes, despliegue y secuencia de sesión. Asociaciones C/R/A se corresponden con las matrices; arquitectura existente ampliada en docs/ARCHITECTURE.md. No se ejecutó render PlantUML ni se presenta fuente como captura de sistema desplegado.

Casos de uso distingue lectura/escritura/administración; matriz-accesos.md precisa las 49 rutas. Componentes muestra Redis y consulta de identidad compartida por APIs. Despliegue representa puertos y HTTP locales existentes, no TLS/VLAN inventados. Secuencia refleja JWT, revocación, errores 401/403/503 y cuenta vigente; no constituye prueba de integración real.

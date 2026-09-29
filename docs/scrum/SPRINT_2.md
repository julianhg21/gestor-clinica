# Scrum — Sprint 2

**Sprint:** 2  
**Periodo de referencia:** 26–29 de septiembre de 2026  
**Objetivo:** implementar CI/CD, formalizar el plan de pruebas y mejorar la mantenibilidad y experiencia de uso del Gestor Clínica Duality.

## Sprint Backlog

| ID | Historia / tarea | Responsable principal | Estimación | Criterio de aceptación |
|---|---|---|---:|---|
| S2-01 | Diseñar pipeline CI/CD | Federico | 6 h | Checkout, build, test y deploy staging definidos |
| S2-02 | Implementar Jenkinsfile | Federico | 5 h | Jenkins reconoce el pipeline |
| S2-03 | Integrar Docker al build | Federico | 4 h | `docker compose build` exitoso |
| S2-04 | Generar reporte pytest HTML | Federico | 4 h | Artefacto HTML disponible |
| S2-05 | Incorporar Selenium | Federico | 4 h | Prueba UI ejecutable contra staging |
| S2-06 | Elaborar plan de pruebas | Carlos | 6 h | Objetivo, alcance, estrategia, parámetros y 15+ casos |
| S2-07 | Documentar Daily Scrum | Carlos | 3 h | Minutas con 3 preguntas por integrante |
| S2-08 | Registrar burn down | Carlos | 3 h | Horas restantes reales por día |
| S2-09 | Coordinar Sprint Review | Carlos | 2 h | Evidencia y resultado documentados |
| S2-10 | Coordinar Retrospectiva | Carlos | 2 h | Qué salió bien, mejorar y acciones |
| S2-11 | Mejorar CRUD de la aplicación | Julián / Federico | 7 h | Editar y anular/desactivar datos según reglas |
| S2-12 | Mejorar interfaz visual | Julián / Federico | 6 h | Login, navegación, tablas y responsive renovados |
| S2-13 | Preparar documento DEVOPS 2 | Julián | 7 h | Documento 12–18 páginas con evidencias reales |
| S2-14 | Preparar video #2 | Julián | 5 h | Video 8–10 min cubriendo CI/CD y pruebas |
| S2-15 | Validación final de entregables | Equipo | 3 h | Checklist completo antes de entrega |

## Daily Scrum

Registrar por cada reunión:

| Fecha | Integrante | ¿Qué hice desde el último Daily? | ¿Qué haré hoy? | ¿Tengo impedimentos? |
|---|---|---|---|---|
|  | Julián |  |  |  |
|  | Carlos |  |  |  |
|  | Federico |  |  |  |

> Completar con información real. No llenar retrospectivamente con datos inventados.

## Burn down

Registrar las horas restantes reales al cierre de cada día.

| Fecha | Horas planificadas restantes | Horas reales restantes |
|---|---:|---:|
| Inicio Sprint 2 | 67 |  |
| 26/09/2026 |  |  |
| 27/09/2026 |  |  |
| 28/09/2026 |  |  |
| 29/09/2026 | 0 |  |

Con estos valores puede generarse el gráfico Burn Down en Azure DevOps o en una hoja de cálculo.

## Sprint Review

### Demostración sugerida

1. Mostrar el objetivo del Sprint 2.
2. Abrir el `Jenkinsfile`.
3. Mostrar pipeline exitoso y una ejecución fallida real.
4. Abrir el reporte HTML de pytest.
5. Mostrar staging.
6. Probar edición y anulación de un registro.
7. Mostrar el nuevo diseño visual.
8. Revisar el plan de pruebas.

### Resultado

Completar después de la revisión:

- Historias aceptadas:
- Historias pendientes:
- Observaciones del Product Owner:
- Retroalimentación del docente:

## Retrospectiva

Completar con el equipo:

**Qué funcionó bien**
- 

**Qué debe mejorar**
- 

**Acciones concretas para el siguiente Sprint**
- 

## Definition of Done Sprint 2

Una tarea se considera terminada cuando:

- el código está en GitHub;
- compila;
- las pruebas automatizadas obligatorias pasan;
- no contiene secretos;
- la funcionalidad fue demostrada;
- la evidencia fue capturada;
- la documentación fue actualizada.

# Índice de la especificación revisada

**Gestión de horarios y francos · Windows offline · edición 1.1 sobre V1.0 · 25/11/2026**

Para decidir si el producto sirve al local, empezar por [la especificación funcional](01_PRODUCT_VISION.md), abrir [el prototipo con datos ficticios](prototipos/horarios.html) y revisar [las cuestiones que requieren al encargado](14_OPEN_QUESTIONS.md). Para implementar el primer incremento, comenzar por [AGENTS.md](../AGENTS.md) y [el encargo F1](17_HANDOFF_CODEX.md).

| N.º | Entregable solicitado | Archivo principal y referencias |
|---|---|---|
| 1 | Revisión crítica de V1.0 | [Contradicciones, factibilidad y resoluciones](15_CRITICAL_REVIEW.md) · [Normativa y encuadre pendiente](16_LABOR_REVIEW.md) |
| 2 | Especificación funcional y técnica definitiva de diseño | [Alcance, operaciones y criterio de publicación](01_PRODUCT_VISION.md) · [Reglas normativas del producto](02_REQUIREMENTS.md) · [Arquitectura](03_ARCHITECTURE.md) |
| 3 | Requisitos trazables con aceptación | [RF-01 a RF-28 y RNF-01 a RNF-07: requisito, tarea y prueba](02_REQUIREMENTS.md) |
| 4 | Arquitectura | [Módulos, contratos internos, selección de tecnologías y distribución](03_ARCHITECTURE.md) |
| 5 | Dominio y datos | [Entidades e identidades](04_DOMAIN_MODEL.md) · [Esquema SQLite y revisiones](05_DATA_MODEL.md) · [Modelo temporal y bordes](06_TIME_MODEL.md) |
| 6 | Algoritmo de optimización | [Modelo, objetivos, alternativas, reparación y diagnóstico](07_OPTIMIZATION_ENGINE.md) · [Política de equidad e historia](08_FAIRNESS_POLICY.md) |
| 7 | Contrato versionado del optimizador | [Protocolo 1.0 y mensajes de ejemplo](09_OPTIMIZER_CONTRACT.md) · [JSON Schema](contracts/optimizer-1.0.schema.json) |
| 8 | Diseño UX/UI | [Flujos, controles, mensajes y criterios accesibles](10_UX_UI.md) · [Prototipo HTML local](prototipos/horarios.html) |
| 9 | Persistencia e intercambio | [Transacciones y revisiones](05_DATA_MODEL.md) · [Configuración, PDF/PNG, respaldo y restauración](11_IMPORT_EXPORT.md) |
| 10 | Pruebas y escenarios | [T01–T40, oráculos y ensayos Windows](12_TESTING_STRATEGY.md) · [Microinstancias sintéticas](fixtures/microinstancias.json) |
| 11 | Backlog por dependencias | [B01–B18 y criterio de cierre](18_BACKLOG.md) |
| 12 | Decisiones y cuestiones abiertas | [ADR](decisions/ADR.md) · [Preguntas con responsable e hito](14_OPEN_QUESTIONS.md) · [Informe laboral](16_LABOR_REVIEW.md) |
| 13 | Instrucciones permanentes para Codex | [AGENTS.md](../AGENTS.md) |
| 14 | Plan incremental | [F0–F6, demo de cada fase y evidencia](13_IMPLEMENTATION_PLAN.md) · [Prompt para la primera entrega](17_HANDOFF_CODEX.md) |

### Cómo resolver diferencias al implementar

En cuestiones de negocio prevalece lo marcado **R**. Los archivos 04–09 precisan las decisiones temporales, matemáticas y de protocolo; 02 vincula el resultado observable con el backlog. Las marcas **D** son propuestas adoptadas para diseñar y **P** identifica conclusiones que aún necesitan evidencia. La simulación y los fixtures nunca fijan un valor del local. Si dos archivos prescriben comportamientos incompatibles, documentar el caso concreto y resolverlo antes de implementar la regla afectada.

### Estado verificable de esta entrega

Consultar [control de la edición](19_VERIFICACION_DEL_DISENO.md) para distinguir las comprobaciones ejecutadas sobre los documentos y sus ejemplos de las pruebas del producto que Codex deberá realizar. Las fuentes externas figuran en el documento que utiliza cada una; la aplicación proyectada funciona sin consultarlas.

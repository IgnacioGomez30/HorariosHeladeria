# Backlog con dependencias y resultado de aceptación

Una fila es una unidad revisable que puede dividirse en commits más pequeños. Todos los ensayos parten de perfiles sintéticos hasta el piloto. [Matriz de requisitos](02_REQUIREMENTS.md) · [Plan y puertas de salida](13_IMPLEMENTATION_PLAN.md).

| ID | Fase | Depende de | Entrega y criterio de cierre |
|---|---|---|---|
| B01 | F1 | F0 | Inspeccionar repo y dependencias. Entorno repetible, estructura de módulos y suite base; el comando documentado funciona en instalación limpia de desarrollo. |
| B02 | F1 | B01 | Intervalos, jornada con múltiples bloques, conversión local, minutos y descanso. Pasan T01–T05 y T07 para el dominio. |
| B03 | F1 | B02 | Vigencias, disponibilidad, calendario, patrones materializados y tipos de descanso. Pueden modelarse T06 y T08–T10; una regla ausente o ambigua queda identificada. |
| B04 | F2 | B03 | Esquema SQLite, migraciones y copia coherente previa; repositorios y datos de demo separados. Fallo en migración conserva base recuperable. |
| B05 | F2 | B03 | Validador independiente inicial, incluido calendario combinado, límites configurados y datos faltantes. Editar a mano nunca invoca el solver. |
| B06 | F2 | B04, B05 | Borrador, autoguardado, deshacer, bloqueos y confirmación con control de revisión. Tras reinicio se distingue vigente de borrador. |
| B07 | F2 | B06 | Primera semana Qt editable con foco accesible; crear persona, editar casilla y reabrir. Ensayo Windows temprano y registro del entorno. |
| B08 | F3 | B03, B05 | Implementar contrato 1.0 y constructor de captura, con versión, contexto e identificación de entrada. Pasan pruebas de conformidad, sustituibilidad y rechazo de datos inseguros/incompletos. |
| B09 | F3 | B08 | Selección CP-SAT de candidatos, bloqueos, horas, cobertura, descanso y propietarios. Propuesta revalidada coincide con oráculo pequeño; explicar un caso imposible. |
| B10 | F3 | B06, B09 | Ejecución fuera del hilo gráfico, presupuesto, cancelación y descarte por cambios de insumos. La UI sigue operativa ante caída. |
| B11 | F4 | B06, B09 | Historia efectiva, elegibilidad, mes de atribución, déficit y desempates. Distinguir ejemplo sin antecedentes del que arrastra deuda. |
| B12 | F4 | B10, B11 | Optimización por prioridades y diversidad de decisiones. Una solución única produce una opción; los indicadores se recalculan desde los bloques. |
| B13 | F4 | B10, B11 | Reparar ante solicitud o ausencia, minimizando cambios y mostrando diferencias. Nunca ampliar fechas automáticamente; botón de cancelar conserva original. |
| B14 | F5 | B07, B12, B13 | Completar los flujos de las cuatro áreas, teclado, estados, pin y consulta de versiones. Ensayar con el guion de [UX](10_UX_UI.md). |
| B15 | F5 | B04, B06 | Configuración JSON, previsualización, importación atómica, respaldos periódicos, restauración completa y fallo a mitad. Restaurar otra instalación de prueba y cotejar relaciones y revisión. |
| B16 | F5 | B06, B14 | Exportar semana confirmada a PDF/PNG; comprobar corte, nombres largos y medianoche con lectores externos offline. |
| B17 | F6 | B14–B16 | Lock de distribución, instalador Windows y guía breve incluida con recuperación. Probar instalación, actualización, desinstalación preservando datos y dependencias del worker. |
| B18 | F6 | B17 y cuestiones de operación aplicables resueltas | Ensayo desconectado con el encargado y horario habitual en paralelo; registrar tarea, errores, tiempos, ajustes y decisión de adopción. |

Ante un bloqueo técnico se puede continuar otra fila con todas sus dependencias resueltas. La falta de información individual afecta únicamente las verificaciones del piloto que la necesitan. No hay estimaciones de duración validadas para estas tareas.

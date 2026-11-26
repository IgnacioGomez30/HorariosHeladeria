# Requisitos trazables y criterios de aceptación

Los IDs RF y RNF conservan el significado de la V1.0. **R** proviene del solicitante; **D** es una elección de diseño; **R/D** conserva el resultado pedido y propone una forma específica de obtenerlo. Una condición particular pendiente nunca se completa con valores de los fixtures. Esta matriz es una especificación de pruebas futuras. Los oráculos documentales comprobados se identifican en [QA](12_TESTING_STRATEGY.md).

### Requisitos funcionales

| ID | Clase | Comportamiento y criterio observable | Tarea | Prueba fuente o comprobación complementaria |
|---|---|---|---|---|
| RF-01 | R | Dos personas con igual nombre conservan IDs, roles y calendarios distintos; tras la baja deja de asignarse trabajo nuevo y se puede consultar el anterior. | B03, B04, B14 | T09, T21; baja con revisión existente |
| RF-02 | R | A 12–16 y B 15–21 producen dos presencias entre 15–16; la edición y el motor aceptan la coincidencia. | B02, B05, B09 | T01 |
| RF-03 | R | Una jornada tiene uno o varios bloques coherentes. De 12–16 y 20–00 resultan 480 min. Un solape personal se identifica por persona y tramo; los extremos adyacentes no se solapan. | B02, B05 | T03, T04 |
| RF-04 | R | De lunes 19 a martes 01 se imputan 360 min al lunes; martes 18–00 conserva otros 360; median 17 h. El mismo criterio funciona a fin de semana, mes y año. | B02, B05 | T02, T05 |
| RF-05 | D | Mostrar fecha operativa y salida «(+1 día)» cuando corresponde. Fecha y hora de ambos extremos son inequívocas; inicio idéntico a fin del mismo día requiere corregir. | B02, B07 | T02, T05, T23 |
| RF-06 | R/D | Elegir jornadas fijas, variantes, ventanas y partidas autorizadas por vigencia. Horas fuera de la grilla generativa se conservan en manual si el patrón las autoriza; un objetivo flexible no actúa como límite. | B03, B05, B09 | T03, T04, T08 |
| RF-07 | R | En una semana completa ordinaria con un fijo y un rotativo se exigen dos fechas distintas. En semana parcial se usa contexto y en ausencia se aplica política específica. | B03, B05, B09 | T06, T14, T26 |
| RF-08 | D | Distinguir trabajo, fijo, rotativo, ausencia/licencia y sin asignar. Una solicitud civil de día libre impide también la cola nocturna del día anterior. | B03, B05, B14 | T06, T07, T19 |
| RF-09 | R | Precargar calendario offline por año/fecha y distinguir feriado, víspera, regla semanal y excepción. Dos reglas especiales incompatibles dejan visible el conflicto. | B03, B14, B15 | T10; dos especiales del mismo rango |
| RF-10 | R | Validar mínimo de empleados y mínimo total garantizado en cada tramo real; no aceptar ideal menor que el mínimo comparable. Informar fecha, hora y cantidad faltante. | B05, B09, B14 | T01, T11, T15 |
| RF-11 | R/D | Un eventual queda fuera del mínimo. Con apoyo solo consultable, mostrar condición pendiente. Registrar el compromiso, recomponer y validar antes de confirmar. Respetar límites del propietario. | B05, B09, B14 | T11, T15 |
| RF-12 | R | Registrar solicitud preferente o indisponibilidad, licencia o cambio vigente. Una preferencia puede quedar sin cumplir con explicación; una indisponibilidad confirmada bloquea los intervalos que toca. | B03, B05, B13, B14 | T04, T07, T17, T19 |
| RF-13 | R | Fijar jornada, franco, bloque o conjunto de fechas futuras. Una generación conserva exactamente lo fijado. Desbloqueo futuro explícito; pasado preservado. | B06, B09, B13 | T17, T19; patrón partido con un bloque fijado |
| RF-14 | R | Dos versiones adyacentes se aplican desde/hasta la fecha correcta; conflicto de vigencias incompatibles requiere resolución. Cambiar una regla marca el impacto futuro y conserva el confirmado anterior. | B03, B04, B06 | T09, T20 |
| RF-15 | R/D | Intentar dos fines de semana distintos por mes. Un sábado y domingo de la misma unidad cuentan una vez bajo la interpretación inicial; con capacidad escasa explicar el déficit. | B11, B12 | T12, T13, T26 |
| RF-16 | D | Comparar personas con oportunidades comparables, excluir fijo adicional del cálculo rotativo y contar secuencias que atraviesan semanas. Exponer alternancia con fechas concretas. | B05, B11 | T06, T13, T14 |
| RF-17 | R/D | Solo historial efectivo de confirmados/correcciones registradas con la política pertinente. Volver a resolver los mismos días no duplica el saldo; persona sin historia parte neutral. | B06, B11 | T13, T26; regenerar sobre dos revisiones de la misma semana |
| RF-18 | R/D | Generar sobre horizonte con contexto suficiente. Confirmar una semana recombina vecinos vigentes, no publica el resto provisional y evalúa cuotas y bordes. | B06, B08, B09 | T05, T14, T26 |
| RF-19 | R/D | Devolver de una a tres opciones válidas si se encuentran. Comparar diferencias visibles, cobertura y apoyo. Si solo hay una combinación útil, se ofrece una. | B10, B12, B14 | T16, T18 |
| RF-20 | R | Al reparar una ausencia, mantener pasado y bloqueos, minimizar personas/celdas afectadas y mostrar antes/después. Cancelar o rechazar mantiene el vigente. | B06, B13, B14 | T17, T20 |
| RF-21 | D | Distinguir solución verificada, inviabilidad probada del modelo evaluado, tiempo agotado, cancelación, entrada inválida y fallo del motor. Propuesta sin validación dura no puede confirmarse. | B05, B09, B10 | T15, T16, T19, T20 |
| RF-22 | R/D | Sustituir worker por doble conforme al contrato; con motor ausente se sigue editando/validando/confirmando manualmente y se puede exportar una revisión vigente. | B05, B08, B10, B17 | T24, T25 |
| RF-23 | R/D | Pantalla inicial semanal y otras tres áreas. Desde una casilla se edita, solicita o repara; vista diaria muestra coincidencias y mensual muestra francos. Realizar recorrido con teclado y estados escritos. | B07, B14 | T01, T07, T19, T21; recorrido de UX |
| RF-24 | D | Autosalvar borrador, confirmar de forma explícita y conservar revisión anterior. Una importación o elegir propuesta no publica. Exportación oficial remite a revisión concreta. | B06, B14, B16 | T09, T17, T19, T23 |
| RF-25 | R/D | Persistencia transaccional por instalación. Una actualización, interrupción o dos confirmaciones sobre la misma base dejan un único estado vigente verificable. | B04, B06 | T20, T22; dos ventanas/borradores obsoletos |
| RF-26 | R | Intercambio de configuración JSON con versión, referencias, previsualización y respaldo previo. Un archivo inválido no modifica el estado; una importación válida conserva historia. | B15 | T21, T22 |
| RF-27 | D | Copia coherente, retención local, recuperación tras migrar/importar y opción de guardar en medio elegido. Restaurar en almacén aislado recupera revisiones y relaciones. | B04, B15, B17 | T22, T25 |
| RF-28 | D | Exportar PDF y PNG de una revisión con fechas, bloques, homónimos distinguibles y `+1 día`. Sin motivos privados. Comprobar en papel y en teléfono. | B16 | T21, T23, T25 |

### Requisitos no funcionales y cierre de riesgos

| ID | Condición exigida | Tarea | Prueba / evidencia |
|---|---|---|---|
| RNF-01 | Con red deshabilitada en Windows limpio se instala, arranca, consulta, confirma y exporta; generación funciona con las dependencias instaladas. Sin cuentas o telemetría. | B10, B17 | T25 y repetición con motor disponible |
| RNF-02 | La UI permanece interactiva; cancelar no bloquea ni publica, el límite de tiempo produce un estado honesto. Se miden latencias con tamaños, equipo y opciones registrados. | B10, B12 | T16, T20 y cronometraje |
| RNF-03 | Con caída, disco sin espacio, migración o importación fallida se recupera el estado previo o el último commit completo, con diagnóstico. | B04, B06, B15 | T20, T22 |
| RNF-04 | Repetir bajo configuración controlada permite comprobar invariantes y vectores de objetivo; conservar versión, opciones y entrada. Una corrida paralela no exige idénticos bytes. | B01, B08, B12 | T18, T24 y oráculo de enumeración |
| RNF-05 | Completar el recorrido por teclado, distinguir foco y estados sin color, usar 24 h y entender qué fecha cambia. Verificar con el encargado. | B07, B14, B18 | T19, T23 y guion de usabilidad |
| RNF-06 | Instalador Windows incluye runtime, zona y worker; actualización preserva datos. Una guía breve permite restaurar sin consola. | B17, B18 | T22, T25 en máquina limpia |
| RNF-07 | Datos reales permanecen en almacén local, exportación pública mínima, importadores validan datos pasivos y logs prescinden de nombres/motivos. | B04, B08, B15, B16 | T22, T23; inspección de binarios, logs y archivos |

**Regla de salida transversal.** Una regla obligatoria aplicable desconocida o sin capacidad de evaluación produce «Falta verificar» para el rango afectado. El encargado conserva el borrador y el horario vigente. Debe probarse tanto en el camino manual como en el automático. Ver [registro de pendientes](14_OPEN_QUESTIONS.md), [estrategia de pruebas y escenarios adicionales](12_TESTING_STRATEGY.md) y [backlog](18_BACKLOG.md).

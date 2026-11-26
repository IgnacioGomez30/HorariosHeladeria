# Especificación funcional y técnica del producto

Edición 1.1. Fuente primaria: V1.0 §§1–10 y pedido de revisión. **R** indica condición confirmada por el solicitante, **D** una decisión de diseño adoptada para construir, **P** un dato o interpretación por validar. Una D es revisable mediante una decisión registrada. Las opciones sintéticas sirven exclusivamente para probar.

## Un turno de uso

El encargado abre **Horarios** en la semana actual, avanza a la próxima y ve si ya tiene versión confirmada. Carga una solicitud desde la casilla de la persona, arma un borrador a mano o pide propuestas. Al elegir una, lee los cambios concretos, revisa los huecos del día y confirma el período elegido. Puede imprimirlo o guardar una imagen. Si alguien avisa que falta, abre «Resolver cambio» sobre esa misma revisión. Hasta que acepta el reemplazo, se puede identificar qué versión comunicó originalmente.

## Contrato de producto

| Tema | Decisión para V1 | Estado |
|---|---|---|
| Finalidad y entorno | Una heladería, un responsable local a la vez, escritorio Windows, español de Argentina, 24 h y semanas lunes–domingo. Instalación y uso final con red desconectada. | R para alcance y uso offline; D para plataforma y presentación |
| Plantel | Identidad estable y nombre visible distinguible. Hay cuatro empleados y dos propietarios, dos personas homónimas. Alta, baja y cambio de reglas con fecha. | R |
| Jornadas | Cualquier combinación autorizada de jornada continua, partida, variable o nocturna. Cada jornada tiene fecha operativa propia; otros empleados pueden coincidir. Conservar minutos exactos de la edición manual. | R |
| Francos | El franco fijo semanal de una persona es adicional al rotativo. Los otros tres empleados tienen un franco rotativo según V1. Las licencias y las ausencias llevan su propia causa operativa. | R; P para semanas especiales |
| Patrón habitual | La fuente describe un cierre habitual y extensiones, una jornada habitualmente partida y otra de duraciones variables; hay al menos una ficha sin duración informada. Son antecedentes para la entrevista. | P para fijar horas y límites efectivos |
| Cobertura | Requisito por tramo real. El mínimo es obligatorio; el ideal guía la comparación. Se distinguen mínimo de empleados y mínimo total. Un propietario eventual queda fuera del mínimo. | R; P para cifras y compromisos reales |
| Equidad | Intentar dos fines de semana distintos por mes, contemplando lo ya confirmado y alternancia entre semana. Explicar a quién le toca una oportunidad cuando escasea. | R para meta flexible; P para definición local |
| Control | Confirmación humana, bloqueos explícitos, revisiones recuperables, cambios de reglas con efecto temporal, generación y reparación por separado. | R |
| Herramientas | Semana, día con presencia, mes de francos, Personal, Solicitudes y Configuración. PDF/PNG del calendario, JSON de configuración y copia completa para recuperación. | R para operaciones; D para formatos |
| Límites | Se excluyen ventas, pagos, fichaje, nómina, mensajería automática, cuentas remotas, sucursales y gestión multiusuario. | R |

## Operaciones y permisos de la persona encargada

| Acción | Condición para iniciarla | Resultado y efecto |
|---|---|---|
| Empezar en una PC nueva | Elegir local vacío o demostración separada | La semana abre vacía; un asistente conduce a apertura, personal, descansos y mínimos. Siempre se puede volver a un borrador. |
| Editar / deshacer | Elegir persona, día y tipo | Guarda borrador; calcula minutos de bloques y muestra conflictos localizados. Deshacer pertenece al borrador. Un cambio sobre un confirmado comienza una revisión derivada. |
| Pedir horarios | Insumos del alcance completos, reglas verificadas para uso real, contexto suficiente y motor disponible | Congela la entrada, busca en segundo plano; devuelve hasta tres opciones válidas o un motivo específico. Una propuesta seleccionada sigue siendo borrador. |
| Confirmar | Revisión vigente, rango explícito, validación completa y apoyos garantizados | Muestra fechas y diferencias. Una transacción crea una revisión. Si falla alguna condición, conserva el borrador y la revisión vigente. Mismo control para cambios manuales. |
| Registrar imprevisto | Persona y intervalo, solicitud preferente o indisponibilidad confirmada | Marca el conflicto en las fechas afectadas, incluso de madrugada. Resolver abre una reparación del rango autorizado. El responsable ve quién cambia y qué se conserva. |
| Corregir un horario comunicado | Revisión elegida y fechas futuras | Previsualización y nueva confirmación explícita. Los antecedentes del arranque se identifican por su procedencia. Una revisión sustituida sigue disponible como fue confirmada; el circuito de reparación solo modifica bloques futuros autorizados. El producto registra planificación. |
| Recuperar | Selección de revisión para consultar o de respaldo para restaurar | Consultar es lectura. Reutilizar fechas futuras de una revisión genera borrador y revalidación actual. Restaurar toda la base es otra operación y requiere copia previa. |
| Compartir | Revisión confirmada y período | PDF/PNG local con fecha y revisión; el responsable elige el medio. La operación de exportar no acredita que el equipo haya sido notificado. |

## Alcance de la validación

La configuración se comprueba para la persona, franja y vigencia afectadas. La ausencia de una cobertura posterior en un feriado no impide consultar marzo pasado. Una regla importante sin decidir queda visible como **Falta definir**. Una casilla vacía en una semana activa requiere una decisión expresa antes de confirmar si se necesita para evaluar trabajo, francos o cobertura. Un cierre del local no acredita por sí solo un franco individual.

El modo demostración usa otro almacén y permite ensayar la secuencia completa con reglas ficticias. En producción, el usuario puede registrar y corregir borradores mientras completa las reglas. El validador distingue *incumple*, *faltan datos* y *cumple dentro del alcance evaluado*. La aplicación no certifica cumplimiento jurídico. Ver [perfil laboral](16_LABOR_REVIEW.md) y [cuestiones pendientes](14_OPEN_QUESTIONS.md).

## Decisión de salida a uso real

Una semana piloto debe poder reproducirse desde sus insumos, inspeccionarse día por día, recuperarse tras cerrar y mostrarse en papel/teléfono. Para pasar a uso real se requieren reglas particulares revisadas, prueba de restauración y recorrido del encargado en la PC objetivo. Un tiempo de cálculo aceptable y una explicación entendida se miden en el piloto. [Criterios verificables](02_REQUIREMENTS.md) · [Plan incremental](13_IMPLEMENTATION_PLAN.md)

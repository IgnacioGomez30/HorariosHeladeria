# UX de escritorio · Horarios de la heladería

[Índice](00_INDEX.md) · [Prototipo navegable sin conexión](prototipos/horarios.html) · [Modelo temporal](06_TIME_MODEL.md) · [Importación y recuperación](11_IMPORT_EXPORT.md)

## Qué se puede probar hoy

Extraé el paquete y abrí `docs/prototipos/horarios.html` con Edge, Firefox o Chrome. La maqueta muestra una semana ficticia del **1 al 7 de abril de 2030**. Las personas, reglas, revisiones y resultados son de demostración. Los recorridos usan pantallas enlazadas y simulaciones locales. Las acciones de archivos se detienen en la previsualización. Recargar reinicia la sesión. La maqueta sirve para decidir si se entiende la tarea antes de programar la aplicación PySide6.

**Recorridos sugeridos**

1. En **Semana**, buscá cómo trabaja Alma el lunes. En **Día**, comprobá quién cubre su intervalo entre bloques y de qué fecha proviene la presencia después de medianoche.
2. En **Mes**, seleccioná a Alma y diferenciá su franco fijo del martes, su rotativo del domingo y las semanas aún sin cargar.
3. En **Personal**, abrí la jornada partida de Alma. Superponé dos bloques y tratá de revisar el cambio. Corregí la hora y revisá el total.
4. Desde **Generar horarios**, compará las dos distribuciones ficticias, llevá una a borrador y revisá el paso de confirmación. Probá también la salida «Se agotó el tiempo».
5. Desde **Resolver un cambio**, seguí la ausencia de Bruno el jueves. Compará las dos personas afectadas, cancelá y verificá qué revisión sigue vigente. Repetí y confirmá el ejemplo.
6. Desde **Configuración → Archivos y copias**, compará qué se recupera con una copia y qué se comparte con un PDF. Probá una importación con una referencia desconocida.

## Decisiones de interacción

| Condición | Conducta requerida |
|---|---|
| Abrir la aplicación | Mostrar **Horarios**, semana actual local, selección en hoy. Si hay un borrador recuperado, ofrecer retomarlo con fecha de último guardado. Mantener a la vista qué versión se está consultando. |
| Primera vez | «Cargar mi local» crea un espacio vacío con campos faltantes visibles. «Ver un ejemplo» usa datos separados y una franja persistente «Demostración». Al salir se vuelve al espacio de origen. |
| Contexto estable | Cuatro destinos principales: Horarios, Personal, Solicitudes, Configuración. Semana, Día y Mes conservan la fecha y la persona seleccionadas cuando tienen correspondencia. Al salir de un editor, el foco vuelve a su celda. |
| Persona repetida | Nombre y rol visibles. Si coinciden ambos, mostrar el alias elegido por el responsable o un identificador breve estable que distinga a cada persona en pantalla y en la exportación. La selección interna usa ID estable. |
| Trabajo frecuente | Acciones principales según estado. Semana confirmada: generar, crear revisión o resolver un cambio. Borrador completo: revisar y confirmar. Bloqueo, deshacer, historial y exportación quedan cerca del objeto al que afectan. |
| Estados | «Borrador», «Borrador con pendientes», «Confirmado · revisión N» y «Revisión anterior». Una propuesta sigue separada del borrador hasta que la persona la elige. Abrir, previsualizar y exportar son acciones de lectura. |
| Trabajo con un dato faltante | El aviso identifica persona o regla, fecha y acción para corregir. El responsable puede avanzar con un borrador manual y regresar al punto pendiente. Una confirmación requiere una validación completa. |
| Escritura y recuperación | Al guardar, informar «Borrador guardado a las 17:42» solo tras la transacción. Ante fallo: «No se pudo guardar. El cambio sigue abierto. Reintentá o guardá una copia donde tengas permiso». No cerrar como guardado. |
| Segundo plano | Durante la búsqueda se puede consultar el calendario y cancelar. Si cambia una entrada, el resultado se marca vencido y se ofrece recalcular con los cambios. Evitar porcentaje ficticio y mantener disponible la edición manual. |
| Bloqueo y tiempo | «Fijar» protege el contenido durante la generación. «Desfijar» en jornada futura exige confirmar alcance y detalle. Un horario confirmado requiere una revisión nueva; un cerrojo y la confirmación tienen efectos distintos. |

## Flujos por tarea

Las decisiones de distribución de controles, textos y pasos son propuestas de diseño. Los comportamientos de dominio se rigen por los requisitos y su validador. Los ejemplos numéricos de esta sección son sintéticos.

| Flujo y entrada | Primer plano | Pasos y resultado observable | Excepción o salida |
|---|---|---|---|
| 1. Pantalla principal · abrir | Semana, fecha, estado, cuatro áreas | Elegir período con Anterior/Hoy/Siguiente; al volver a Horarios, recuperar selección. En instalación vacía, ofrecer «Agregar personal» y «Abrir borrador». | Una semana vacía muestra «Sin asignar» o falta de configuración, nunca francos inventados. Un fallo del motor deja accesibles las vistas, la edición y la exportación de confirmados. |
| 2. Vista semanal · elegir celda | Personas × lunes–domingo; propietarios agrupados; nombre y rol; cada bloque en su línea. | Enter o clic abre la ficha de persona y fecha. Elegir trabajar, franco fijo/rotativo, ausencia o pendiente, según elegibilidad; editar horas; aplicar al borrador; mostrar anomalías y acción Deshacer. Fijar una celda o un bloque explícito. | Si ya está confirmado, ofrecer «Crear revisión» indicando base. Dos personas pueden trabajar juntas. Solapamiento dentro de una persona resalta ambos intervalos y bloquea la confirmación hasta corregir. |
| 3. Vista diaria · abrir Día | Línea temporal por persona, una banda por bloque, eje de horas y fecha en el cambio de día. Debajo, tabla equivalente navegable. | Comparar bandas concurrentes; seleccionar una franja para ver presentes, cantidad de empleados, propietarios comprometidos, mínimo e ideal. Para una fecha civil incluir la cola anterior; al mirar un cierre operativo mostrar su cola con fecha real. | Diferenciar «Falta 1 para el mínimo», «Mínimo cubierto; falta 1 para el ideal», «Sin regla cargada» y «Local cerrado». Ningún refuerzo eventual suma al mínimo. Un hueco de jornada partida queda vacío. |
| 4. Vista mensual · Mes | Calendario lunes–domingo; selector de persona; días rotulados. | Distinguir franco fijo, rotativo, ausencia, trabajo y pendientes; abrir el día. Explicar qué sábados/domingos se contaron para esa persona y mes y cuándo un cierre cae en otra fecha. | Una semana que cruza meses conserva su semana de referencia. Dos francos del mismo fin de semana se agrupan según política; mostrar «Sin historial anterior» si corresponde. |
| 5. Configurar personal · Personal | Nombre visible, rol, alta, vigencia, jornada habitual, francos. | Editar ficha, revisar «Desde el…» y guardar nueva versión. Opciones avanzadas: ventanas, objetivo/mín./máx., patrones y participación. Jefe: distinguir compromiso fechado (tramo exacto o ventana con límites acordados), disponible para consultar y eventual. | Desactivar con fecha conserva historial. Si dos reglas de igual prioridad se contradicen, mostrar ambas y la fecha de inicio del conflicto. Un campo desconocido queda «Por definir». |
| 6. Configurar jornada partida · Personal → Jornadas | Dos filas con día/inicio y día/fin, duración trabajada total y pausa. | Agregar o quitar bloques, marcar «día siguiente» explícitamente, revisar suma y huecos; guardar patrón autorizado con fecha de vigencia. Editar una sola celda es otra acción. | Fin igual a inicio en misma fecha pide corrección. En superposición, explicar qué bloque corregir. Hora manual exacta se conserva independientemente del paso del generador. |
| 7. Solicitudes y excepciones · Solicitudes / celda | Persona, tipo, fecha y, si corresponde, horas reales. | Distinguir «Preferiría librar» de «No puede trabajar»; «Franco operativo» de «Día completo sin presencia»; revisar fecha, alcance y obligación. Guardar, marcar período afectado y ofrecer reparar. Motivo genérico opcional. | Licencia y ausencia tienen etiqueta propia. Si ya existía jornada que termina a la 01:00, señalar la hora incompatible con un día civil libre. La solicitud guardada y la reparación son dos operaciones separadas. |
| 8. Generar y elegir · Generar horarios | Período visible y próxima acción. Opciones técnicas ocultas. | Verificar configuración y contexto, buscar, comparar hasta tres opciones distintas por días de franco, huecos de ideal y minutos de apoyo. Seleccionar, revisar semana, guardar como borrador, validar y confirmar. Asociar revisión y fecha. | Mostrar las alternativas encontradas, incluso una sola. El apoyo hipotético se muestra por separado como diagnóstico. Permite registrar un compromiso, recalcular y volver a validar. Cancelación, tiempo agotado e inviabilidad tienen mensajes distintos. |
| 9. Reparar · Resolver un cambio | Solicitud, revisión de origen y período editable. | Elegir alcance, revisar comparación por persona y fecha, mostrar cambios obligados y cambios para cubrirlos, bloqueos respetados y períodos ajenos. Aceptar la revisión nueva mediante un paso explícito. | Cancelar conserva confirmado y solicitud ya registrada. Si falla, indicar franja y regla. Para ampliar el período o desfijar pedir una decisión específica; jamás hacerlo automáticamente. |
| 10. Configuración general · Configuración | Horarios del local, cobertura por franja, feriados/excepciones, francos y descanso; entrada a archivos. | Copiar plantilla entre días con vista previa; editar «desde/hasta»; mostrar regla efectiva y origen para una fecha; detectar empates incompatibles; revisar impacto en borradores y confirmados futuros. | Feriados introducidos localmente, con fecha y año. Perfil laboral sin verificar: mostrar el dato preciso pendiente y bloquear acciones productivas que dependen de él. |
| 11. Archivos · Horarios → Exportar / Configuración → Archivos y copias | Elegir por intención: «Compartir horario», «Llevar configuración», «Recuperar todo». | PDF/PNG: período y revisión → previsualizar → guardar. Configuración JSON: leer → validar → previsualizar diferencias y vigencias → copia previa → aplicar todo. Copia completa: elegir destino → crear/verificar. Restaurar: validar copia → mostrar revisiones/fechas que se sustituirán → guardar estado previo → restaurar. | Con archivo incompatible, copia incompleta, destino sin espacio o cancelación, mostrar resultado exacto, preservar datos vigentes, volver al selector. Ofrecer «Abrir carpeta» tras escritura exitosa. |

## Qué ve el responsable al resolver problemas

| Situación | Microtexto propuesto | Acción primaria |
|---|---|---|
| Jornada que cruza medianoche | «Lunes 19:00 – martes 01:00 (+1 día). Seis horas del lunes. Presente el martes de 00:00 a 01:00». | Ver el día |
| Días fijos y rotativos | «El martes ya es su franco fijo. Elegí otro día para su franco rotativo». | Elegir fecha |
| Compromiso faltante | «Jueves 18:00–19:00 necesita una persona. Leo figura como disponible. ¿Confirmó ese horario?» | Registrar compromiso y volver a validar |
| Tiempo agotado con cero resultados | «Terminó el tiempo de búsqueda. Todavía no encontramos un horario». | Reintentar / editar a mano |
| Inviabilidad demostrada | «El jueves de 16:00 a 18:00 se necesita una persona. Ninguna de las personas habilitadas puede cubrir esa franja». Mostrar esta causa solo si se demostró ese dato. | Revisar disponibilidad |
| Bloqueo enfrentado con ausencia | «El bloque de Bruno del jueves está fijado y coincide con su ausencia». | Ver bloque y solicitud |
| Borrador desactualizado | «Cambió la disponibilidad desde que se preparó esta propuesta». | Revisar con los datos actuales |
| Revisión anterior | «Esta semana tiene una revisión más reciente». | Ver revisión vigente |
| Fallo en respaldo previo | «La copia previa no terminó. Elegí otro destino y reintentá la importación». | Elegir destino |

## Accesibilidad y exportación

- Usar controles Qt estándar cuando permitan la tarea. Para celdas personalizadas, exponer rol, nombre, valor, estado, acción, orden y cambios al lector. Ejemplo de nombre accesible: «Alma, lunes 1, dos bloques, 12 a 16 y 18 a 20, seis horas». Dar a la línea de tiempo una tabla equivalente con los mismos límites y cantidades. [Qt, Accessibility](https://doc.qt.io/qt-6/accessible.html)
- Tab recorre secciones; las flechas recorren la cuadrícula en la aplicación; Enter abre y Esc vuelve. Ofrecer controles visibles para esas acciones. No exigir arrastre ni doble clic. Mover foco al primer error al revisar y devolverlo al control de origen al cancelar. Mostrar el error también junto al campo y conservar lo escrito.
- Objetivo visual propuesto: contraste de texto normal ≥4,5:1 y texto grande ≥3:1. Junto a todo color indicar «Fijo», «Rotativo», «Ausencia», «Sin asignar» o «Cierre +1 día». Respetar fuentes y escala del sistema. Usar estas referencias como criterios medibles de diseño; comprobar la GUI empaquetada con Narrador, alto contraste y escalado de Windows. [W3C, contraste](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) · [W3C, uso de color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
- A escala 150–200 %, mantener controles visibles, permitir desplazamiento del contenido y conservar encabezados identificables. Para lectura en celular, evaluar PNG por días si la semana completa obliga a reducir demasiado la letra. La previsualización representa exactamente páginas o imágenes a guardar. Mostrar el nombre distinguible y el cruce nocturno completos. PDF y PNG omiten solicitudes privadas. Impresión legible en escala de grises.
- Propuesta para V1: exportación compartible solo desde la revisión confirmada elegida. Un borrador guarda los cambios locales; «Compartir» enlaza a «Revisar y confirmar» cuando faltan pasos. La acción «Guardar archivo» termina localmente; compartir por otro medio corresponde al responsable.

## Prueba con el responsable

Hacerla primero con la maqueta extraída y después con la versión candidata en Windows. Pedir que piense en voz alta sin guiar los clics. Registrar tarea, punto donde dudó, intentos, intervención necesaria y si interpretó bien el resultado. Los criterios de salida son propuestas de evaluación, todavía pendientes de prueba con usuarios.

| Tarea observada | Señal de éxito |
|---|---|
| Encontrar una superposición y la pausa de Alma | Ubica a Alma y Bruno juntos de 15:00 a 16:00 del lunes y lee que Alma vuelve a las 18:00. |
| Mover un franco y distinguir los dos tipos | Conserva el fijo, elige otra fecha para el rotativo y sabe si está mirando un borrador. |
| Comprender una madrugada | Señala el lunes como jornada y el martes como fecha de presencia física en el cierre de Celia. |
| Reparar y cancelar | Identifica la ausencia, las personas afectadas y la versión que sigue vigente al cancelar. |
| Compartir vs. recuperar | Elige PDF/PNG para comunicar y copia completa para restaurar, y reconoce qué información saldría del equipo. |
| Resolver con teclado | Completa una edición, localiza un error, vuelve a la celda y puede leer la franja sin usar mouse ni color. |

Registrar dificultades y repetir tras corregirlas. El prototipo no acredita la usabilidad del instalador, la accesibilidad de PySide6 ni las propiedades matemáticas del motor.

## Verificación realizada sobre la maqueta

Se abrió el HTML mediante archivo local con Qt WebEngine en Linux. Se recorrieron 117 enlaces internos distintos, incluidos los detalles por persona y fecha. Se verificaron los cambios visibles al elegir propuesta, confirmar una revisión, cancelar la reparación, confirmar la reparación, volver a una revisión anterior, corregir bloques superpuestos y previsualizar una importación inválida. La vista diaria mostró la presencia de Bruno y Alma y la cola nocturna de Celia. En esa ejecución no se observaron recursos HTTP/HTTPS cargados. Se inspeccionaron visualmente Semana y Día a 1366 × 768. Quedan pendientes las pruebas en Windows, con tecnología asistiva y con el responsable del local.

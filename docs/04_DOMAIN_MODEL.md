# 04 · Modelo de dominio

La unidad que edita el responsable es la casilla de **una persona en una fecha operativa**. La unidad que cubre un intervalo es **una persona físicamente presente**. Una casilla puede aportar presencia a dos fechas civiles. Las reglas que autorizan ese trabajo tienen su propia vigencia.

## Identidades y relaciones

| Objeto | Identidad y relaciones | Invariantes |
|---|---|---|
| Persona | ID opaco estable generado localmente. Cada versión de su ficha conserva nombre visible, rol y fechas de actividad. | Dos personas pueden llamarse igual. Mostrar un distintivo comprensible (p. ej. «Vera · empleada», «Vera · jefa»). Si coinciden también los roles, pedir una etiqueta local. La baja tiene fecha y conserva el pasado. |
| Regla | Familia, alcance, unidad y clase (obligatoria o preferencia), versión y vigencia. Incluye disponibilidad recurrente, límites, cuotas y política de equidad. | Una preferencia produce un costo explicable. Un límite obligatorio necesita un comprobador independiente para poder publicar. Un dato laboral pendiente conserva ese estado. |
| Patrón de jornada | Identidad lógica y versión, aplicabilidad por persona/día, uno o más bloques autorizados con ancla local o relativa y desplazamiento de fecha. Puede definir ventanas acotadas. | El patrón describe alternativas, no crea horas trabajadas. La instancia elegida fija exactamente cada inicio y fin. Las ventanas no se combinan libremente si corresponden a variantes excluyentes. |
| Día del local | Proyección de fecha operativa y calendario efectivo. Apertura al público, intervalos con tareas autorizadas y requisitos de cobertura son conceptos distintos. | «Cerrado» es una decisión explícita. Un día sin parámetros es desconocido. La franja puede prolongarse hasta el siguiente día civil. |
| Casilla | Par (persona, fecha operativa) en una versión del calendario. Contiene estado, bloques si corresponde, origen y relación con patrón/regla autorizante. | Como máximo una casilla efectiva por clave. Las versiones de una misma casilla no se suman entre sí. Una edición ad hoc debe satisfacer las reglas o apoyarse en una excepción autorizada. |
| Jornada y bloque | Jornada de trabajo de esa casilla, compuesta por bloques reales ordenados. | Al menos un bloque positivo. Los intervalos pertenecen a la misma persona. Pausas fuera de los bloques; ver [modelo temporal](06_TIME_MODEL.md). |
| Solicitud/excepción | ID, persona, alcance, clase, prioridad, estado y vigencia. Una restricción física lleva intervalo real; una preferencia por un franco puede llevar fecha operativa. | Una solicitud pendiente no es una licencia aprobada. Al aceptarla se registra el efecto preciso; «día calendario completo» cubre también la madrugada. Motivo genérico opcional en la aplicación, fuera de los intercambios con el motor. |
| Compromiso de propietario | Persona e intervalo comprometido, origen y versión de aprobación. Un bloque candidato puede necesitar varios compromisos o quedar parcialmente cubierto. | Solo cuentan los tramos efectivamente comprometidos y asignados. Una presencia ya pactada como obligatoria debe mantenerse aunque nunca ayude a alcanzar el mínimo. La disponibilidad sin compromiso solo habilita explorar alternativas. |
| Fijación | Clave de persona/día y estado o conjunto de bloques exactos que debe preservarse. Un grupo de fechas se expande en fijaciones explícitas. | Una fijación de bloque obliga a conservar sus extremos; puede haber otros bloques compatibles autorizados. Una fijación de jornada preserva también el estado y la composición completa. |
| Revisión, borrador y ejecución | Una revisión identifica la planificación publicada; un borrador parte de una revisión y una configuración concretas. Una ejecución vincula instantánea de entrada y propuestas. | El motor no edita confirmados. Se conserva el origen manual o automático. Reproducir la entrada es posible sin prometer la misma respuesta ante otros binarios o límites de tiempo. |

## Estados de una casilla

| Estado | Bloques físicos | Cómputo y presentación |
|---|---:|---|
| Trabajo | 1 o más | Suma de minutos efectivos. La jornada partida ocupa una sola casilla. |
| Franco fijo | 0 | Cuenta exclusivamente para el cupo fijo correspondiente. |
| Franco rotativo | 0 | Cuenta para el cupo rotativo y, si es elegible, para equidad. La solicitud de un franco confirmado debe especificar de cuál se trata. |
| Ausencia/licencia | 0 | No descuenta un franco automáticamente. Una indisponibilidad parcial se guarda como intervalo y puede coexistir con trabajo fuera de él. |
| Sin asignar | 0 | Para un propietario sin compromiso puede ser resultado definitivo; para un empleado pendiente es una edición incompleta. Una fecha cerrada sin jornada que no deba contar como franco requiere una política explícita de elegibilidad/cierre. |
| Fuera de actividad | — | Se deriva de las fechas de actividad. No se fabrica una casilla de franco. |

Una celda inexistente fuera del calendario confirmado significa **dato desconocido**. En la vista semanal se debe distinguir una fecha no publicada de un franco. El estado del **día físico** se deriva de sus intervalos y no se escribe en la casilla para «corregir» la fecha operativa.

## Agregación y vigencias

1. La persona y la regla conservan identidad estable. Un cambio de contenido crea una versión. Una revisión de configuración contiene la línea de tiempo completa conocida al guardarla; las publicaciones antiguas conservan la revisión y las versiones con que se evaluaron.
2. Las reglas por fecha operativa se aplican con inicio incluido y fin excluido. Para una misma clave y nivel, dos versiones incompatibles con vigencias superpuestas requieren resolución. Para valores sustituibles del calendario usar fecha concreta, especial y semanal, de mayor a menor prioridad. Dos especiales aplicables al mismo atributo con cierres diferentes requieren una prioridad explícita o una excepción fechada. Se muestra el origen del valor efectivo.
3. Los pisos, topes, prohibiciones y compromisos obligatorios de diferentes clases se intersectan. Una excepción personal que habilita un patrón distinto no levanta un descanso obligatorio. Una obligación aprobada y una indisponibilidad posterior en el mismo intervalo generan un conflicto comprobable.
4. Cada política declara su base temporal: fecha operativa, intervalo físico, semana/ventana o fin de semana anclado. Para cuotas semanales buscar la política del ciclo completo. En un cambio a mitad de semana solicitar una regla transitoria explícita con el cupo de esa semana o una vigencia desde el próximo lunes. No sumar los dos cupos semanales completos ni prorratear por costumbre. El cambio de patrón diario puede entrar en vigor cualquier fecha.
5. Ante una ausencia de semana completa o un alta/baja parcial, la regla aprobada determina participación y cuota del ciclo. Si todavía falta, permitir configurar y ensayar con datos ficticios; mostrar que falta antes de confirmar una planificación real dependiente de esa regla. Conservar el motivo de exclusión de una oportunidad como categoría general, sin texto sensible.
6. Una edición del calendario o de reglas invalida propuestas vinculadas a la versión anterior y marca para revisión los borradores afectados. Si una publicación futura entra en conflicto, sigue siendo la publicación vigente hasta que una persona apruebe una reparación.

## Publicación y corrección

El calendario confirmado tiene una única **cabeza** que señala su revisión vigente. «Histórico» es una vista de revisiones confirmadas anteriores. Solo una confirmación humana crea la siguiente revisión. Una propuesta validada pasa primero a borrador editable; un resultado que depende del compromiso de un propietario se muestra por separado como condicional. Registrar el compromiso explícito cambia los insumos y exige una nueva validación.

La publicación toma el subconjunto de fechas autorizado, lo une con la cabeza actual y verifica la transición en una sola transacción. Fuera del subconjunto conserva las casillas anteriores. El pasado y los bloques iniciados quedan fijos; para una jornada partida en curso el responsable puede autorizar reparar solo los bloques futuros, conservando exactamente los ya iniciados. Si no existe patrón o excepción compatible, mostrar la incompatibilidad. Ante un cambio de cabeza, pedir comparar la versión actual. Reutilizar un horario anterior genera un nuevo borrador y el mismo circuito de validación; para consultar basta abrir la revisión original.

**Ejemplo sintético.** En la revisión 7, A tiene franco rotativo el sábado. En una reparación autorizada pasa al domingo y se crea la revisión 8. La consulta de la 7 sigue mostrando sábado. El historial usado para planificar desde la revisión 8 computa solo el día vigente de ese fin de semana. El borrador que consideró ambos días nunca fue evidencia de dos francos.

[Índice](00_INDEX.md) · [Modelo de datos](05_DATA_MODEL.md) · [Equidad](08_FAIRNESS_POLICY.md) · [Contrato del motor](09_OPTIMIZER_CONTRACT.md)

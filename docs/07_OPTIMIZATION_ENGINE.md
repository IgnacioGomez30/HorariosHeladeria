# Motor de planificación

**Alcance.** Diseño de referencia para RF-02 a RF-22. La unidad que elige el motor es la jornada de una persona en una fecha operativa. La unidad que necesita el local es una persona presente durante un intervalo real. Vincular ambas evita que una jornada partida cubra el hueco entre sus bloques. La salida es una propuesta que el responsable puede revisar.

Los parámetros, umbrales y prioridades indicados como propuesta se pueden probar con datos sintéticos. La activación de reglas de trabajo reales exige resolver los datos del local y el régimen aplicable. Ver [modelo temporal](06_TIME_MODEL.md), [equidad](08_FAIRNESS_POLICY.md) y [contrato del motor](09_OPTIMIZER_CONTRACT.md).

## Elección del método

| Método | Aplicación y límite para este caso |
|---|---|
| Construcción voraz por persona/día | Sirve para una sugerencia inicial o para una *pista* de búsqueda. Elegir hoy el único franco posible para dos personas puede agotar la capacidad de mañana. Un intento fallido carece de valor como prueba de imposibilidad. |
| Enumeración completa | Oráculo independiente para fixtures chicos. Con solamente 3 decisiones por persona-día, 4 personas y 7 días ya dan hasta 3²⁸ combinaciones brutas antes de los filtros. |
| Programación lineal entera con patrones | Cobertura y elección son lineales. Es una alternativa si medir instancias revela ventaja. Habría que expresar también disyunciones, fines de semana distintos, ventanas de descanso y bloqueos. |
| CP-SAT local | Propuesta inicial. Una elección entre patrones finitos, implicaciones y objetivos enteros se expresan directamente. Permite distinguir solución factible, prueba de inviabilidad y fin del presupuesto sin prueba. La generación combinatoria de patrones y las pasadas sucesivas necesitan medición en la PC objetivo. |

El ejemplo oficial de planificación de empleados utiliza una cuadrícula de turnos. Aquí se conserva la elección binaria y se sustituye la cuadrícula de turnos compartidos por patrones específicos y cobertura por intervalos. La dependencia es la biblioteca local. [Guía de planificación de empleados](https://developers.google.com/optimization/scheduling/employee_scheduling) · [CP-SAT y sus estados](https://developers.google.com/optimization/cp/cp_solver)

## Qué se resuelve y qué se puede publicar

1. **Alcance editable.** Conjunto autorizado de personas/fechas/bloques. Confirmar una semana exige validarla junto con los días vecinos. Los días pasados, bloqueados o confirmados fuera de una revisión autorizada son hechos fijos.
2. **Contexto de cálculo.** Completar las semanas que cruzan los límites, los fines de semana de las metas mensuales y todas las ventanas que tocan un cambio. Cargar los bloques que cruzan los extremos, incluidas tareas antes de apertura y después de cierre. Para el descanso interjornada importar la jornada anterior y la siguiente relevantes aunque haya días sin actividad. Para rachas y descanso semanal cargar la longitud íntegra de las ventanas según cada regla. Para una vigencia cambiante identificar qué versión gobierna cada medida.
3. **Contexto sin publicar.** Si faltan fechas futuras, es posible resolverlas junto con el período como extensión provisional explícita. Entregar su asignación testigo, revalidar y marcar qué condiciones dependen de ella. La justicia mensual incompleta se muestra como proyección. Una confirmación parcial requiere contexto suficiente para todas las obligaciones que se cierran con ella y que las decisiones futuras respeten el borde confirmado. Si un cupo obligatorio necesita otros días aún inciertos, confirmar la semana íntegra o conservar el borrador. Una nueva búsqueda revalida esos bordes. Una extensión provisional jamás altera por sí misma una fecha confirmada.
4. **Datos incompletos.** La ausencia de contexto histórico indispensable para una obligación genera «Falta información» y bloquea confirmación/generación completa en el ámbito afectado. La ausencia de historia de equidad tiene su propio inicio neutral. Una asignación persona-fecha entra una sola vez, como variable, dato fijo o hecho histórico. Para un trabajo que cruza medianoche hay un único ID de jornada.

**Ejemplo sintético.** Domingo 19:00–lunes 01:00 y lunes 18:00–martes 00:00. En sus respectivas semanas se imputan 360 y 360 minutos. El lunes civil tiene presencia de 00:00 a 01:00 y de 18:00 a 24:00, con 17 horas de descanso entre jornadas. Cambiar el cierre del domingo obliga a revalidar la semana de la jornada del lunes.

## Datos y generación de opciones

Para cada persona activa $p$ y fecha operativa $d$, el materializador entrega un conjunto finito $K_{pd}$ de opciones. Cada opción tiene estado, ID, regla de origen y, si es trabajo, lista ordenada de bloques reales semiabiertos en minutos enteros. En los demás estados la lista está vacía. El ID de plantilla ayuda a rastrear decisiones. La validez se determina a partir de los hechos.

| Paso | Condición de construcción |
|---|---|
| Resolver el calendario | Elegir apertura/cierre y vigencias según la precedencia declarada. Una misma prioridad con valores incompatibles detiene la materialización. Si se permiten tareas fuera de apertura, usar la ventana laboral autorizada. |
| Expandir plantillas | Evaluar anclas absolutas o relativas a apertura/cierre con sus desplazamientos de fecha. Para ventanas flexibles enumerar inicios, finales o duraciones autorizados sobre la rejilla de esa plantilla. En partidas, combinar bloques solo si respetan orden, hueco, duración, amplitud, actividad, disponibilidad y reglas efectivas. No convertir un hueco en descanso entre jornadas. |
| Preservar exactitud | Guardar extremos manuales y bloqueados al minuto exacto. Si una asignación manual válida fuera de rejilla puede conservarse, incorporarla literalmente a su dominio con su autorización de origen. Si contradice una restricción dura, devolver el conflicto con su bloqueo. La rejilla de búsqueda no autoriza redondear un dato. |
| Añadir estados autorizados | Franco fijo, franco rotativo y ausencia son categorías distintas. Una licencia total se vincula a un hecho. Una indisponibilidad parcial filtra bloques y deja otras opciones. «Sin asignar» es admisible para el jefe sin turno o como falta en un borrador. Un empleado activo no puede eludir trabajo/cupos con un día vacío en un horario completo. Un cierre del local necesita la regla de estado/cómputo aprobada para ese día. |
| Normalizar | Usar la unión de bloques para comparar presencia. Mantener la segmentación original cuando un bloqueo o regla de pausa le dé significado. Deduplicar solo opciones equivalentes para **todas** las restricciones, salidas y métricas, incluidas elegibilidad de apoyo y fijación de bloques. |
| Medir el dominio | Registrar tamaños antes/después de filtros, grupos descartados y procedencia. Límites de expansión, memoria o tiempo se fijan para la ejecución. Un recorte técnico sin prueba de equivalencia impide declarar inviable el dominio completo. Se puede detener y pedir acotar un patrón. Una búsqueda parcial solo entrega un hallazgo factible y validado o un resultado indeterminado. |

Una ventana autorizada «cada 15 minutos» define un dominio finito. La decisión técnica de probar cada 15 minutos cuando la regla admite cada minuto es una reducción de búsqueda. Debe declararse, aunque ambas produzcan las mismas opciones en una corrida. Usar orden estable. Detectar límites antes del producto cartesiano de plantillas partidas y cancelar durante la expansión. No fijar un tope de jornadas del negocio por comodidad del generador.

## Modelo de factibilidad

Usar $x_{pdk}\in\{0,1\}$. Exactamente una opción por persona-fecha modelada. Una celda fija se puede incorporar con un solo candidato o como constante, nunca por ambos caminos. El número de minutos operativos de una opción es la suma de las longitudes de sus bloques reales.

| Familia | Formulación y control de bordes |
|---|---|
| Asignación individual | Para cada celda, $\sum_{k} x_{pdk}=1$. Actividad y patrones válidos dependen de la persona y la fecha. Si el dominio completo queda vacío, informar su causa. |
| Compatibilidad personal | Para opciones incompatibles de fechas distintas de la **misma** persona imponer $x_i+x_j\leq1$. Hay incompatibilidad por intersección positiva de bloques o violación de la separación interjornada aprobada. Una jornada partida ocupa para este último control el período desde su primer bloque hasta su último fin. No puede intercalarse otra jornada de la misma persona en el hueco. Entre personas distintas no se crea esa exclusión. Para horarios cronológicamente ordenados con descanso mínimo uniforme basta comprobar pares potencialmente demasiado cercanos. Políticas dependientes de la jornada siguiente real deben evaluar la sucesión efectiva, incluidas jornadas fijas en ambos bordes. |
| Horas | Para semana operativa $w$, $H_{pw}=H^f_{pw}+\sum_{d\in w,k}m_{pdk}x_{pdk}$. Aplicar cotas duras solo cuando estén vigentes. Las metas se evalúan aparte. Una regla legal definida por día civil, ventana móvil u hora nocturna usa la intersección real de cada bloque con esa ventana y su propia unidad, nunca $H_{pw}$ por sustitución. |
| Francos | Máscara fija por fecha y contador separado de opciones «rotativo». Para el cupo semanal exacto, fijar suma de elegidos más los rotativos exteriores fijos igual al cupo resuelto. Para una política de mínimo/máximo, usar las desigualdades pactadas. Una sola etiqueta por fecha impide doble imputación. La licencia puede exigir una regla de cupo particular para esa semana. Sin regla que resuelva el caso, devolver dato faltante. |
| Descanso físico | El franco operativo impide una nueva jornada ese día. Si se exige día civil enteramente libre, el estado excluye además todo bloque de fechas vecinas que lo toque. Para un descanso continuo de $L$ minutos dentro de una ventana real $[a,b)$, crear posibles inicios $a$ y los fines de bloques candidatos o fijos dentro de la ventana, con $t+L\leq b$. Exigir al menos un testigo $t$, incompatible con cualquier opción o bloque fijo que intersecte $[t,t+L)$. Es exacto para ese tipo de regla porque todo hueco empieza en el borde o al terminar un bloque. Aplicar la definición específica de ventana aprobada. |
| Consecutividad | Si el máximo autorizado es $c$ días operativos trabajados seguidos, sobre cada ventana de $c+1$ fechas imponer que a lo sumo $c$ estén trabajadas. Si cuenta días civiles con presencia, formar primero ese indicador con un OR sobre bloques que los tocan. |
| Ausencia, disponibilidad, bloqueos | Toda presencia debe estar contenida en disponibilidad efectiva y libre de indisponibilidad confirmada. Bloqueo de jornada/franco fija la firma completa. Bloqueo de bloque exige exactamente sus extremos e identidad semántica en el candidato. Una petición preferente únicamente genera coste. Prohibir cambios en celdas fijas aun si ello hace inviable una reparación. |
| Otras obligaciones configuradas | Permisos de apertura/cierre se expresan como cobertura por grupo habilitado, con personas únicas. Duración mínima/máxima, pausas, amplitud y reglas nocturnas se aplican a la escala de tiempo que indique la regla. Cada regla dura debe tener soporte en el validador para confirmar y además en el motor para generar. Si solo falta soporte en el motor, está disponible la confirmación manual tras validación completa. Si la interpretación o el soporte del validador siguen pendientes, la aplicación conserva el trabajo como borrador. |

Si se confirma una obligación de franco parcial, hacen falta su unidad, jornada habitual de referencia, vigencia y condiciones de goce. Una jornada corta o un hueco de una partida no acreditan ese beneficio por sí mismos. Igualmente, si la persona permanece a disposición durante una pausa, distinguirla del hueco libre antes de computar trabajo, disponibilidad para cobertura o descanso según las reglas verificadas. Si falta esa capacidad en el validador, se conserva la edición de borradores. Ver el análisis normativo en el [índice](00_INDEX.md).

En una excepción retroactiva, mostrar el conflicto con la revisión vigente. Para hoy, congelar toda presencia iniciada y todo el pasado al corte real de la instantánea. Solo considerar bloques posteriores sin empezar si están en el área autorizada. Si lo iniciado vuelve imposible el cambio, conservar el original y registrar el incidente para revisión.

### Cobertura simultánea exacta

Ordenar y deduplicar todos los inicios/fines de bloques candidatos y fijos, requisitos de demanda y cambios de regla/grupo que afecten el conteo. Entre puntos consecutivos, la presencia y el requisito son constantes. Incluir el tramo después de medianoche de la jornada anterior y el hueco entre bloques de una partida. Una rejilla de visualización no define los segmentos matemáticos.

En cada segmento $s$, $a_{is}=1$ si una opción $i$ cubre todo $s$, y 0 en otro caso. Para grupo $g$, con opciones elegibles $E_g$, la presencia garantizada $N_{gs}=N^f_{gs}+\sum_{i\in E_g}a_{is}x_i$. Contar cada persona una sola vez por segmento. Las incompatibilidades de la misma persona y la partición entre constantes y variables garantizan esa propiedad. Exigir $N_{gs}\geq M_{gs}$ para cada mínimo activo. Por ejemplo, un mínimo de empleados y un mínimo total son dos restricciones simultáneas. Dos requisitos de grupos superpuestos no implican automáticamente que deban cubrirlos dos personas distintas. Si se exige simultáneamente cubrir puestos exclusivos, la configuración debe definirlos expresamente y requerirá una asignación de persona a puesto antes de habilitar esa regla.

Definir un déficit ideal $I_{gs}=\max(0,D_{gs}-N_{gs})$, donde $D\geq M$. El coste $C=\sum_{g,s}\mathrm{dur}(s)I_{gs}$ se expresa en personas-minuto por requisito ideal. Si se configuran dos ideales superpuestos, informar cada uno por separado y explicitar que ambos entran en $C$. Un segmento de 5 minutos tiene menos peso que otro de dos horas.

| Presencia de propietarios | Efecto sobre el plan garantizado |
|---|---|
| Bloque comprometido y fijo | Obligatorio en sus minutos exactos. Cuenta en los grupos que admiten jefes y consume sus límites. |
| Compromiso previo explícito de aceptar una asignación dentro de opciones delimitadas | Permite opciones de apoyo elegibles bajo los límites aceptados. Cuenta solo lo que se asigna dentro de dicho compromiso. Opcional en la configuración, pendiente de confirmar como mecanismo del local. |
| Disponible, pendiente de confirmar | Puede originar una sugerencia separada «Pedir apoyo de 18:00 a 19:00». Indicar el hueco que quedaría si no acepta. Tras registrar el compromiso se obtiene una instantánea nueva y se revalida antes de confirmar. |
| Refuerzo eventual | Queda fuera de mínimos e ideales garantizados. No genera un turno ficticio ni se incluye en la equidad de los empleados. |

El tiempo $J$ de apoyo electivo mide los minutos efectivamente asignados entre las opciones previamente comprometidas. El apoyo fijo adicional se informa como constante. Con apoyo exclusivamente fijo, todos los planes pueden empatar en $J$.

## Preferencias, orden de optimización y alternativas

**[D]** Minimizar vectores lexicográficos enteros. $F$ es el vector de equidad definido en el documento asociado. $H$ suma minutos absolutos de desviación de metas blandas diarias/semanales activas. $P$ suma las penalizaciones enteras documentadas de preferencias incumplidas, una por solicitud o por minuto según su tipo declarado. $R$ evalúa alternancia y variedad. $C,J$ tienen las unidades indicadas arriba. El esquema registra reglas y prioridades, límites superiores de cada función y métricas por persona/grupo. Una escala o suma que pueda exceder enteros admitidos es entrada no admisible para ese modelo.

| Perfil sugerido | Prioridades de menor a mayor índice, empezando por la más importante |
|---|---|
| Equilibrada | $F, C, J, H, P, R$ |
| Priorizar cobertura ideal | $C, F, J, H, P, R$ |
| Priorizar menor apoyo | $J, F, C, H, P, R$ |
| Reparar | Anteponer personas afectadas, celdas afectadas y minutos cambiados al perfil Equilibrada. |

Resolver un nivel cada vez con objetivo entero y brechas de óptimo exactas para declararlo probado. Solo fijar como óptimo un valor probado. Si vence el presupuesto global, conservar el mejor testigo válido encontrado con sus niveles probados y pendientes. Omitir pasadas posteriores o fijar explícitamente una cota factible como heurística, sin proclamar óptimo global. Un óptimo bajo cortes de diversidad solo vale para ese subproblema. Un empate final se puede resolver por orden estable de IDs y opciones cuando todavía hay presupuesto. Semilla, versión y opciones de prueba quedan registradas.

**[D]** Pedir hasta tres propuestas. Resolver el perfil Equilibrada y conservar sus métricas como referencia. Al buscar las restantes, imponer que cada componente de $F$ quede como máximo en la referencia más la tolerancia autorizada. Propuesta inicial de tolerancia cero. Toda referencia no probada óptima se identifica como factible. La tolerancia sirve para comparar propuestas y jamás relaja una obligación.

**Consecuencia verificable de estas prioridades.** Si Equilibrada demuestra el óptimo de $F$ y después de $C$, y la tolerancia en todos los componentes de $F$ es cero, ninguna otra solución admisible de esa búsqueda puede mejorar $C$. Puede cambiar la distribución de francos con empate o reducir apoyo aceptando peor cobertura ideal. En ese escenario no corresponde prometer una opción «Mejor cobertura». Para explorar un intercambio real entre equidad y cobertura, el responsable puede autorizar una tolerancia blanda visible, o se puede obtener una mejora respecto de una referencia que solo era factible. Mostrar en cantidades qué componente cedió. Un mínimo obligatorio conserva siempre el mismo valor.

Para cada propuesta previa (q), marcar de antemano las opciones que cambian materialmente una **celda visible y editable** respecto de (q). Cuenta un cambio de estado (p. ej., mover un franco), un cambio de apoyo de una persona identificada o una diferencia de presencia de al menos un umbral configurable. Se propone probar 60 minutos de diferencia simétrica, calculada como minutos presentes en exactamente una de las dos jornadas. Exigir que al menos una opción marcada sea elegida para **cada** (q). Una diferencia de ID interno o fuera de la vista no cuenta. Si todas las celdas están fijadas o no hay diferencias elegibles, mostrar solo la primera.

Descartar alternativas dominadas respecto de todas las métricas comparadas. Mantener distribuciones de francos materialmente distintas que empatan. Usar «Mejor cobertura» o «Menos apoyo» solo cuando las cifras realmente mejoren frente a la referencia. Si empatan, explicar la diferencia concreta, p. ej. «El franco del sábado pasa de A a B». Un corte de diversidad infactible demuestra a lo sumo la ausencia de otra propuesta con **esas** condiciones. Evitar enumerar todos los horarios. [Límites de búsqueda oficiales](https://developers.google.com/optimization/cp/cp_tasks)

## Reparación local

Base = revisión vigente identificada y leída al comenzar. Aplicar el imprevisto como excepción explícita. Fuera de las celdas autorizadas, fijar exactamente la base, incluidas las asignaciones vecinas que atraviesan el período. En una celda con bloque protegido, fijar ese bloque aunque otras partes sean editables. Incluir como opciones las asignaciones base que todavía sean válidas. Se permite un bloqueo incompatible como evidencia de conflicto, nunca como candidato legal.

Para cada opción precalcular contra la base un indicador de cambio de estado, trabajo o compromiso visible y las longitudes de las diferencias simétricas entre uniones de bloques. Conservar la segmentación cuando la separación sea relevante para la persona o esté fijada. El cambio de identificador de una plantilla equivalente cuesta cero. $z_{pd}$ es la suma de opciones elegidas que cambian la celda. Definir $u_p=\max_d z_{pd}$. Minimizar en orden ($\sum_p u_p,\sum_{pd}z_{pd},\sum_{pdk}\Delta_{pdk}x_{pdk}$). Incluir cambios forzados en los totales y distinguirlos en el resumen. Una ausencia impuesta puede agregar un coste constante que no altera el orden de soluciones.

Mostrar personas y turnos antes/después, cambios obligados, arrastre de madrugada y apoyo comprometido. Revalidar al presentar y al confirmar con las versiones actuales. Ante una colisión explicar qué ampliar o revisar. La ampliación de alcance requiere una nueva decisión humana. La operación nunca publica la base modificada por sí sola.

## Diagnóstico y garantías

| Observación | Diagnóstico permitido |
|---|---|
| Faltan cobertura, elegibilidad, contexto obligatorio o reglas soportadas | Entrada incompleta/no compatible con ruta al campo. La omisión de un mínimo y un mínimo explícito cero son valores distintos. |
| Franja con mínimo 3 y solo 2 personas distintas con opción compatible incluso por separado | Cota superior 2. El certificado de insuficiencia vale si el catálogo está completo para esa franja. Es una condición necesaria. Que 3 personas tengan opciones no garantiza que se puedan combinar en toda la semana. |
| Inviabilidad demostrada del problema estricto completo | Informar período, alcance, bloqueos y dominio autorizado bajo los que se probó. Opcionalmente reconstruir un modelo diagnóstico de factibilidad, sin objetivos/cortes, con grupos de restricciones identificados. |
| Núcleo de supuestos | Activar grupos con literales de hipótesis solo cuando la restricción admita esa forma o se transforme correctamente. Para este pase usar un trabajador y verificar la correspondencia del núcleo con reglas de la instantánea. Las eliminaciones hechas en el materializador necesitan trazas propias o reconstrucción sin filtrado previo. Un subconjunto suficiente puede incluir causas redundantes. [Guía de diagnóstico de OR-Tools](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/troubleshooting.md) |
| Límite de tiempo, memoria, generación incompleta o interrupción sin testigo | Indeterminado o cancelado según la causa. Sugerir revisar la ventana, el patrón o el presupuesto. No declarar incompatibilidad demostrada. |
| Resultado no validable o modelo interno inválido con petición bien formada | Error técnico. Aislar el resultado, permitir edición manual y conservar la revisión vigente. Un error del motor difiere de datos de entrada inválidos. |

Un ensayo contrafáctico para explicar un bloqueo puede indicar dónde se necesitaría apoyo. Sus horarios no se ofrecen como válidos. Cualquier sugerencia debe respetar las obligaciones verificadas. La UI debe expresar el dato y la consecuencia, por ejemplo «El domingo de 19:00 a 20:00 se necesitan dos empleados. Solo hay uno con disponibilidad».

## Comprobación independiente y criterios de salida

El validador parte de asignaciones materializadas, reglas de negocio, autorizaciones y contexto, compartiendo únicamente primitivas temporales comprobadas. Recalcula identidad, estados/fechas, ajuste a plantilla/permiso, vigencia, bloqueos, horas, disponibilidad, cupos, descanso, rachas y apoyo. Para cobertura recorre eventos reales de entrada/salida y límites de requisitos, con extremos semiabiertos. No lee variables del modelo, coeficientes de cobertura precalculados ni el «válido» del motor. Recalcula métricas y diferencias para mostrarlas. Un fallo duro impide ofrecer la propuesta para confirmación.

El oráculo de fixtures pequeños enumera opciones de manera independiente y usa ese validador. Comparar existencia, vectores óptimos y distancia de reparación, admitiendo empates de horarios. Añadir fixtures con un solo minuto descubierto, una jornada partida, un borde nocturno de mes, dos personas para tres plazas, bloqueos parciales, y óptimos alternativos indistinguibles en la semana visible. Las pruebas de tiempo se hacen con límites inyectables, en procesos locales, verificando que un resultado tardío no publique nada. Registrar tiempo de expansión/modelado/solución/validación, memoria, número de opciones, segmentos, pares incompatibles y niveles probados en el equipo de prueba. Este documento especifica pruebas por ejecutar.

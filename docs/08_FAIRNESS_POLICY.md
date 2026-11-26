# Equidad histórica y rotación de francos

**Requisito.** Procurar dos fines de semana disfrutados al mes por persona elegible, alternados con francos entre semana, en la medida en que la cobertura y las obligaciones lo permitan. El martes fijo y el rotativo adicional son beneficios independientes. El historial documenta lo planificado y confirmado, e incorpora sus correcciones autorizadas. No acredita asistencia.

**Propuesta de diseño.** A continuación se explicita una política verificable para iniciar las pruebas. El local debe elegir cómo entiende un fin de semana disfrutado, cómo trata licencias y altas/bajas, y si acepta el criterio de compensación. Conservar la versión de esta política en cada revisión. Las cifras de los ejemplos son sintéticas.

## Qué se cuenta

| Hecho | Cupo fijo/rotativo semanal | Beneficio de fin de semana propuesto |
|---|---|---|
| Franco fijo | Únicamente el cupo fijo que corresponda | Por sí solo, cero |
| Franco rotativo en día hábil de la rotación | Una unidad en el cupo rotativo | Una unidad solo si cae en día elegible del fin de semana |
| Dos rotativos el mismo fin de semana, autorizados en su semana | Dos fechas de franco rotativo | Un solo fin de semana disfrutado |
| Licencia, vacaciones, ausencia, día sin asignar o refuerzo eventual | Ningún crédito automático | Cero. Puede reducir la oportunidad de participar según la política de elegibilidad. |
| Jornada corta o supuesto medio franco | Solo lo que establezca una regla expresa y soportada | Cero por defecto. Nunca inferir un crédito completo a partir de la duración. |
| Franco operativo con arrastre del turno anterior hasta la 01:00 | Puede satisfacer el cupo operativo | Depende de si la política exige fecha operativa o día civil totalmente libre. |

Identificar cada fin de semana por la fecha de su sábado local. Asignarlo al mes de ese sábado. Un domingo 1.º puede pertenecer al mes anterior. Si se incluye el viernes, pertenece al sábado siguiente. Contar sus fechas completas aunque se consulte un solo mes en pantalla. Un mes tiene cuatro o cinco sábados y el quinto por sí mismo no crea una tercera meta.

La configuración distingue dos interpretaciones. En el modo **algún día**, basta un franco rotativo en cualquiera de los días elegibles que cumpla la base temporal elegida. En el modo **fin de semana completo**, todos los días definidos deben estar libres por franco admisible y al menos uno debe ser rotativo. Un fijo puede completar el conjunto. La licencia no origina el crédito. Pedir todo sábado y domingo con una sola fecha de franco posible por semana y ningún otro día libre compatible puede hacer inalcanzable esta meta. Revisar la interpretación con el dueño.

Para una persona $p$ y fin de semana $w$, definir $b_{pd}$ binario para «rotativo válido en ese día». En base civil, ligarlo además a que ningún bloque real invada la fecha. Esa conjunción debe evaluarse sobre opciones propias y vecinas. En modo algún día usar $y_{pw}=\max_{d\in w} b_{pd}$. En modo completo, $y_{pw}$ es el AND de «cada fecha está libre por franco admisible» y «algún $b_{pd}=1$». Usar equivalencias en ambos sentidos para que los créditos se puedan auditar aun cuando no estén en el objetivo activo. La propiedad de un fin de semana se resuelve una vez y $y$ es binario. Los conteos de sábados/domingos libres se conservan separados.

## Elegibilidad y objetivo mensual

Propuesta para el piloto sintético. Participan empleados activos con cupo rotativo y condiciones comparables. El jefe sin rotación y la persona con francos exclusivamente fijos quedan fuera. Una persona con fijo adicional sigue participando por su cupo rotativo. Asignar grupos de comparación con reglas explícitas (p. ej., mismo cupo y tipo de rotación). Conservar grupo y vigencia. Si se pierde la comparabilidad al cambiar de régimen, cerrar la serie anterior y empezar la nueva con saldo neutral o una equivalencia documentada.

Para cada persona y fin de semana determinar la elegibilidad **antes** de buscar. Considerar vínculo activo, esquema de rotación pactado y excepciones confirmadas que dejan o quitan la oportunidad de recibir un franco rotativo. Si solo el sábado es elegible y la persona está de licencia ese día, esa oportunidad queda fuera cuando así lo determine la política de licencia. Una mera preferencia, el resultado que escoja el optimizador, un bloqueo creado para favorecer a otra persona o la escasez de cobertura no deben eliminar retroactivamente la oportunidad del denominador. Guardar motivo y versión por exclusión. En modo completo, verificar la elegibilidad de todo el grupo de días. Clasificar los casos ambiguos antes de usar el cálculo real.

Sea $W_m$ el número de fines de semana atribuidos al mes civil $m$ y $n_{pm}$ el número elegible para $p$. La meta blanda propuesta equivale a $2n_{pm}/W_m$ fines de semana. Para no redondear una oportunidad parcial a cero o uno, usar unidades enteras de **1/20 de fin de semana**, porque 20 es múltiplo de 4 y de 5. Con la meta de dos, el objetivo en unidades es $T_{pm}=40n_{pm}/W_m$ y el crédito $A_{pm}=20\sum_{w\in m} y_{pw}$. El objetivo nunca supera 40. Si se introduce otra meta, comprobar que la escala represente sus valores exactamente y versionar el cambio.

| Caso sintético | Operación | Lectura |
|---|---|---|
| Persona activa todo un mes con cinco sábados | 40 × 5 / 5 = 40 | Objetivo de dos fines de semana |
| Alta a mitad de mes, dos elegibles de cuatro | 40 × 2 / 4 = 20 | Objetivo de uno |
| Dos elegibles de cinco | 40 × 2 / 5 = 16 | Objetivo contable de 0,8. Un único crédito real equivale a 20 unidades. |
| Licencia completa, cero elegibles | 40 × 0 / 4 = 0 | Sin deuda nueva producida por esa licencia |

Los créditos se ganan solo enteros. La fracción sirve para comparar oportunidades en el cálculo. En pantalla corresponde mostrar «1 fin de semana con franco, de 2 en que podía participar» y los días concretos. No exponer como obligación individual una meta fraccionaria.

## Historial y prioridad

**[D] Ventana inicial.** Dos meses anteriores más el mes en planificación. Dentro de la ventana solo incorporar las asignaciones vigentes confirmadas de meses anteriores. Su revisión sustituida no se vuelve a contar. Para el mes actual sumar fijos ya confirmados y asignaciones candidatas de fechas distintas. Si un fin de semana tiene un día histórico fijo y otro variable, combinar ambos para generar un único $y$. Un fin de semana de borde ya ganado no se puede ganar otra vez por confirmar el domingo. Recalcular siempre desde hechos y política versionados. El saldo es derivado.

Para cada persona de un grupo, sumar en los meses previos comparables las diferencias $T_{pm}-A_{pm}$. Si no hay historia, iniciar en cero y mostrar «Rotación iniciada sin historial previo». Si la historia empieza a mitad de un mes, tomar solo oportunidades documentadas para las que haya hechos completos, usando el número real de sábados del mes como denominador y excluyendo de la deuda los tramos de historia desconocida. Un hueco de datos no demuestra que la persona trabajó. Registrar qué fines de semana se incluyeron.

La política propuesta satura el saldo previo entre −40 y +40 unidades, es decir, hasta dos fines de semana en cada dirección. El tope evita que un mes excepcional determine toda la temporada. Sea $B_p$ ese saldo. Para el mes evaluado, calcular dos déficits no negativos:

- $d_p=\max(0,B_p+T_{pm}-A_{pm})$, el déficit con memoria acotada.
- $q_p=\max(0,T_{pm}-A_{pm})$, el déficit de la meta del mes.

En el grupo con personas elegibles en el mes actual, priorizar en orden la mayor deuda individual $d_p$, la suma de deudas $d_p$ y la suma de déficits mensuales $q_p$. Si no hay elegibles, los tres valores son cero. Cuando hay varios grupos comparables internamente, formar para el primer nivel la suma de los máximos **de cada grupo**. Para los otros dos niveles sumar los componentes de los grupos. Esta agregación se propone para un local pequeño. La interfaz explica las fechas en juego. Devolver siempre los valores individuales y los de grupo para reconstruir el vector $F$. Si el mes contiene solo parte de una cohorte, congelar el grupo efectivo para cada oportunidad y agregar por persona-régimen con sus objetivos proporcionales y un único crédito por sábado. No trasladar automáticamente un saldo entre regímenes no comparables.

Optimizar un mes de referencia por petición de equidad. El plan puede abarcar semanas vecinas por factibilidad. Cargar todos los fines de semana del mes relevantes como hechos fijos o decisiones, y resolver los fines de semana de borde atribuidos a él. Si se visualiza solo una semana, la UI distingue un fin de semana *ya confirmado* de uno *previsto en el resto del mes*. La deuda futura jamás se persiste a partir de una propuesta descartada. Ver [objetivos y alternativas](07_OPTIMIZATION_ENGINE.md).

**Desempate de alternancia y variedad.** Ordenar por fecha los francos rotativos elegidos por persona, incluido el último anterior relevante si se conoce. Clasificar cada uno como fin de semana o entre semana con la política de esa fecha. Para dos francos consecutivos, sumar un punto si repiten categoría y otro si repiten el día de la semana. $R$ es el par ordenado (repeticiones de categoría, repeticiones de día de la semana). Minimizar sus componentes en ese orden, según el contrato 1.0. Así una repetición de categoría no se intercambia por varias de día sin una decisión de política. Para CP-SAT puede definirse un indicador de transición $i\to j$ cuando hay rotativo en ambas fechas y ninguno entre ellas. Incluir la transición de salida a un rotativo exterior fijo cuando pueda cambiar. Esta penalización no modifica cupos ni reemplaza el control de rachas y descanso. Dos rotativos en el mismo fin de semana producen un solo crédito mensual y pueden generar repetición de categoría. Si una rotación necesita otra cadencia, versionarla.

## Factibilidad y explicaciones para el responsable

**Capacidad necesaria.** En cuatro fines de semana hay ocho días sábado/domingo. Con cuatro personas y una sola plaza libre por día, hay a lo sumo $8\times1=8$ días de franco favorable para $4\times2=8$ fines de semana-persona deseados. Esa igualdad es solo una cota. Si una persona usa sábado y domingo del mismo fin de semana, se gastan dos días para un solo crédito. Si todos requieren los mismos sábados, los huecos dominicales quizá no se puedan usar. Un franco operativo y uno civil pueden dar capacidades distintas.

**Déficit demostrable.** En el mismo ejemplo, una fecha que no admita ningún rotativo reduce el máximo a 7 días. Dado que cada fin de semana disfrutado necesita al menos un día, faltará **al menos uno** de los ocho créditos deseados, aun antes de mirar el resto de las reglas. Este déficit de una meta blanda no vuelve inviable al calendario. Si además falta personal para un mínimo obligatorio, sí puede faltar un horario válido.

**Ejemplo de prioridad, sintético.** A y B tuvieron la misma participación en un mes anterior completo y empezaron entonces sin historial. A recibió dos fines de semana y B ninguno. Para el mes actual ambos tienen objetivo de dos y aún no recibieron créditos. Solo queda un fin de semana disponible para uno de ellos. Antes de asignar, las deudas son 40 y 80 unidades. Otorgarlo a A daría 20 y 80. Otorgarlo a B daría 40 y 60. La segunda opción reduce la mayor deuda. La interfaz puede explicar «B tuvo menos fines de semana con franco en el período revisado. Esta propuesta le asigna el sábado 21», usando una fecha real de la propuesta.

**Comprobaciones de aceptación.** T06, T07, T12, T13, T14, T18 y T26. Incluir además una corrección histórica que cambia el crédito una sola vez, un mes con cinco sábados, un cambio de régimen a mitad de mes, un finde que cruza año, una fracción de elegibilidad, un mes sin datos y dos perfiles con iguales métricas que mueven francos entre personas. En casos pequeños enumerar independientemente todos los planes, calcular los créditos y comparar el vector óptimo sin exigir que el solver elija un empate particular. Son criterios para la implementación posterior.

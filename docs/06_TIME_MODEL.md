# 06 · Modelo temporal

**Convenciones V1.** Zona del establecimiento `America/Argentina/Mendoza`. Fechas operativas y civiles locales en calendario gregoriano; semana de lunes a domingo. La UI usa reloj de 24 h, sin segundos. El tiempo interno para distancias, orden y presencia es un entero de minutos UTC desde 1970-01-01T00:00Z. Un bloque se representa como `(persona, fecha_operativa, inicio_utc_min, fin_utc_min)` con `inicio < fin`. El formato de transporte se especifica en el [contrato](09_OPTIMIZER_CONTRACT.md).

## Tres preguntas diferentes

| Pregunta | Operación | Qué ocurre con un cierre tardío |
|---|---|---|
| ¿Cuántos minutos de jornada corresponden a la fecha operativa D? | Sumar `fin − inicio` de todos los bloques cuya casilla pertenece a D. | Todos los minutos de los bloques de D permanecen en D, incluidos los de la madrugada posterior. |
| ¿Quién está presente físicamente en el instante t? | Personas distintas con al menos un bloque cuyo `inicio ≤ t < fin` y el requisito de compromiso aplicable. | Un cierre del lunes aporta presencia a la madrugada civil del martes. |
| ¿Cuánto descanso separa dos jornadas consecutivas de una persona? | Primer inicio real de la siguiente menos último fin real de la anterior. Si las envolventes se intercalan, revisar conflicto de jornadas. | El descanso comienza a la salida real. La pausa dentro de una jornada partida tiene reglas propias. |

El cómputo de tiempo de trabajo o descanso exigido por una regla laboral conserva su ventana y base específicas. Definirlas en el perfil validado. La asignación interna al lunes nunca reemplaza el cálculo de mínimos o máximos que corresponda realizar en tiempo físico.

## Fechas y resolución de instantes

- Guardar la fecha operativa explícita. Una tarea de preparación antes de la apertura pertenece a la apertura a la que fue asignada. Un bloque de una jornada partida puede comenzar después de las 00:00 y seguir perteneciendo al día operativo anterior. Inicios y finales admiten desplazamientos de día explícitos, sujetos a una ventana laboral configurada.
- Un patrón fijo usa hora local + desplazamiento entero de fecha respecto de la operativa. Uno relativo usa apertura/cierre resueltos y un desplazamiento explícito en minutos reales. Los patrones situados por reloj civil se resuelven antes de restar minutos. Una ventana sin ancla disponible, p. ej. «30 minutos antes del cierre» en día sin cierre configurado, no produce un candidato silencioso.
- El editor pide hora y día del fin; puede sugerir «día siguiente» con vista previa y elección explícita. `00:00` es el inicio de la **fecha indicada**. Inicio igual a fin con la misma fecha se rechaza. No aceptar segundos fraccionarios, horas inexistentes ni redondear 17:07 a un múltiplo de 15. Un paso de generación solo limita las combinaciones automáticas habilitadas.
- Resolver fecha/hora en la zona del local. Si una hora es ambigua, pedir la ocurrencia o el desplazamiento explícito; si es inexistente, solicitar otra hora. Para detectar, convertir con las dos ocurrencias posibles a UTC y volver a la zona, verificando que la fecha/hora y el desplazamiento coincidan. Hacer restas sobre minutos UTC. No depender de la zona configurada en la PC ni de un desplazamiento fijo.
- Empaquetar la base IANA `tzdata` en Windows, fijar su versión y garantizar que el resolvedor del producto utiliza esa copia. Persistir instantes, zona, desplazamientos UTC de ambos extremos mostrados al confirmar y versión del resolvedor para reconstruir exactamente un horario histórico. Un cambio de reglas de zona afecta fechas futuras mediante revisión explícita. [Python · zoneinfo y fuentes de datos](https://docs.python.org/3/library/zoneinfo.html)

## Álgebra de intervalos

Para dos intervalos `[a,b)` y `[c,d)` hay solapamiento si `max(a,c) < min(b,d)`. Su longitud común es `max(0,min(b,d)−max(a,c))`. Se acepta `b=c` sin conflicto de presencia; un requisito de descanso independiente puede igualmente impedir esa sucesión. Validar bloques de todas las casillas de una persona, incluso en fechas operativas distintas. Una jornada posterior no puede introducirse en el hueco de una jornada partida anterior si rompe el orden o descanso interjornada.

Para un día civil libre `D` construir `[inicio_local(D), inicio_local(D+1))` resolviendo ambos extremos; no usar una duración universal de 1440 minutos. Se rechaza cualquier intersección positiva. Un franco meramente operativo exige que no exista trabajo imputado a D. Un requisito que combine ambos predicados debe satisfacer ambos.

Para cobertura dividir el tiempo real en segmentos cortados por inicios y fines de demanda, trabajo, compromisos, ventanas de rol y contexto. En cada segmento aplicar por separado el mínimo de empleados, el mínimo total elegible y los objetivos ideales. Si se usan eventos simultáneos, retirar los que terminan y agregar los que empiezan antes de evaluar el segmento que sigue. No contar a nadie dos veces. Conservar todos los límites exactos, incluidos 15:07 o 00:01. Un tramo sin política de demanda solo es cero si está declarado sin requerimiento (p. ej. cerrado).

## Contexto en los bordes

1. Definir el tramo solicitado, las fechas modificables autorizadas y un tramo de cálculo ampliado. Obtener desde ambos lados todas las jornadas cuyos bloques reales pueden tocar el área de análisis y los vecinos consecutivos relevantes por persona, aunque su día operativo esté fuera de la vista. Para una cuota semanal, traer toda la semana; para la equidad, el historial único y el fin de semana completo según la política. Los límites de rachas y reposos pueden exigir más de un día. Derivar la longitud de contexto de las reglas y de las extensiones de los patrones, no de una constante.
2. Distinguir asignación publicada, inactividad conocida, contexto de arranque declarado y desconocido. Un dato histórico confirmado o de arranque tiene fuente y cobertura temporal explícitas. Un historial de equidad ausente permite arranque neutral; la falta de una salida anterior necesaria para el descanso obligatorio requiere completar ese contexto. La futura fecha sin publicar no equivale a «libre».
3. Para confirmar, fusionar el cambio autorizado con los vecinos que quedan confirmados. Las restricciones duras que vencen en el período deben quedar verificadas. Puede cerrarse una semana completa con futuro abierto si el contrato de salida es imponible a la próxima edición (p. ej. primer inicio futuro ≥ última salida + descanso, o días trabajados consecutivos de arrastre). Conservar esos datos o derivarlos de las asignaciones inmutables. Para una cuota semanal que cruza una publicación parcial validar con el resto ya fijado o acordar publicar la semana completa. Un día hipotético generado fuera del tramo no es evidencia confirmada. Ante una dependencia sin resolver, guardar borrador con explicación.
4. Al entrar una nueva excepción física recalcular todos los días operativos que la intersectan, incluido el previo. Un día civil totalmente indisponible el 1.º de enero puede impedir la salida tardía del 31 de diciembre.

## Comprobaciones manuales para automatizar

Todos los datos de esta tabla son sintéticos. Las tolerancias reales se configuran por separado.

| Entrada local en Mendoza | Resultado esperado |
|---|---|
| Lun. 01/02/2027 19:00 → mar. 02/02 01:00; martes 18:00 → mié. 03/02 00:00 | Lunes 5×60 + 1×60 = 360 min; martes 6×60 = 360 min; descanso 18:00 − 01:00 = 17 h. Hay presencia 00:00–01:00 el martes, que conserva todos los minutos de su propia jornada. |
| D 12:00–16:00 y D 20:00 → D+1 00:00 | 240 + 240 = 480 min. El hueco de 240 min no aporta presencia ni duración. |
| A 12:00–16:00, B 15:00–21:00 | Cobertura 2 en [15:00,16:00); a las 16:00 solo B. |
| Dom. 31/01/2027 19:00 → lun. 01/02 01:00 | 360 min a enero y a la semana terminada el 31. La demanda física de febrero de 00:00 a 01:00 recibe presencia de ese bloque. |
| Dom. 31/12/2028 19:00 → lun. 01/01/2029 01:00 | Igual tratamiento en semana, mes y año. «Todo el lunes libre» en tiempo civil es incompatible; «sin jornada operativa el lunes» por sí solo es compatible. |
| Trabajo de A lunes 22:00 → martes 01:00 y otro bloque martes 00:50–01:10 | La intersección real de 10 minutos invalida el horario, aunque los bloques tengan distinta fecha de imputación. |
| Patrón de 15 min y bloque fijado 17:07–19:07 | Conservar exactamente 120 min si hay respaldo en las reglas; si choca con una norma, informar qué regla y qué bloqueo se contradicen. |

[Índice](00_INDEX.md) · [Dominio](04_DOMAIN_MODEL.md) · [Motor](07_OPTIMIZATION_ENGINE.md) · [Plan de pruebas](12_TESTING_STRATEGY.md)

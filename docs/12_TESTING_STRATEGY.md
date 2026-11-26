# 12 · Estrategia de pruebas y escenarios sintéticos

**Estado al 25 de noviembre de 2026.** Este documento define pruebas de aceptación para la implementación. Durante el diseño se ejecutaron dos enumeraciones independientes que aparecen al final. Las pruebas de la aplicación, del instalador Windows, del motor y de usabilidad con el responsable quedan pendientes.

[Índice](00_INDEX.md) · [Requisitos](02_REQUIREMENTS.md) · [Tiempo](06_TIME_MODEL.md) · [Motor](07_OPTIMIZATION_ENGINE.md) · [Equidad](08_FAIRNESS_POLICY.md) · [Contrato](09_OPTIMIZER_CONTRACT.md) · [Plan](13_IMPLEMENTATION_PLAN.md)

## Cómo preparar los ensayos

- Trabajar en una carpeta temporal y, desde F2, en una base nueva por prueba. Usar una copia descartable para pruebas de cierre abrupto y restauración. La demostración debe poder distinguirse visualmente y por ruta de datos. Ninguna prueba lee la carpeta personal del responsable.
- Identidades sintéticas A, B, C y D (empleados) y J (propietario). Fechas ISO, zona `America/Argentina/Mendoza`, minutos exactos, semana operativa lunes–domingo. Los nombres, tiempos, límites y acuerdos elegidos en cada escenario son valores del ensayo. Los casos aislados de tiempo y equidad no se ofrecen como configuraciones laborales completas.
- Para las pruebas integrales, declarar expresamente calendario, vigencias, disponibilidad, patrones, franjas de demanda, participación de propietarios, elegibilidad, cuotas, política de descanso y contexto. Para una franja sin demanda, declarar mínimo e ideal cero. Una regla desconocida en modo real requiere resolución para confirmar. El arnés de pruebas no puede convertir silenciosamente «desconocido» en cero.
- Conservar IDs T01–T26 de la V1. Los casos T27–T40 amplían la cobertura. Usar estos IDs en nombres o marcadores de Pytest y en los informes. Cada prueba debe registrar la precondición, el estímulo y valores esperados obtenidos de este documento, del dominio o de un oráculo independiente.
- Unidad de comparación de horarios: (persona, fecha operativa, estado, bloques reales ordenados). Comparar fechas, minutos y personas. Ignorar el identificador interno de patrón al medir si dos horarios son iguales y preservar la identidad cuando se modifica un nombre visible.
- Las fechas se fijan o se inyecta un reloj. Los ensayos de estados del motor emplean doble de prueba en el límite del proceso. No forzar un timeout eligiendo una máquina «lenta».
- Una contradicción de reglas válidas, un dato estructural inválido y una búsqueda agotada requieren diagnósticos distintos. Cuando no haya contexto conocido para verificar una obligación, el resultado sigue pendiente de esa verificación.

## Casos de aceptación heredados

Cada fila puede originar varias pruebas unitarias y de integración. Al probar confirmación o importación, verificar también las filas efectivas, la revisión vigente y el historial después de cerrar y reabrir el programa.

| ID | Entrada sintética y acción | Oráculo observable |
|---|---|---|
| T01 | A 12:00–16:00 y B 15:00–21:00 el mismo día | Entre 12–15 hay 1, 15–16 hay 2, 16–21 hay 1. Dos personas pueden trabajar al mismo tiempo. |
| T02 | A, lunes 2026-11-30 19:00 a martes 01:00; martes 2026-12-01 18:00 a miércoles 00:00 | Lunes 360 min, martes 360 min y 720 en total. La presencia del martes civil suma 60 + 360 = 420 min. Pausa real entre jornadas 17 × 60 = 1020 min. Mostrar ambas fechas al editar. |
| T03 | A, bloques 12:00–16:00 y 20:00–00:00 (+1) | Duración 240 + 240 = 480 min. Entre 16 y 20 A aporta cero. La pausa interna de 4 h no satisface por sí misma un descanso obligatorio entre jornadas. |
| T04 | A 12:00–16:00 y 15:59–18:00; repetir con segundo inicio 16:00; acortar disponibilidad hasta 17:59 | Rechazar el solapamiento de un minuto. La adyacencia es válida si las demás reglas la permiten. Rechazar el último minuto fuera de disponibilidad y señalar persona y hora. |
| T05 | Domingo 2027-01-31 19:00 a lunes 2027-02-01 01:00; repetir 2026-12-31 al 2027-01-01 | 360 min al día inicial y a su semana/mes/año. Entre 00–01 de la siguiente fecha existe cobertura física. Al consultar solamente el nuevo período el bloque entrante sigue computando presencia. |
| T06 | En semana completa, A tiene martes fijo y un rotativo adicional; B tiene únicamente un rotativo; sin licencias ni cierres | A tiene exactamente un fijo y un rotativo en días distintos. B tiene un rotativo. Otro empleado puede trabajar el martes. Un martes sin jornada no concede a A crédito por dos francos. |
| T07 | A sale a la 01:00 del martes. Primero martes franco operativo, después solicitud confirmada de martes civil libre | Con la primera regla no inicia jornada el martes y se comprueba el descanso real. Con la segunda existe conflicto 00–01 del martes. Un franco civil cubre hasta la medianoche siguiente. |
| T08 | Dos fechas A con únicas duraciones 180 o 360 min. Objetivo duro reducido de ambas fechas 540. Repetir con objetivo blando 500 y, luego, con 500 obligatorio | Para 540 sólo valen (180,360) y (360,180). Con objetivo blando y penalización absoluta, mínima desviación 40 min. Para 500 obligatorio se demuestra imposibilidad en esos dominios. Prohibir 3 h un día descarta su patrón ese día. |
| T09 | Patrón individual de 360 min hasta el 14 inclusive y 420 desde el 15. Existe confirmado del 14 y borrador que abarca el 15 | Aplicar por fecha operativa y vigencia. Confirmado del 14 idéntico al reabrir; borrador afectado pide revalidar. Un cambio que afecte a un confirmado futuro crea aviso sin alterar su contenido. |
| T10 | Calendario artificial habitual 12–20, especial 12–21, excepción específica 13–18; feriado y víspera coinciden con igual prioridad y cierres distintos | La excepción aplicable resuelve el horario en 13–18. Sin excepción ni precedencia que desempate las especiales se debe pedir resolución. Probar cierre a 00:00 exacta sin crear un segmento de un minuto al día siguiente. |
| T11 | Franja 18–19 con mínimo total 2, mínimo empleados 1; A presente, J eventual o disponible sin compromiso. Repetir con apoyo J comprometido en esa franja | Garantizados 1 en los primeros casos. Si no hay otro personal, se explica la falta y el posible compromiso. Con J comprometido hay 2 totales y 1 empleado. Si el mínimo empleados sube a 2 la misma pareja resulta insuficiente. |
| T12 | A tiene sábado y domingo rotativos del mismo fin de semana; regla del ensayo autoriza dos rotativos esa semana | Dos días rotativos, un fin de semana distinto bajo la política de «al menos un día». Añadir un sábado del fin siguiente incrementa el contador a dos. Probar por separado la política de fin completo si se habilita. |
| T13 | A y B tienen idéntica elegibilidad y oportunidades. A recibió menos fines de semana rotativos en historia confirmada; hay un cupo para A o B con iguales demás objetivos prioritarios. Añadir un martes fijo de A y borradores favorables a A | Si el componente de deuda histórica distingue a A como más postergada y todo lo anterior empata, priorizar A. Fijo y borradores no alteran la comparación. Al sustituir una revisión histórica, aplicar sólo la efectiva, una vez. |
| T14 | A tiene franco lunes 2026-11-02 y luego domingo 2026-11-15, con trabajo entre ambos; límite sintético de 6 fechas operativas laborables consecutivas | Son 12 fechas consecutivas (3–14 inclusive); aunque cada semana tenga un franco, excede el límite. Al abrir sólo la segunda semana conservar la racha anterior. En la variante límite 12, ese criterio se satisface. |
| T15 | Mínimo empleados 2 entre 18–19. A cubre todo y B sólo 18:15–19. Nadie más disponible | El hueco es 18:00–18:15, faltante 1 empleado y 15 persona-minutos. Explicar con datos de esa franja. No confirmar. Una relajación diagnóstica nunca reemplaza el plan oficial. |
| T16 | Doble de motor agota presupuesto antes de hallar una solución; otra variante halla una válida sin prueba de optimalidad | En el primero informar «no se encontró dentro del tiempo». En el segundo se puede ofrecer la solución validada como factible. Ninguno demuestra imposibilidad u optimalidad. |
| T17 | En [microinstancias](fixtures/microinstancias.json), jueves A pasa a tener indisponibilidad confirmada 16–20 y C está fijada a la mañana. Miércoles exterior inmutable | Mínimo lexicográfico de la microinstancia (2 personas, 2 celdas). El jueves cambian A y B, viernes y miércoles se conservan. Mostrar cambios y dejar igual la revisión oficial hasta que se confirme explícitamente. |
| T18 | Un único candidato por persona y fecha; agregar otro ID de patrón con idénticos bloques | Hay a lo sumo una propuesta material. Cambiar IDs, orden de filas o etiquetas de perfil no crea otra. Construir un segundo caso con tres repartos de francos que sí cumplan el umbral configurado. |
| T19 | Editar manualmente un bloque y dejar 10 minutos sin mínimo obligatorio; guardar borrador, cerrar, reabrir, corregir y confirmar | Borrador recuperable con conflicto localizado. Confirmación bloqueada mientras haya hueco. Tras corregir, se crea revisión y se conserva la anterior, también sin optimizador disponible. |
| T20 | Cancelar generación, simular caída de proceso y modificar una regla o asignación durante una búsqueda que devuelve éxito tardío | La revisión confirmada y el borrador editado permanecen íntegros. Descartar resultado obsoleto o cancelado, permitir reintento y distinguir el fallo técnico. |
| T21 | Dos personas con etiqueta visible «Demo Sol», IDs diferentes y roles empleado/jefe. Editar sólo una; luego desactivarla con vigencia | Identidades distintas en búsqueda, exportación y asignaciones históricas. Las fechas posteriores a la baja no admiten asignaciones nuevas para esa persona. |
| T22 | Tomar respaldo; importar configuración con referencia huérfana y otra de versión incompatible; ejecutar restauración de respaldo válido tras un cambio intencional | Cada rechazo conserva íntegros revisión vigente, conteos e historial. Restaurar recupera estado anterior, incluidos reglas, revisiones y bloqueos. Comparar contenido lógico reabierto; un hash binario de la base activa no es un oráculo adecuado para equivalencia lógica. |
| T23 | Exportar PDF y PNG de semana confirmada con nombre largo, jornada partida y salida 01:00 (+1), solicitud con motivo sintético «PRIVADO-DEMO» | Fecha/revisión y estado visibles, ambos bloques legibles en previsualización, papel y teléfono. Marca de cambio de fecha. El motivo no aparece ni en texto exportado ni en imagen o metadatos. |
| T24 | Sustituir el adaptador CP por un doble que habla el contrato y sólo recibe la solicitud serializada; devolver propuesta válida y luego una inválida | La primera llega a revisión humana luego del control independiente. La segunda es rechazada y queda diagnóstico. Revisar dependencias/importaciones del adaptador: ninguna de interfaz, repositorio ni ruta de base. |
| T25 | En Windows limpio, cuenta estándar y red deshabilitada, instalar desde medios locales; ejecutar con optimizador retirado o que falla. Usar configuración sintética completa | Abrir, editar, validar, confirmar y exportar manualmente; sin descargas de dependencias ni intérprete preinstalado. Generación indica problema de motor y conserva el trabajo. |
| T26 | Sábado 2026-10-31 y domingo 2026-11-01, política de atribución al sábado. Rehacer abriendo noviembre solo, con historial; repetir con alta/baja intermedia, mes de cinco sábados y ventana parcial | El mismo fin se cuenta una vez en octubre. La incorporación o baja ajusta el denominador/meta según la política versionada de elegibilidad, nunca añade deuda previa al alta. Al abrir un tramo parcial no se crean cuotas semanales adicionales. Sin contexto suficiente se indica pendiente. |

## Casos adicionales de riesgo

| ID | Variaciones que se deben ensayar | Oráculo o evidencia exigible |
|---|---|---|
| T27 | Edición autorizada a 12:07–13:03 junto a candidatos en grilla de 15 o 30 min. Disponibilidad y demanda cambian a 12:11. Par idéntico de horas de inicio/fin sin desplazamiento de fecha | Conservar 56 min y el punto 12:11. Si el acuerdo prohíbe el bloque, explicar. Una coincidencia de extremos sin fecha de salida posterior es duración cero inválida. Comparar cobertura con barrido por minuto. |
| T28 | Tramo lunes–viernes entre domingo confirmado que cruza medianoche y sábado ya fijado. Falta parte de la semana exterior; generar, confirmar parcialmente y luego recomputar el resto | Leer contexto por ambos lados para presencia, descanso y cuotas. Un dato ausente se distingue de un día libre confirmado. La vista parcial respeta las decisiones exteriores y ningún día de contexto se publica accidentalmente. Modificar el sábado invalida un resultado que dependía de él. |
| T29 | Jornada en curso con un bloque ya empezado y otro futuro. Abrir inconsistencia al registrar ausencia sobre bloque futuro fijado; agregar bloqueo parcial de un bloque entre varios candidatos | Preservar el pasado según el instante de corte y la política de jornada en curso. El bloqueo parcial conserva el intervalo exacto; si no hay patrón compatible, informar conflicto. La aceptación de un cambio o desbloqueo futuro requiere autorización explícita. |
| T30 | Día de local cerrado, permiso parcial, licencia de día completo y día sin asignar de J. Activación y vencimiento de normas justo a medianoche. Dos reglas de igual precedencia incompatibles | Tipos distinguibles. Un cierre o licencia no crea automáticamente crédito de franco. Cruces reales de indisponibilidad afectan a turnos de la víspera. Rechazar ambigüedad o exponerla sin modificar vigencias previas. |
| T31 | Crear instancia de reparación con empates y víctima de ausencia bloqueada; simular límite antes de probar el primer nivel y otro límite durante nivel inferior | Mostrar un conflicto si los bloqueos lo fuerzan. Una solución factible por límite no se presenta como reparación mínima demostrada. No ampliar automáticamente personas, fechas o tolerancias para obtener más alternativas. |
| T32 | Corromper de forma controlada una respuesta de prueba cambiando persona, fecha, referencia o bloque, retirando una asignación, duplicando una celda o contradiciendo métrica de cobertura. Repetir con versión de protocolo incompatible | Rechazo por esquema, integridad semántica o validador de dominio según el caso. Recalcular cobertura con personas únicas en tiempo real. Reemplazar el motor no cambia esta defensa. |
| T33 | Modelo de una solución agotado por cortes de diversidad, modelo sin solución desde el inicio y catálogo reducido por límite de materialización | Distinguir «no hay más alternativas bajo esta distancia», «ninguna de las permitidas satisface las reglas» y búsqueda/catalogación incompleta. El agotamiento de alternativas no invalida la ya encontrada. |
| T34 | Ocho cupos de fin de semana, cuatro personas con meta dos; A y B compiten por los mismos dos sábados. Ver oráculo al pie | Hay soluciones a las reglas duras y ninguna satisface todas las metas de ese caso. Coste reducido óptimo (1,2). El informe conserva el déficit. Sin historia, la interfaz informa inicio neutral y la ventana futura no se considera observada. |
| T35 | Inyectar falla entre escrituras de una confirmación; reabrir tras interrupción; reintentar la misma acción; abrir segundo escritor; suplir poco espacio en un directorio de pruebas | O se lee la revisión antigua completa o la nueva completa. Ningún puntero hacia revisión parcial. La operación repetida no crea una segunda confirmación del mismo intento. Segundo escritor recibe respuesta controlada. El fallo de autosave se hace visible y permite conservar/recuperar cambios según el último guardado exitoso. |
| T36 | Importación cancelada en previsualización, archivo sobredimensionado o con referencias ajenas, copia de respaldo dañada/incompleta, falta de espacio/permiso, fallo durante restauración y migración interrumpida | No aplicar cambios parciales ni borrar historial. Respaldar antes de mutar y permitir volver a una copia íntegra. Verificar integridad de SQLite y claves foráneas tras reabrir. Hacer un ciclo real de migración desde la versión anterior cuando exista. |
| T37 | Usar sólo teclado; activar lector de pantalla de Windows; escalar pantalla a 150 % y 200 %; distinguir estados en escala de grises; nombre largo, grilla semanal y cuadro de error de reparación | Acciones alcanzables sin mouse, foco visible, anuncio de persona/fecha/estado, retorno al disparador tras cerrar diálogo. A escalas altas: scroll o reflujo con acciones accesibles. El mensaje de error localiza la celda y ofrece cómo corregirla. Registrar capturas sintéticas y secuencia observada. |
| T38 | Instalar, desinstalar conservando los datos y actualizar conforme al plan de distribución. Archivos en carpeta de usuario con espacios y tildes. Repetir el respaldo en destino removible y simular retiro antes de completar | La app localiza los datos previstos; conserva historial al actualizar. Si falla la copia, no ofrece ese respaldo como válido. En máquina sin red, examinar intentos salientes y recursos empacados, incluidos datos de zona horaria y componentes Qt. |
| T39 | En configuración real vacía faltan cobertura y políticas; abrir demo, crear borrador, salir. Declarar cada campo pendiente explícitamente y repetir con un perfil sintético completo | La app explica qué dato falta y permite edición parcial. Solo el perfil completo puede confirmar si pasa reglas duras. La demo mantiene sus datos separados y no precarga personas/patrones en el caso real. |
| T40 | Abrir una revisión antigua después de cambiar nombre, reglas o política de equidad; generar exportación de configuración y respaldo completo; deshacer una edición de borrador; confirmar dos operaciones en conflicto lógico | La revisión conserva su contexto. El JSON de configuración excluye horarios e historial privados; el respaldo recupera ambos. Deshacer en borrador no modifica el confirmado. Una confirmación contra una revisión de base obsoleta exige recargar o revisar diferencias. |

**Variantes laborales de T03, T07, T30 y T39.** Incorporar los cuatro [casos de revisión del perfil laboral](16_LABOR_REVIEW.md) con datos sintéticos. Desde 19:00 hasta 01:00 hay 240 min en la franja artificial 21:00–06:00; volver a las 12:00 deja 660 min reales y, con un mínimo sintético de 720, faltan 60. Un trabajo acortado no acredita automáticamente medio franco. Una espera a disposición sin atención al público necesita cómputos distintos de horas y cobertura. Si esas obligaciones están activas y el validador carece de soporte, sólo se conserva el borrador. Cuando el validador sí las comprueba pero el adaptador de optimización carece de soporte, probar confirmación manual válida y bloqueo de la generación afectada. La implementación del perfil definitivo necesita ejemplos aceptados por el asesor.

## Oráculos independientes y comprobaciones de diseño

**Tiempo y cobertura.** En muestras pequeñas, expandir cada bloque real en los minutos enteros que lo componen. Para cada minuto armar el conjunto de personas presentes y filtrar por rol y compromiso. Comparar contra todos los segmentos reportados, incluidos extremos y huecos. Para el total operativo sumar duraciones agrupando por el identificador explícito del día, sin cortar en la medianoche civil. La implementación de referencia de pruebas no importará el constructor de segmentos ni la matriz de cobertura del solver.

**Enumeración de dos microinstancias.** Los [datos completos](fixtures/microinstancias.json) fijan el orden de las personas y fechas. Son problemas reducidos para validar componentes y cotas. Para compararlos con el sistema, el fixture de integración deberá declarar explícitamente los demás parámetros y aportar un contexto compatible. La prueba de capacidad sólo considera los ocho días indicados y cada empleado puede recibir como máximo un rotativo por fin de semana; los francos entre semana quedan fuera de esta proyección. La meta de dos se fija deliberadamente para todos en esta microinstancia, independientemente de cualquier política de prorrateo.

| Caso | Espacio explorado | Resultado obtenido por enumeración exhaustiva |
|---|---|---|
| Reparación T17 | 2 patrones para 6 celdas: 2⁶ = 64 combinaciones | 3 satisfacen bloqueos, indisponibilidad y mínimos. Pares ordenados (personas modificadas, celdas modificadas): (2,2), (2,4), (3,4). La primera conserva el viernes entero. |
| Capacidad T34 | Dominios diarios de tamaño 4,2,4,2,2,2,2,2: producto 1024 elecciones | 144 respetan como máximo un rotativo/persona/fin. Al minimizar (máximo déficit personal, suma de déficits), el mínimo es (1,2), con 32 soluciones. A y B sólo pueden repartirse dos sábados para una meta conjunta de cuatro. Que haya ocho días con cupo no demuestra equidad alcanzable. |

Se ejecutó el siguiente cálculo con Python 3.12.14, biblioteca estándar, sobre el JSON incluido. Para reproducirlo desde la raíz, usar el contenido del bloque como archivo temporal y ejecutar `python ruta_al_archivo.py`. El programa no importa código del producto. No se ejecutó CP-SAT para estos resultados.

```python
import json
from itertools import product
from pathlib import Path

datos = json.loads(Path("docs/fixtures/microinstancias.json").read_text(encoding="utf-8"))
r = datos["reparacion"]
personas, fechas = r["personas"], r["fechas"]
base = {(p, d): patron for d, fila in zip(fechas, r["basePorFecha"]) for p, patron in zip(personas, fila)}
celdas = list(base)
reparaciones = []
for eleccion in product(r["patrones"], repeat=len(celdas)):
    asignado = dict(zip(celdas, eleccion))
    if any(asignado[x["persona"], x["fecha"]] != x["patron"] for x in r["fijados"]):
        continue
    if any(asignado[x["persona"], x["fecha"]] == x["patron"] for x in r["prohibidos"]):
        continue
    if any(sum(asignado[p, d] == turno for p in personas) < minimo
           for d in fechas for turno, minimo in [("M", r["minimoM"]), ("T", r["minimoT"])]):
        continue
    cambios = [(p, d) for p, d in celdas if base[p, d] != asignado[p, d]]
    reparaciones.append((len({p for p, d in cambios}), len(cambios)))
print("Reparación. Costes factibles:", sorted(reparaciones))

c = datos["capacidad"]
dominios = c["personasQuePuedenRecibirUnicoFrancoPorDia"]
factibles, costes = 0, []
for seleccion in product(*dominios):
    parejas = list(zip(seleccion[::2], seleccion[1::2]))
    if any(sabado == domingo for sabado, domingo in parejas):
        continue
    factibles += 1
    deuda = [max(0, c["objetivoDeLaMicroinstancia"] - sum(p in pareja for pareja in parejas))
             for p in c["personas"]]
    costes.append((max(deuda), sum(deuda)))
print("Capacidad. Factibles, mejor coste y cantidad óptima:", factibles, min(costes), costes.count(min(costes)))
```

## Pruebas por capa y paso de fase

| Fase | Qué se compara | Evidencia para avanzar |
|---|---|---|
| F1 · Dominio y tiempo | Ejemplos T01–T10, T14, T26–T30 en la medida en que corresponda a primitivas y reglas. Sumar un día entero al calendario conserva minutos y desplaza las fechas cuando no cambia el desfase de zona ni las reglas. Dividir un bloque en dos adyacentes conserva presencia y duración si la partición está autorizada. Permutar filas conserva el resultado. | Pruebas unitarias con fechas y salidas explícitas; semilla y dominio reproducibles si se generan intervalos. Fixtures totalmente sintéticos. |
| F2 · Circuito manual local | Editar→guardar→reabrir→validar→confirmar→revisar. Inspeccionar confirmación atómica, historial y efecto de fallos T19, T21, T35, T40. | Evidencia de lectura después de cierre abrupto en base de prueba. Ninguna operación manual depende del proceso optimizador. |
| F3 · Contrato y factibilidad | Validar ejemplos de entrada/salida y versiones; comparar factibilidad con enumeración y comprobar independientemente cada propuesta. Probar límites, entrada inválida, bloqueos, J eventual y contexto. | Informar instancia, opciones, estado, propuesta validada y prueba de optimalidad sólo si existe. Eliminar un patrón permitido no puede crear soluciones nuevas a las mismas restricciones; relajar un mínimo no puede eliminar soluciones existentes. |
| F4 · Equidad y reparación | Correr T12, T13, T16–T18, T20, T26, T31–T34. Para instancias pequeñas comparar vector objetivo con el mínimo enumerado. Verificar distancia entre alternativas y repetir con otra semilla y orden de personas. | La validez y las métricas se sostienen aun si cambia el horario concreto entre óptimos equivalentes. Un límite de tiempo no prueba optimalidad de un nivel no cerrado. |
| F5 · Interfaz e intercambio | Reproducir semana, vista diaria, mensual, edición partida, solicitudes, comparación, reparación y confirmación. Incluir T22, T23, T36, T37, T39, T40. | Informe de prueba de ida y vuelta JSON y respaldo restaurado; PDF/PNG inspeccionados a tamaño real; prueba de teclado y lector en Windows. Documentar todo caso no ejecutado. |
| F6 · Instalador y piloto | T25 y T38 en VM Windows limpia y PC representativa. Simular primer arranque, deshabilitar red, usar con y sin motor, actualizar desde build anterior cuando exista y restaurar copia. | Registrar edición/build de Windows, arquitectura, escala, versión de instalador/huella, política de red y resultados por operación. Registrar sesión de prueba con el responsable, incidentes y ajustes aceptados. |

**Mediciones de búsqueda.** Para comparar versiones usar escenarios sintéticos chicos de referencia, un mes con cuatro empleados y dos propietarios sintéticos y una variante con dominios flexibles más amplios. Variar cantidad de candidatos y patrones partidos. Registrar máquina, versión de solver, cantidad de segmentos y candidatos, semilla, trabajadores, presupuesto y tiempos de preparación, primera propuesta válida y finalización, memoria y motivo de salida. Medir también la respuesta de la interfaz a cancelar y editar. Antes del piloto, acordar con el responsable el tiempo tolerable en su PC. Un número de rendimiento sin el hardware y el escenario carece de valor para aprobar la entrega.

**Prueba con el responsable.** Partir de la demo en una PC similar a la de la heladería. Pedirle que encuentre quién está de 15 a 16, distinga un martes franco de la labor de madrugada, cargue una jornada partida, resuelva una ausencia del jueves sin cambiar el pasado, compare dos opciones, confirme y exporte para compartir. Luego pedir que recupere una copia de práctica. Observar sin guiar salvo bloqueo. Anotar tarea, interpretación, pasos fallidos, ayuda necesaria y consecuencias; nunca registrar datos laborales sensibles. Si confunde borrador con confirmado, cuenta apoyo eventual como garantizado o publica sin advertir cambios, corregir y repetir esas tareas.

**Registro por ejecución.** Incluir ID, revisión Git, versión de contrato/esquema/motor, OS, reloj/zona, fixture, comando, opciones, estado real, resultado esperado, resultado obtenido y evidencia. En pruebas automatizadas registrar casos pasados, fallidos, omitidos y motivo de omisión. En verificaciones humanas adjuntar observación replicable. No declarar un gate aprobado con casos pendientes que correspondan a esa fase. La documentación de diseño sólo acredita las dos enumeraciones y las verificaciones documentales que se informen expresamente.

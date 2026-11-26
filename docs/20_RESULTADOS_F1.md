# F1 · Dominio y tiempo en memoria

La demostración construye una semana completa de dos personas ficticias y agrega las jornadas que tocan sus dos bordes. Se puede ejecutar por separado desde la raíz con el entorno activado.

```sh
python -m pytest -q tests/unit/test_semana.py
```

## Resultados de aceptación

| Caso | Resultado comprobado |
|---|---|
| T02 · Nocturnas | Lunes 30/11/2026 de 19:00 a 01:00 del martes y martes 01/12/2026 de 18:00 a 00:00 del miércoles. Corresponden 360 min a noviembre y 360 a diciembre. Entre la salida y la entrada hay 1.020 min. El martes civil tiene 420 min de presencia. |
| T01, T03, T04 · Presencia | Dos personas coinciden de 15:00 a 16:00. A las 16:00 solo queda la segunda. Una jornada 12–16 y 20–00 suma 480 min. Una intersección personal de un minuto genera conflicto. Se admite la adyacencia y se rechaza introducir otra jornada en la pausa de la primera. |
| T05, T07, T27, T28 · Bordes | El cierre del domingo 31/01/2027 aporta presencia al lunes de febrero. Se repite al cambiar el año. Una indisponibilidad de todo el martes alcanza los 60 min de la jornada del lunes. Se conservan los minutos fuera de grilla y se comprueban ambos vecinos de una semana. |
| T06, T14, T26, T30 · Francos y contexto | Un martes fijo y un rotativo adicional requieren dos fechas. Licencia, jornada corta y casilla sin asignar conservan su estado. Se detectan el contexto semanal incompleto, una racha de doce días y un cambio de cupo que necesita transición. |
| T08–T10 · Patrones y reglas | Se prueban variantes de 180 y 360 min, objetivos duros y preferentes, versiones de 360 y 420 min con cambio el día 15 y excepciones de calendario. Una regla ausente, un empate incompatible o un ancla pendiente producen un diagnóstico. |
| Identidad, compromiso y reloj | Se comprueban homónimos, baja, materialización para una persona activa y cobertura del propietario solo durante el compromiso coincidente. La base IANA empaquetada distingue horas inexistentes o repetidas y días civiles de 23 y 25 h en Mendoza. |

## Entrega y reproducción

Partida del repositorio en `e269941`. Se incorporó el diseño 1.1 en `05c7753`, manteniendo el README de diseño en la raíz como `README_DISENO.md` para conservar sus enlaces. El índice, el handoff y el prototipo sueltos coinciden byte por byte con los del ZIP. Se usó la secuencia F1 de la revisión 1.1 cuando difería de la numeración de fases de V1.0.

| Incremento | Archivos principales | Verificación |
|---|---|---|
| B01 · `712f813`, `3704d62` | `.python-version`, `pyproject.toml`, `uv.lock`, paquetes bajo `src/heladeria/` y `tests/unit/test_entorno.py` | Instalación bloqueada, importación del dominio y lectura local de la base horaria. |
| B02 · `5a1b0a5` | `dominio/personas.py`, `dominio/tiempo.py` y sus dos archivos de pruebas | 20 pruebas específicas aprobadas. La verificación de indisponibilidad civil de T07 se integra en B03. |
| B03 · `b3d8f54`, `115dcbf` | `dominio/reglas.py`, `patrones.py`, `disponibilidad.py`, `francos.py` y pruebas de patrones, francos y semana | 8 pruebas de reglas/patrones y 20 de disponibilidad, francos y semana aprobadas. |

**Entorno probado.** Debian 13 x86-64, CPython 3.12.14, uv 0.13.9, pytest 8.4.2 y tzdata 2026.2 (IANA 2026b). Se exportó el árbol de la revisión funcional `115dcbf` a un directorio vacío y se usó una caché de paquetes nueva. Se ejecutaron:

```sh
uv sync --locked
source .venv/bin/activate
python -m pytest -q
TZ=Pacific/Auckland uv run --offline --locked python -m pytest -q
```

**Resultado.** Ambas ejecuciones completaron las mismas 49 pruebas, con 49 aprobadas, 0 fallidas y 0 omitidas en cada una. La repetición comprueba que cambiar la zona de la máquina conserva los resultados de Mendoza.

## Punto de revisión

Las fechas de apertura, las disponibilidades individuales y los cupos del local siguen pendientes de datos reales. La semana sintética sirve para revisar el comportamiento del dominio. Las ventanas de patrón en F1 permiten desplazar juntos los bloques de una variante dentro de límites en minutos. La generación de candidatos y las decisiones de equidad pertenecen a las fases del optimizador.

El siguiente incremento previsto es B04, persistencia SQLite, tras la revisión de F1 por el solicitante. Reabrir un confirmado, revalidar borradores y ejecutar la interfaz en Windows corresponden a F2. La validación de esta entrega se hizo en Linux.

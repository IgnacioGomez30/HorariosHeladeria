# Instrucciones para Codex

Leé [README](README.md), [índice](docs/00_INDEX.md), [requisitos](docs/02_REQUIREMENTS.md), [ADR](docs/decisions/ADR.md) y los documentos normativos de la fase. Inspeccioná cambios locales antes de editar. El [primer encargo](docs/17_HANDOFF_CODEX.md) se limita a F1 del [plan](docs/13_IMPLEMENTATION_PLAN.md). El HTML y los JSON entregados son materiales de diseño.

## Invariantes

- Proyecto offline de horarios y francos para una sola instalación. Trabajá con datos sintéticos. Preservá las condiciones reales desconocidas como pendientes.
- Cada persona tiene ID estable y cada jornada tiene fecha operativa explícita. Los bloques se almacenan en minutos reales, son semiabiertos y pueden cruzar medianoche. Sumá toda la duración de la jornada en su fecha operativa. La jornada siguiente conserva su propia duración.
- Permití solapes entre personas; impedí el solape o intercalación incompatible de jornadas de la misma persona, aun entre días operativos. En jornada partida excluí pausas libres. Medí descansos entre jornadas y cobertura en tiempo real con ambos bordes del período.
- Franco fijo y rotativo adicional se acreditan en fechas distintas. Licencias, jornadas cortas, celdas vacías y propietarios sin asignar tienen significado propio. Un refuerzo eventual no cubre el mínimo. El historial de equidad usa únicamente el plan confirmado efectivo y correcciones con procedencia.
- Reglas obligatorias y capacidades para comprobarlas preceden a todo objetivo. Conservá manual y automático bajo la misma validación independiente. Si falta un dato imprescindible, permití editar y señalá qué impide confirmar ese período.
- Aislá dominio, casos de uso, infraestructura, interfaz, validación y solucionador. El worker recibe una instantánea por contrato; no lee SQLite, conoce nombres reales ni maneja la ventana. Un motor ausente deja disponible la ruta manual.
- La publicación requiere autorización explícita y transacción sobre la revisión vigente. Un resultado tardío o un conflicto conserva el original. Fuera del rango autorizado no se cambian asignaciones. Congelá pasado y bloques ya iniciados.

## Rutina de trabajo

1. Elegí un ticket con sus dependencias cumplidas; registrá cualquier contradicción reproducible por ID. No fijes como configuración del negocio las decisiones provisionales de la demo.
2. Introducí primero el ejemplo sintético y su resultado esperado cuando cambie una invariante. Validá los casos que tocan los dos extremos de semana, mes o año.
3. En F1 creá el entorno con el intérprete compatible seleccionado y documentá instalación reproducible. Una vez creado: en la raíz del repo y con el entorno activado, la suite se ejecuta con `python -m pytest -q`. Para F1, la ruta prevista de tests es `tests/unit/`. Este comando es la convención para el código futuro; esta edición contiene documentación.
4. Guardá el código y los tests en Git por incrementos. Mantené fuera del repo bases reales, copias, impresos, logs de personas y credenciales. Dependencias, formato de datos o cambios del contrato se justifican y prueban antes de promoverlos.
5. Al cerrar cada fase indicá archivos y comportamiento entregados, entorno, comandos y resultados efectivos, errores, pendientes y siguiente fase. Actualizá documentación y ADR si cambia la semántica. Informá por separado simulación local y verificación en Windows.

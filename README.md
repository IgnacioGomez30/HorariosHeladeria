# HorariosHeladeria

## Desarrollo de la fase 1

El dominio se encuentra en `src/heladeria/dominio/`. Los ejemplos y pruebas de aceptación usan personas ficticias y fechas explícitas de Mendoza. El [índice de la especificación](docs/00_INDEX.md) enlaza los requisitos y el [plan de pruebas](docs/12_TESTING_STRATEGY.md).

Desde la raíz del repositorio, con CPython 3.12.14 y uv 0.13.9 disponibles, instalar las versiones y artefactos fijados en `uv.lock`:

```sh
uv sync --locked
source .venv/bin/activate
python -m pytest -q
```

En PowerShell, la activación equivalente es `.venv\Scripts\Activate.ps1`. También se puede ejecutar la suite con `uv run --locked python -m pytest -q`. La primera instalación necesita acceso al índice de paquetes o una caché preparada. Una vez instalado, el dominio y las pruebas funcionan sin conexión. La única dependencia de ejecución es la base horaria IANA empaquetada en `tzdata`. Pytest y sus dependencias son de desarrollo.

La demostración de la semana, los resultados por requisito y el entorno verificado están en el [informe de F1](docs/20_RESULTADOS_F1.md).

## Persistencia local · B04

Desde Python, `abrir_base(raiz, modo)` abre un almacén y aplica las migraciones pendientes. La raíz es un directorio de datos del perfil local. Cada modo tiene su propio archivo (`demo/schedule.sqlite` o `real/schedule.sqlite`), identificador de conjunto y carpeta `respaldos/`. El modo se comprueba también dentro del archivo. Solo puede abrirse un escritor por conjunto.

Este ejemplo guarda una ficha sintética, cierra la conexión y la lee desde otra usando el mismo ID:

```python
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from heladeria.dominio.personas import Persona, Rol
from heladeria.infraestructura.base import Modo, abrir_base
from heladeria.infraestructura.repositorios import guardar_persona, persona_por_id

with TemporaryDirectory() as carpeta:
    raiz = Path(carpeta)
    persona = Persona("Demo Alba", Rol.EMPLEADO, date(2027, 2, 1))
    with abrir_base(raiz, Modo.DEMO) as conexion:
        revision = guardar_persona(conexion, persona)
    with abrir_base(raiz, Modo.DEMO) as conexion:
        assert persona_por_id(conexion, persona.id, revision) == persona
```

La versión 1 conserva personas, revisiones de configuración y reglas personales de cupos de franco y metas de minutos. La versión 2 incorpora casillas materializadas y sus bloques con minutos UTC, desfases locales y etiqueta de la persona al guardarlas. Una casilla guardada se consulta por su ID. La confirmación de un calendario corresponde a B06.

Al actualizar una base existente, el migrador toma la reserva de escritura y guarda una copia previa `.hhbackup` con `manifest.json` y `schedule.sqlite`. Comprueba la integridad de SQLite, las claves foráneas, la identidad del conjunto y el SHA-256 de la imagen empaquetada. Los cambios de esquema y su historial se confirman en una sola transacción. Si la migración falla, se puede reintentar desde el estado anterior y la copia verificada queda en el directorio de ese modo.

Desde la raíz, `uv run --locked python -m pytest -q` ejecuta F1 y B04 juntas. Las pruebas en `tests/integracion/` usan directorios temporales y reproducen una reapertura, una migración desde v1, errores de copia y de SQL y la terminación abrupta del proceso migrador.

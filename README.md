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

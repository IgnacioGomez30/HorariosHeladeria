# 11 · Intercambio de archivos y recuperación

Tres acciones de la pantalla de configuración tienen resultados diferentes. El responsable debe poder elegir a partir de lo que necesita recuperar o compartir.

| Acción | Archivo propuesto | Qué conserva | Qué se puede hacer después |
|---|---|---|---|
| Guardar o traer configuración | JSON UTF-8 versionado | Identidades y fichas, patrones, reglas, disponibilidades recurrentes, calendario, feriados, mínimos e ideales, política de equidad y vigencias | Previsualizar y aplicar una configuración |
| Hacer o restaurar copia de seguridad | `.hhbackup`, contenedor ZIP con dos miembros definidos | Base local consistente, incluidos históricos, borradores, solicitudes, restricciones, compromisos y metadatos de versión | Recuperar el estado completo de la fecha del respaldo |
| Exportar horario | PDF o PNG local | Vista autorizada de la revisión elegida, con período y fecha de confirmación | Imprimir o compartir el archivo por decisión del responsable |

## Configuración versionada

**Formato 1.0 propuesto.** Campos obligatorios: `format="heladeria-horarios.config"`, `formatVersion="1.0"`, `datasetId` de origen, `mode=REAL|DEMO`, `timeZone`, `people` e `items`. `people` declara IDs estables. Cada `item` declara `id` lógico, `versionId`, `kind`, `scopePersonId` si aplica, `fromDate`, `untilDateExclusive` (admite nulo) y `value` tipado. Transportar líneas de vigencia de la revisión de configuración elegida. Las referencias cruzadas usan IDs y vigencias; el orden de los elementos no cambia su significado. Documentar en la fase de persistencia el esquema mecanizado de cada familia de [configuración](05_DATA_MODEL.md), incluir fixture de cada tipo y rechazar familias desconocidas. Versionar independientemente de la base SQLite y del contrato del optimizador.

Ejemplo sintético de un archivo de demostración de **configuración incompleta**, admisible para configurar un conjunto vacío en modo demo. La falta de cobertura o reglas autorizadas seguirá visible.

```json
{
  "format": "heladeria-horarios.config",
  "formatVersion": "1.0",
  "datasetId": "d320b005-cdd8-418d-9aa8-58ed3fbd04ab",
  "mode": "DEMO",
  "timeZone": "America/Argentina/Mendoza",
  "people": [{"id":"9bbdfc87-7af1-448b-a4c9-63af04e21ca6"}],
  "items": [{
    "id":"7689cdeb-2d65-4e5f-ae25-ad9c97196837",
    "versionId":"ebb65f6d-f902-4f2b-a069-b4f36db425f2",
    "kind":"PERSON_PROFILE",
    "scopePersonId":"9bbdfc87-7af1-448b-a4c9-63af04e21ca6",
    "fromDate":"2027-02-01",
    "untilDateExclusive":null,
    "value":{"displayName":"Persona A","role":"EMPLOYEE","active":true}
  }]
}
```

No se exportan casillas, historial individual de arranque/equidad, borradores, fijaciones, solicitudes, ausencias concretas, apoyos pactados, notas privadas ni archivos ejecutables. El archivo sí contiene nombres y disponibilidad habitual: mostrar estas categorías en la vista previa. Mantener los datos de arranque observados en un ámbito no reemplazable por este formato. La base interna puede tener más metadatos que el JSON.

**Único modo de aplicación en V1:** instalación de la configuración visible y versionada a partir de una fecha explícita. Sin fusión automática campo por campo. En un conjunto real ya utilizado, aceptar una instantánea de su misma identidad de origen; en uno vacío, presentar su inicialización con los IDs importados. Copiar una configuración desde otro equipo con todo su historial requiere el respaldo completo. Un archivo de otro origen puede iniciar un conjunto vacío del mismo modo; no vincular personas entre orígenes por nombre. El piloto puede validar más adelante la necesidad de mapeo entre configuraciones independientes.

1. Leer como datos. Limitar tamaño y profundidad antes o durante el análisis, rechazar claves duplicadas, valores no finitos, fechas imposibles, versiones mayores incompatibles y contenido fuera del esquema. Los formatos anteriores solo se aceptan con un migrador documentado. No ejecutar SQL, scripts ni rutas llegados en el JSON. Establecer límites de tamaño/número documentados en el lector y ensayar el mayor respaldo del piloto.
2. Construir modelo temporal en memoria o base de ensayo. Validar tipos, IDs únicos, pertenencia de cada persona/patrón, vigencias, compatibilidad entre reglas y que cada plantilla relativa resuelva sus anclas en los días que aplican. Distinguir una contradicción de una configuración todavía incompleta. Mostrar qué funciones dependen de datos faltantes. Una configuración inconsistente nunca activa cambios parciales.
3. Previsualizar fecha efectiva, incorporaciones, modificaciones, perfiles omitidos y publicaciones futuras potencialmente afectadas. Una omisión prohíbe aplicar una baja implícita: exigir decisión explícita para desactivar desde la fecha elegida o cancelar. Explicar que las solicitudes/fijaciones existentes pueden quedar en conflicto. Requerir acción «Aplicar configuración».
4. Para cambios sobre datos existentes, conservar íntegro el pasado; la fecha de aplicación debe ser hoy o posterior y respetar los bloques ya iniciados. Recortar las versiones nuevas y previas a sus porciones efectivas en la **nueva** revisión, mantener anteriores para las publicaciones históricas. Los cambios de regla semanal a mitad de semana necesitan transición según [dominio](04_DOMAIN_MODEL.md). Mantener la validación por fecha y la distinción entre faltante operativo y formato inválido.
5. Si no hay diferencia efectiva, mostrar «La configuración ya coincide». Para aplicar, impedir escrituras desde la captura de estado, hacer copia previa verificada, comprobar de nuevo el token de vista previa bajo transacción y registrar versión de configuración + membresía + evento + incremento de época. Para reintentos reconocer el mismo contenido, fecha efectiva y revisión de partida. Si falló el respaldo o cambiaron los insumos, mantener el estado anterior y ofrecer reintentar o revisar diferencias. Conservar las publicaciones y señalar las futuras afectadas.

## Copia de seguridad coherente

Datos activos siempre en disco local del perfil del usuario. La copia puede guardarse en otro medio. Para una copia programada, propuesta inicial modificable: al primer uso de un día con cambios desde la última copia, más una copia previa a migración, importación y restauración. Mostrar fecha de la última copia verificada y acceso a «Guardar copia en otra ubicación». Para rotación inicial sugerida, conservar 7 copias diarias verificadas y la última copia anterior a cada operación pendiente de validar. Los respaldos manuales elegidos por el usuario quedan fuera de la purga automática. Revisar frecuencia/retención con el responsable; un disco común a la base y a la copia comparte el riesgo de falla. La aplicación no necesita un servicio residente para ejecutar esta política.

1. Usar la API de copia consistente de SQLite, p. ej. `sqlite3.Connection.backup`, desde origen a base de staging nueva y privada. Coordinar escrituras para identificar una revisión y evitar reinicios indefinidos. Cancelar limpiamente ante falta de espacio, permiso denegado o dispositivo retirado. No copiar en caliente el archivo activo desde el explorador. [SQLite · Online Backup API](https://www.sqlite.org/backup.html) · [Python · sqlite3](https://docs.python.org/3/library/sqlite3.html)
2. Cerrar la conexión de destino y verificar la copia en solo lectura: `integrity_check` devuelve una fila «ok» y `foreign_key_check` cero filas. Verificar ID de aplicación/esquema, versiones soportadas, cabeza, membresías y legibilidad de una revisión con sus bloques. Ejecutar ambas comprobaciones: la primera no cubre errores de FK. [SQLite · PRAGMA](https://www.sqlite.org/pragma.html)
3. Crear en temporal del destino un contenedor con **solo** `manifest.json` y `schedule.sqlite`. Manifiesto v1: identificador de formato, versión del respaldo, fecha UTC de creación, versión de aplicación, versión de esquema y conjunto, modo, última revisión confirmada (puede ser nula), tamaño en bytes y SHA-256 de la base cerrada. El hash detecta alteraciones respecto del manifiesto; un tercero que modifica ambos puede recalcularlo. El formato V1 no ofrece autenticación ni cifrado.
4. Reabrir el contenedor producido, verificar miembros y digest, finalizar/sincronizar archivo y publicar en el mismo volumen del destino. Si existe el nombre, permitir guardar otro o pedir autorización para reemplazar. Rotar copias antiguas solo después de verificar la nueva. Nunca purgar la única copia verificable. A falta de espacio mostrar cómo elegir otro destino y conservar todas las versiones válidas.

## Restauración recuperable

El responsable elige archivo → ve fecha, modo y última revisión → confirma «Restaurar esta copia». Informar que el calendario activo volverá a esa fecha y señalar dónde recuperar el estado actual. La vista previa es de solo lectura y nunca activa una base al abrir un archivo.

| Paso | Comprobación y acción | Qué queda tras fallo |
|---|---|---|
| Inspeccionar | Validar formato, versión y límites de bytes comprimidos y descomprimidos. Aceptar solo los dos nombres fijos en la raíz, sin duplicados ni enlaces; copiar el contenido como flujo a destinos creados por la app. Rechazar entradas inesperadas y no usar rutas del archivo. Verificar digest, modo y esquema. | Activa y respaldos sin cambios. El formulario señala formato, límite o prueba que falló. |
| Validar staging | En conexión privada de solo lectura, imponer límites y `trusted_schema=OFF` cuando proceda, extensiones deshabilitadas, ninguna función con efectos secundarios y catálogo de esquema coincidente con la versión que la app reconoce. Rechazar objetos imprevistos. Verificar integridad/FK, miembros de revisiones y reglas estructurales, sin exigir a un borrador ser factible. Si la base es antigua, migrar **solo staging** y verificarla de nuevo. | Se descarta staging. Se mantiene la base activa. [SQLite · recomendaciones para archivos no confiables](https://www.sqlite.org/security.html) |
| Preparar cambio | Tomar control exclusivo de la app, suspender autosave, cerrar vistas/conexiones, cancelar y esperar al proceso del motor. Comprobar espacio, capacidad de escritura y copia previa del estado actual. Dejar fuera de la base una marca local de operación con IDs de revisión y referencias a ambas copias verificadas. | El estado actual sigue disponible. Si un archivo está en uso, posponer sin intentar removerlo. |
| Aplicar en una base sana | Con las otras conexiones cerradas, usar staging como **origen** de la API de backup y base activa como **destino**. Esperar completitud sin error, cerrar y reabrir. La copia usa la transacción de destino de SQLite; no envolver esa conexión en otra transacción. No reemplazar archivos SQLite con conexiones o diarios abiertos. | Una operación abortada antes de completarse revierte su transacción; si hubo corte, permitir recuperación del journal al abrir. La marca impide admitir ediciones hasta identificar qué estado válido quedó. [SQLite · semántica de backup y rollback](https://www.sqlite.org/c3ref/backup_finish.html) · [SQLite · commit atómico](https://www.sqlite.org/atomiccommit.html) |
| Comprobar y reanudar | Revisar esquema, integridad/FK, dataset y cabeza esperados; comparar una huella **lógica** del estado restaurado con staging (filas/tablas relevantes en orden estable). No exigir igualdad byte a byte entre archivos producidos por la API. Nuevo identificador de sesión, invalidación de ejecuciones antiguas y presentación de la fecha recuperada. Registrar resultado y retirar la marca al terminar. | Si la base no se puede identificar como anterior o nueva válida, mantener modo recuperación; ofrecer cargar la copia previa verificada. Nunca inicializar una base vacía por un error de apertura. |

Si la base actual es ilegible, la restauración normal desde «Configuración» puede no ser posible. En el arranque de recuperación, preservar el conjunto dañado y sus diarios en una ubicación identificada, con todas las conexiones cerradas. Si se dispone de una base restaurada y verificada, abrirla como **nuevo conjunto local** con ruta distinta; el usuario confirma el cambio y la app guarda la nueva ruta con escritura recuperable. Un fallo de ese cambio conserva ambas ubicaciones y permite volver a elegir. No declarar «copia válida del estado previo» cuando solo se preservaron archivos dañados. En un equipo nuevo no hay estado previo que respaldar; instalar en ruta nueva a partir del mismo protocolo de validación. Probar reinicio en cada punto del circuito, también en Windows.

## Privacidad y salidas para el personal

La aplicación usa permisos heredados del perfil local. El operador elige ubicación de exportaciones; el archivo que lleva a USB conserva sensibilidad aunque el nombre sea genérico. Evitar nombres, notas, rutas personales y contenido de horarios en registros de errores. Los logs pueden contener un ID de acción, fase, código y versión para diagnóstico. La demostración usa directorios, respaldos y leyenda propios; no importar demostración en una base real.

Para la salida oficial, seleccionar **revisión confirmada y semana** antes de renderizar. Crear una proyección con lista permitida de campos: período, nombres/alias distinguibles, rol cuando ayude a distinguir, día, estado público (p. ej. «Ausente»), todos los bloques, etiqueta «+1 día» donde corresponda, referencia y fecha de confirmación. Dejar fuera motivos, notas privadas, reglas, preferencias, datos legales, de equidad y de generación. Una revisión recompuesta puede indicar procedencia por período cuando se combinan confirmaciones. V1 propone exportar confirmados; si se habilita más adelante un borrador, marca «BORRADOR» en todas las páginas/imágenes.

Generar PDF para papel con encabezado repetido, leyenda y paginación sin cortar las casillas partidas. En PNG priorizar legibilidad a escala de teléfono y vista previa; si resulta demasiado ancho, dividir por días en imágenes identificadas dentro del mismo período, con consentimiento del responsable y nombres de archivo previsibles. Usar la misma proyección, no capturar la pantalla (podría mostrar notas, controles o borradores). Comprobar texto largo, acentos, dos nombres iguales, escalado de pantalla, feriado y cierre al día siguiente con el responsable. El mensaje de éxito requiere escritura completada y ubicación definida. [Qt · QPdfWriter](https://doc.qt.io/qt-6/qpdfwriter.html) · [Qt · QImageWriter](https://doc.qt.io/qt-6/qimagewriter.html)

## Prueba de restauración que habilita el piloto

Generar dos publicaciones sintéticas distinguibles, una ficha desactivada, una jornada partida/nocturna, una excepción, un compromiso, una fijación y un borrador modificado. Respaldar, registrar objetos canónicos esperados, aplicar cambios posteriores y restaurar. Comparar las colecciones ordenadas, identidades, procedencias y cabeza con el momento de la copia. Reabrir la aplicación y comprobar que exporta la semana restaurada y que la copia previa recupera los cambios posteriores. Repetir con disco lleno, archivo truncado, FK huérfana, versión futura, corte durante activación, token anterior y carpeta de destino sin permisos. El procedimiento define evidencias exigibles; el ensayo de la aplicación y de su instalador se realiza en sus fases de implementación.

[Índice](00_INDEX.md) · [Datos](05_DATA_MODEL.md) · [UX/UI](10_UX_UI.md) · [Pruebas](12_TESTING_STRATEGY.md)
